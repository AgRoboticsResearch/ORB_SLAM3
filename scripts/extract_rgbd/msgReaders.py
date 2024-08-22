import rosbag
import numpy as np
import time
import math
import os
import rospy
from std_msgs.msg import Int32, String
from sensor_msgs.msg import NavSatFix
from nav_msgs.msg import Odometry
from scipy.spatial import KDTree

def print_bag_topics(bag):
    topics = bag.get_type_and_topic_info()[1].keys()
    print("Topics: ", topics)

def camera_info_msg(bag, topic):
    """read camera info msg from bag"""
    # only read the first one published
    # return camera info in  dictonary, follow this ros cam_info msg definition, http://docs.ros.org/melodic/api/sensor_msgs/html/msg/CameraInfo.html
    print("Topics: ", topic)

    for topic, msg, t in bag.read_messages(topics=topic):
        camera_info =  {
                          "height": msg.height,
                          "width": msg.width,
                          "distortion_model": msg.distortion_model,
                          "D": msg.D,
                          "K": msg.K,
                          "R": msg.R,
                          "P": msg.P
                        }

        break

    return camera_info

def general_msg_reader(bag, topic):
    """read any msg into [n*[t, msg]] list"""
    print("Topics: ", topic)
    msgs = []
    for topic, msg, t in bag.read_messages(topics=topic):
        msgs.append([t, msg])
    return msgs

def imu_msg(bag):
    """ read imu ypr msg from bag"""
    imu_yprs, imu_gyroscope, imu_accelerometer = [], [], []
    timestamps = []
    for topic, msg, t in bag.read_messages(topics='/imu/ypr'):
        imu_yprs.append([msg.x, msg.y, msg.z]) 
    
    for topic, msg, t in bag.read_messages(topics='/imu/imu'):
        imu_gyroscope.append([msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z])
        imu_accelerometer.append([msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]) 
        timestamp = msg.header.stamp.secs + float(msg.header.stamp.nsecs) * 1e-9 # this is the true time, it is different from bag t.to_time()

        timestamps.append(timestamp)

    # convert to numpy
    imu_yprs = np.asarray(imu_yprs)
    imu_gyroscope = np.asarray(imu_gyroscope)
    imu_accelerometer = np.asarray(imu_accelerometer)
    timestamps =  np.asarray(timestamps)
    
    print("imu_yprs", imu_yprs.shape)
    print("imu_gyroscope", imu_gyroscope.shape)
    print("imu_accelerometer", imu_accelerometer.shape)
    print("timestamps", timestamps.shape)

    return imu_yprs, imu_gyroscope, imu_accelerometer, timestamps


# Image extraction not working on python 3
try:
    import cv2
    from cv_bridge import CvBridge, CvBridgeError

except ImportError:
    print("[WARNING] cv_bridge not working, image_msg reader is not imported, \
            make sure you are using python 2, installed ros and has ros python path in your python path")    
else:
    def image_msg(bag, topic, save_dir):
        """ read and save image msg """

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        print('Save directory: ', save_dir)
        print("Topics: ", topic)    
        bridge = CvBridge()
        for topic, msg, t in bag.read_messages(topics=topic):
            try:
                cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
            except CvBridgeError as e:
                print(e)
            timestamp = msg.header.stamp.secs + float(msg.header.stamp.nsecs) * 1e-9 # this is the true time, it is different from bag t.to_time()
            filename = save_dir + '/' + "%.9f"%timestamp + ".png"
            print("filename: ", filename)
            cv2.imwrite(filename, cv_image)


    def read_nth_msg(n_idx, bag, topic, timelist):
        msg_time = timelist[n_idx]
        retrived_msg = None
        for topic, msg, t in bag.read_messages(topics=topic, start_time=msg_time):
            retrived_msg = msg
            break
        return retrived_msg

    def create_timelist(bag, topic):
        time_list = []
        row_time_list = []
        i = 0
        for topic, msg, t in bag.read_messages(topics=topic):
            time_list.append([t.to_sec(), i])
            row_time_list.append(t)
            i += 1
        print("%s: %i " %(topic, len(time_list)))
        time_list = np.asarray(time_list)
        return time_list, row_time_list

    def retrive_image(n_idx, bag, timelist_ros_synced, topic, desired_encoding="passthrough", compressed=False):
        # Change the encoding to desired encoding if the passthrough not working well.
        # Encoding: http://wiki.ros.org/cv_bridge/Tutorials/ConvertingBetweenROSImagesAndOpenCVImagesPython
        # read the nth msg
        img_msg = read_nth_msg(n_idx, bag, topic, timelist_ros_synced)
        # msg to image
        bridge = CvBridge()
        if compressed:
            img = bridge.compressed_imgmsg_to_cv2(img_msg)
        else:
            img = bridge.imgmsg_to_cv2(img_msg, desired_encoding=desired_encoding)
        return img

    # get synchronized multiple msgs
    def sync_msgs(msgs, dt_threshold=None):
        # sync multiple msgs in msgs list []
        # msg should be a numpy array of size (N, data), timestamps should be the first dimension of the msgs
        # synchronization will based on the first msg in the list
        print("msgs to sync: ", len(msgs))
        
        if dt_threshold is None:
            # if dt is not set, dt will be the average period of the first msg
            msg_t = msgs[0][:, 0]
            dt_threshold = (msg_t[-1] - msg_t[1])/ len(msg_t)

        print("dt threshold: ", dt_threshold)

        msg1_t = msgs[0][:, 0]

        # timestamp kd of the rest msgs
        timestamps_kd_list = []
        for msg in msgs[1:]:
            timestamps_kd = KDTree(np.asarray(msg[:, 0]).reshape(-1, 1))
            timestamps_kd_list.append(timestamps_kd)


        msgs_idx_synced = []
        for msg1_idx in range(len(msg1_t)):
            msg_idx_list = [msg1_idx]
            dt_valid = True
            for timestamps_kd in timestamps_kd_list:
                dt, msg_idx = timestamps_kd.query([msg1_t[msg1_idx]])
                if abs(dt) > dt_threshold:
                    dt_valid = False
                    break
                msg_idx_list.append(msg_idx)

            if dt_valid:
                msgs_idx_synced.append(msg_idx_list)

        msgs_idx_synced = np.asarray(msgs_idx_synced).T
        print("msgs_idx_synced: ", msgs_idx_synced.shape)
        
        msgs_synced = []
        for i, msg in enumerate(msgs):
            msg_synced = msg[msgs_idx_synced[i]]
            msgs_synced.append(msg_synced)
            
        return msgs_synced