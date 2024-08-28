import rosbag
import numpy as np
import msgReaders
import cv2
import os
import argparse

def main(bag_path, save_folder, compressed, depth):
    bag = rosbag.Bag(bag_path)
    msgReaders.print_bag_topics(bag)
    save_folder = save_folder + os.path.basename(bag_path).replace(".bag", "") + "/"



    prefix = "/camera"
    depth_cam_info_topic = prefix + "/aligned_depth_to_color/camera_info"
    depth_topic = "/aligned_depth_to_color/image_raw"
    right_cam_topic = prefix + "/infra2/image_rect_raw" + ("/compressed" if compressed else "")
    left_cam_topic = prefix + "/infra1/image_rect_raw" + ("/compressed" if compressed else "")
    right_camera_info_topic = prefix + "/infra2/camera_info"
    left_camera_info_topic = prefix + "/infra1/camera_info"
    color_cam_topic = "/camera/color/image_raw" + ("/compressed" if compressed else "")
    color_camera_info_topic = "/camera/color/camera_info"


    right_cam_timelist, right_cam_timelist_ros = msgReaders.create_timelist(bag, right_cam_topic)
    right_cam_cam_info = msgReaders.camera_info_msg(bag, right_camera_info_topic)
    proj_mat_right_cam = np.asarray(right_cam_cam_info['P']).reshape([3, 4])


    left_cam_timelist, left_cam_timelist_ros = msgReaders.create_timelist(bag, left_cam_topic)
    left_cam_cam_info = msgReaders.camera_info_msg(bag, left_camera_info_topic)
    proj_mat_left_cam = np.asarray(left_cam_cam_info['P']).reshape([3, 4])

    color_cam_timelist, color_cam_timelist_ros = msgReaders.create_timelist(bag, color_cam_topic)
    color_cam_cam_info = msgReaders.camera_info_msg(bag, color_camera_info_topic)
    proj_mat_color_cam = np.asarray(color_cam_cam_info['P']).reshape([3, 4])

    if depth:
        depth_timelist, depth_timelist_ros = msgReaders.create_timelist(bag, depth_topic)
        depth_cam_info = msgReaders.camera_info_msg(bag, depth_cam_info_topic)
        proj_mat_depth = np.asarray(depth_cam_info['P']).reshape([3, 4])


    # Sync timelist
    if depth:
        left_cam_timelist_synced, right_cam_timelist_synced, color_cam_timelist_synced, depth_timelist_synced = msgReaders.sync_msgs([left_cam_timelist, right_cam_timelist, color_cam_timelist, depth_timelist])
        right_cam_timelist_ros_synced = [right_cam_timelist_ros[i] for i in (right_cam_timelist_synced[:, 1].astype(dtype=int))]
        left_cam_timelist_ros_synced = [left_cam_timelist_ros[i] for i in (left_cam_timelist_synced[:, 1].astype(dtype=int))]
        color_cam_timelist_ros_synced = [color_cam_timelist_ros[i] for i in (color_cam_timelist_synced[:, 1].astype(dtype=int))]
        depth_timelist_ros_synced = [depth_timelist_ros[i] for i in (depth_timelist_synced[:, 1].astype(dtype=int))]

        right_cam_timelist_synced = [right_cam_timelist[i] for i in (right_cam_timelist_synced[:, 1].astype(dtype=int))]
        left_cam_timelist_synced = [left_cam_timelist[i] for i in (left_cam_timelist_synced[:, 1].astype(dtype=int))]
        color_cam_timelist_synced = [color_cam_timelist[i] for i in (color_cam_timelist_synced[:, 1].astype(dtype=int))]
        depth_timelist_synced = [depth_timelist[i] for i in (depth_timelist_synced[:, 1].astype(dtype=int))]
        print("depth_timelist_ros_synced: ", len(depth_timelist_ros_synced))

    else:
        left_cam_timelist_synced, right_cam_timelist_synced, color_cam_timelist_synced = msgReaders.sync_msgs([left_cam_timelist, right_cam_timelist, color_cam_timelist])
        right_cam_timelist_ros_synced = [right_cam_timelist_ros[i] for i in (right_cam_timelist_synced[:, 1].astype(dtype=int))]
        left_cam_timelist_ros_synced = [left_cam_timelist_ros[i] for i in (left_cam_timelist_synced[:, 1].astype(dtype=int))]
        color_cam_timelist_ros_synced = [color_cam_timelist_ros[i] for i in (color_cam_timelist_synced[:, 1].astype(dtype=int))]

        right_cam_timelist_synced = [right_cam_timelist[i] for i in (right_cam_timelist_synced[:, 1].astype(dtype=int))]
        left_cam_timelist_synced = [left_cam_timelist[i] for i in (left_cam_timelist_synced[:, 1].astype(dtype=int))]
        color_cam_timelist_synced = [color_cam_timelist[i] for i in (color_cam_timelist_synced[:, 1].astype(dtype=int))]

    print("right_cam_timelist_ros_synced: ", len(right_cam_timelist_ros_synced))
    print("left_cam_timelist_ros_synced: ", len(left_cam_timelist_ros_synced))
    print("color_cam_timelist_ros_synced: ", len(color_cam_timelist_ros_synced))

    # check if save folder exsit and create if not
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # save camera info in txt
    np.savetxt(save_folder + "camera_info_right.txt", proj_mat_right_cam)
    np.savetxt(save_folder + "camera_info_left.txt", proj_mat_left_cam)
    np.savetxt(save_folder + "camera_info_color.txt", proj_mat_color_cam)


    # open a file to save the timestamps
    with open(save_folder + "times.txt", "w") as f:
        for idx in range(len(left_cam_timelist_ros_synced)):
            f.write(str(left_cam_timelist_synced[idx][0]) + "\n")

            right_cam_image = msgReaders.retrive_image(idx, bag, right_cam_timelist_ros_synced, right_cam_topic, compressed=True)
            # right_cam_image = cv2.cvtColor(right_cam_image, cv2.COLOR_BGR2RGB)

            left_cam_image = msgReaders.retrive_image(idx, bag, left_cam_timelist_ros_synced, left_cam_topic, compressed=True)
            # left_cam_image = cv2.cvtColor(left_cam_image, cv2.COLOR_BGR2RGB)

            color_cam_image = msgReaders.retrive_image(idx, bag, color_cam_timelist_ros_synced, color_cam_topic, compressed=True)
            color_cam_image = cv2.cvtColor(color_cam_image, cv2.COLOR_BGR2RGB)

            # save 
            cv2.imwrite(save_folder + "right_%06i.png" % idx, right_cam_image)
            cv2.imwrite(save_folder + "left_%06i.png" % idx, left_cam_image)
            cv2.imwrite(save_folder + "color_%06i.png" % idx, color_cam_image)

            if depth:
                depth_image = msgReaders.retrive_image(idx, bag, depth_timelist_ros_synced, depth_topic)
                cv2.imwrite(save_folder + "depth_%06i.png" % idx, depth_image)

def parse_args():
    parser = argparse.ArgumentParser(description="Process your script's arguments")
    parser.add_argument("bag_path", help="Path to the bag file")
    parser.add_argument("save_folder", help="Path to the save folder")
    parser.add_argument("--compressed", action="store_true", help="Whether the image msgs are compressed")
    parser.add_argument("--depth", action="store_true", help="Whether to extract depth images")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"bag_path: {args.bag_path}")
    print(f"save_folder: {args.save_folder}")
    print(f"compressed: {args.compressed}")
    print(f"depth: {args.depth}")
    main(args.bag_path, args.save_folder, args.compressed, args.depth)