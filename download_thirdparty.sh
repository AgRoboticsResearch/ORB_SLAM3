#!/bin/bash
cd Thirdparty

echo "Downloading Pangolin..."
if [ ! -d "Pangolin" ]; then
    git clone https://github.com/stevenlovegrove/Pangolin.git
else
    echo "Pangolin already exists."
fi

echo "Downloading OpenCV 4.4.0..."
if [ ! -d "opencv" ]; then
    wget -O opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip
    unzip opencv.zip
    mv opencv-4.4.0 opencv
    rm opencv.zip
else
    echo "opencv already exists."
fi
