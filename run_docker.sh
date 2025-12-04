#! /bin/bash
xhost + 
docker container run -it --rm  --privileged --net=host --gpus device=0 \
    --env="NVIDIA_DRIVER_CAPABILITIES=all" \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,video \
    -e __NV_PRIME_RENDER_OFFLOAD=1 \
    -e __GLX_VENDOR_LIBRARY_NAME=nvidia \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="/home/${USER}/codes":"/codes":rw  \
    --volume=/dev:/dev \
    -w /codes \
    orb_slam3:v1 \
    bash
