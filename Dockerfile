FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --fix-missing \
    cmake \
    g++ \
    git \
    wget \
    unzip \
    libeigen3-dev \
    libboost-all-dev \
    libssl-dev \
    libglew-dev \
    libpython3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libepoxy-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Thirdparty directory
WORKDIR /ORB_SLAM3/Thirdparty

# Copy and build Pangolin
COPY Thirdparty/Pangolin /ORB_SLAM3/Thirdparty/Pangolin
RUN cd Pangolin && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Copy and build OpenCV 4.4.0
COPY Thirdparty/opencv /ORB_SLAM3/Thirdparty/opencv
RUN cd opencv && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DBUILD_TESTS=OFF \
    -DBUILD_PERF_TESTS=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_opencv_apps=OFF \
    && make -j$(nproc) && \
    make install

# Set working directory
WORKDIR /ORB_SLAM3

# Copy source code
COPY . /ORB_SLAM3

# Build ORB_SLAM3
RUN chmod +x build.sh && ./build.sh
