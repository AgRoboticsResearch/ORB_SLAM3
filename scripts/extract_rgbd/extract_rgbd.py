import rosbag
import numpy as np
import msgReaders
import cv2

print("Reading bag file")
bag_path = "/codes/data/rgbd/rgbd_2024-08-02-00-30-23.bag"
save_folder = "./rgbd/"

bag = rosbag.Bag(bag_path)
msgReaders.print_bag_topics(bag)


depth_topic = "/camera/aligned_depth_to_color/image_raw"
depth_timelist, depth_timelist_ros = msgReaders.create_timelist(bag, depth_topic)
depth_cam_info = msgReaders.camera_info_msg(bag, "/camera/aligned_depth_to_color/camera_info")
proj_mat_depth = np.asarray(depth_cam_info['P']).reshape([3, 4])


rgb_topic = "/camera/color/image_raw"
rgb_timelist, rgb_timelist_ros = msgReaders.create_timelist(bag, rgb_topic)
rgb_cam_info = msgReaders.camera_info_msg(bag, "/camera/color/camera_info")
proj_mat_rgb = np.asarray(rgb_cam_info['P']).reshape([3, 4])

# Sync timelist
rgb_timelist_synced, depth_timelist_synced = msgReaders.sync_msgs([rgb_timelist, depth_timelist])
depth_timelist_ros_synced = [depth_timelist_ros[i] for i in (depth_timelist_synced[:, 1].astype(dtype=int))]
rgb_timelist_ros_synced = [rgb_timelist_ros[i] for i in (rgb_timelist_synced[:, 1].astype(dtype=int))]

print("depth_timelist_ros_synced: ", len(depth_timelist_ros_synced))
print("rgb_timelist_ros_synced: ", len(rgb_timelist_ros_synced))

for idx in range(len(depth_timelist_ros_synced)):
    depth_image = msgReaders.retrive_image(idx, bag, depth_timelist_ros_synced, depth_topic)
    rgb_image = msgReaders.retrive_image(idx, bag, rgb_timelist_ros_synced, rgb_topic)
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    # save 
    cv2.imwrite(save_folder + "depth_%05i.png" % idx, depth_image)
    cv2.imwrite(save_folder + "rgb_%05i.png" % idx, rgb_image)

    # break
