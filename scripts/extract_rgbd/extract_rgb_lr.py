import rosbag
import numpy as np
import msgReaders
import cv2
import os
print("Reading bag file")
bag_path = "/codes/data/rgbd/strawberry_oak/oak_2024-08-13-09-09-41.bag"
save_folder = "/codes/data/rgbd/strawberry_oak/oak_imgs/" + bag_path.split("/")[-1].split(".")[0] + "/"

print("Save folder: ", save_folder)

bag = rosbag.Bag(bag_path)
msgReaders.print_bag_topics(bag)


rgb_right_topic = "/oak/right/image_raw"
rgb_right_timelist, rgb_right_timelist_ros = msgReaders.create_timelist(bag, rgb_right_topic)
rgb_right_cam_info = msgReaders.camera_info_msg(bag, "/oak/right/camera_info")
proj_mat_depth = np.asarray(rgb_right_cam_info['P']).reshape([3, 4])


rgb_left_topic = "/oak/left/image_raw"
rgb_left_timelist, rgb_left_timelist_ros = msgReaders.create_timelist(bag, rgb_left_topic)
rgb_left_cam_info = msgReaders.camera_info_msg(bag, "/oak/left/camera_info")
proj_mat_rgb = np.asarray(rgb_left_cam_info['P']).reshape([3, 4])


depth_topic = "/oak/stereo/image_raw"
depth_timelist, depth_timelist_ros = msgReaders.create_timelist(bag, depth_topic)
depth_cam_info = msgReaders.camera_info_msg(bag, "/oak/stereo/camera_info")
proj_mat_depth = np.asarray(depth_cam_info['P']).reshape([3, 4])


# Sync timelist
# rgb_left_timelist_synced, rgb_right_timelist_synced = msgReaders.sync_msgs([rgb_left_timelist, rgb_right_timelist])
# rgb_right_timelist_ros_synced = [rgb_right_timelist_ros[i] for i in (rgb_right_timelist_synced[:, 1].astype(dtype=int))]
# rgb_left_timelist_ros_synced = [rgb_left_timelist_ros[i] for i in (rgb_left_timelist_synced[:, 1].astype(dtype=int))]

rgb_left_timelist_synced, rgb_right_timelist_synced, depth_timelist_synced = msgReaders.sync_msgs([rgb_left_timelist, rgb_right_timelist, depth_timelist])
rgb_right_timelist_ros_synced = [rgb_right_timelist_ros[i] for i in (rgb_right_timelist_synced[:, 1].astype(dtype=int))]
rgb_left_timelist_ros_synced = [rgb_left_timelist_ros[i] for i in (rgb_left_timelist_synced[:, 1].astype(dtype=int))]
depth_timelist_ros_synced = [depth_timelist_ros[i] for i in (depth_timelist_synced[:, 1].astype(dtype=int))]

print("rgb_right_timelist_ros_synced: ", len(rgb_right_timelist_ros_synced))
print("rgb_left_timelist_ros_synced: ", len(rgb_left_timelist_ros_synced))
print("depth_timelist_ros_synced: ", len(depth_timelist_ros_synced))
# check if save folder exsit and create if not
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

for idx in range(len(rgb_right_timelist_ros_synced)):
    rgb_right_image = msgReaders.retrive_image(idx, bag, rgb_right_timelist_ros_synced, rgb_right_topic)
    # rgb_right_image = cv2.cvtColor(rgb_right_image, cv2.COLOR_BGR2RGB)

    rgb_left_image = msgReaders.retrive_image(idx, bag, rgb_left_timelist_ros_synced, rgb_left_topic)
    # rgb_left_image = cv2.cvtColor(rgb_left_image, cv2.COLOR_BGR2RGB)

    depth_image = msgReaders.retrive_image(idx, bag, depth_timelist_ros_synced, depth_topic)


    # save 
    cv2.imwrite(save_folder + "rgb_right_%05i.png" % idx, rgb_right_image)
    cv2.imwrite(save_folder + "rgb_left_%05i.png" % idx, rgb_left_image)
    cv2.imwrite(save_folder + "depth_%05i.png" % idx, depth_image)

    # break
