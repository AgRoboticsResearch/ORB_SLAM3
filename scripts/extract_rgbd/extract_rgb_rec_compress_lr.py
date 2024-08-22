import rosbag
import numpy as np
import msgReaders
import cv2
import os
print("Reading bag file")
bag_path = "/codes/data/rgbd/strawberry_oak/oak_rect_2024-08-16-15-27-22.bag"
save_folder = "/codes/data/rgbd/strawberry_oak/oak_imgs/" + bag_path.split("/")[-1].split(".")[0] + "/"

print("Save folder: ", save_folder)

bag = rosbag.Bag(bag_path)
msgReaders.print_bag_topics(bag)


rgb_right_topic = "/oak/right/image_rect_color/compressed"
rgb_right_timelist, rgb_right_timelist_ros = msgReaders.create_timelist(bag, rgb_right_topic)
rgb_right_cam_info = msgReaders.camera_info_msg(bag, "/oak/right/camera_info")
proj_mat_rgb_right = np.asarray(rgb_right_cam_info['P']).reshape([3, 4])


rgb_left_topic = "/oak/left/image_rect_color/compressed"
rgb_left_timelist, rgb_left_timelist_ros = msgReaders.create_timelist(bag, rgb_left_topic)
rgb_left_cam_info = msgReaders.camera_info_msg(bag, "/oak/left/camera_info")
proj_mat_rgb_left = np.asarray(rgb_left_cam_info['P']).reshape([3, 4])


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

rgb_right_timelist_synced = [rgb_right_timelist[i] for i in (rgb_right_timelist_synced[:, 1].astype(dtype=int))]
rgb_left_timelist_synced = [rgb_left_timelist[i] for i in (rgb_left_timelist_synced[:, 1].astype(dtype=int))]
depth_timelist_synced = [depth_timelist[i] for i in (depth_timelist_synced[:, 1].astype(dtype=int))]


print("rgb_right_timelist_ros_synced: ", len(rgb_right_timelist_ros_synced))
print("rgb_left_timelist_ros_synced: ", len(rgb_left_timelist_ros_synced))
print("depth_timelist_ros_synced: ", len(depth_timelist_ros_synced))
# check if save folder exsit and create if not
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# save camera info in txt
np.savetxt(save_folder + "camera_info_right.txt", proj_mat_rgb_right)
np.savetxt(save_folder + "camera_info_left.txt", proj_mat_rgb_left)


# open a file to save the timestamps
with open(save_folder + "times.txt", "w") as f:
    for idx in range(len(rgb_right_timelist_ros_synced)):
        f.write(str(rgb_right_timelist_synced[idx][0]) + "\n")

        rgb_right_image = msgReaders.retrive_image(idx, bag, rgb_right_timelist_ros_synced, rgb_right_topic, compressed=True)
        # rgb_right_image = cv2.cvtColor(rgb_right_image, cv2.COLOR_BGR2RGB)

        rgb_left_image = msgReaders.retrive_image(idx, bag, rgb_left_timelist_ros_synced, rgb_left_topic, compressed=True)
        # rgb_left_image = cv2.cvtColor(rgb_left_image, cv2.COLOR_BGR2RGB)

        depth_image = msgReaders.retrive_image(idx, bag, depth_timelist_ros_synced, depth_topic)


        # save 
        cv2.imwrite(save_folder + "rgb_right_%06i.png" % idx, rgb_right_image)
        cv2.imwrite(save_folder + "rgb_left_%06i.png" % idx, rgb_left_image)
        cv2.imwrite(save_folder + "depth_%06i.png" % idx, depth_image)

