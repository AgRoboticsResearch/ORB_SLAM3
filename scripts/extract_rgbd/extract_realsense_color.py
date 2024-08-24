import rosbag
import numpy as np
import msgReaders
import cv2
import os
import argparse

def main(bag_path, save_folder, compressed):
    bag = rosbag.Bag(bag_path)
    msgReaders.print_bag_topics(bag)
    save_folder = (save_folder + "/" + os.path.basename(bag_path).replace(".bag", "") + "/").replace("//", "/")

    color_topic = "/camera/color/image_raw" + ("/compressed" if compressed else "")
    camera_info_topic = "/camera/color/camera_info"

    color_timelist, color_timelist_ros = msgReaders.create_timelist(bag, color_topic)
    color_cam_info = msgReaders.camera_info_msg(bag, camera_info_topic)
    proj_mat_cam = np.asarray(color_cam_info['P']).reshape([3, 4])

    print("color_timelist_ros: ", len(color_timelist_ros))
    # check if save folder exsit and create if not
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # save camera info in txt
    np.savetxt(save_folder + "camera_info_color.txt", proj_mat_cam)

    # open a file to save the timestamps
    with open(save_folder + "times.txt", "w") as f:
        for idx in range(len(color_timelist_ros)):
            f.write(str(color_timelist[idx][0]) + "\n")
            cam_image = msgReaders.retrive_image(idx, bag, color_timelist_ros, color_topic, compressed=True)
            cv2.imwrite(save_folder + "color_%06i.png" % idx, cam_image)

def parse_args():
    parser = argparse.ArgumentParser(description="Process your script's arguments")
    parser.add_argument("bag_path", help="Path to the bag file")
    parser.add_argument("save_folder", help="Path to the save folder")
    parser.add_argument("--compressed", action="store_true", help="Whether the image msgs are compressed")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"bag_path: {args.bag_path}")
    print(f"save_folder: {args.save_folder}")
    print(f"compressed: {args.compressed}")
    main(args.bag_path, args.save_folder, args.compressed)