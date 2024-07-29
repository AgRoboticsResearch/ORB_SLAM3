echo "Building ROS nodes"
export ROS_PACKAGE_PATH=${ROS_PACKAGE_PATH}:/codes/ORB_SLAM3_docker/Examples/ROS
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
cd Examples/ROS/ORB_SLAM3
rm -r build
mkdir build
cd build
cmake .. -DROS_BUILD_TYPE=Release
make -j4
