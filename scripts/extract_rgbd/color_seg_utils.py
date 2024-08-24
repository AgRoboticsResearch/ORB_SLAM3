# -----------------------------------------------------
#  These tools are useful to do colorbased segmentation
# -----------------------------------------------------

import numpy as np
import math
import cv2 as cv
from sklearn import linear_model
from mpl_toolkits.mplot3d import Axes3D

def segment(img, roi_rgbhsv_mean, roi_rgbhsv_std, threshold, var_weighting=False):
    image_hsv = cv.cvtColor(img, cv.COLOR_RGB2HSV)
    image_rgbhsv = np.concatenate((img, image_hsv), axis=2)
    image_rgbhsv.shape
    if var_weighting:
        distance_map = np.sum(np.abs((image_rgbhsv - roi_rgbhsv_mean) / roi_rgbhsv_std**2), axis=2)        
    else:
        distance_map = np.sum(np.abs((image_rgbhsv - roi_rgbhsv_mean) / roi_rgbhsv_std), axis=2)
    segmentation = distance_map<threshold
    return segmentation, distance_map

def get_center_std(roi):
    roi_hsv = cv.cvtColor(roi, cv.COLOR_RGB2HSV)
    roi_rgbhsv = np.concatenate((roi, roi_hsv), axis=2)
    roi_flat = roi_rgbhsv.reshape([-1, roi_rgbhsv.shape[-1]])
    roi_mean = np.mean(roi_flat, axis=0)
    roi_std = np.std(roi_flat, axis=0)
    return roi_mean, roi_std

def ransac_line(segmentation_img, ransac_threshold=20):
    uv_inliers = np.where(segmentation_img)

    # fit a line
    x = uv_inliers[0].reshape(-1, 1)
    y = uv_inliers[1]

    ransac = linear_model.RANSACRegressor(residual_threshold=ransac_threshold)
    ransac.fit(x, y)
    inlier_mask = ransac.inlier_mask_
    print("Inliers: ", len(inlier_mask))
    inlier_x = x[inlier_mask]
    inlier_y = y[inlier_mask]    
    min_x = min(inlier_x)
    max_x = max(inlier_x)
    xrange = [min_x, max_x]

    lr = linear_model.LinearRegression()
    lr.fit(inlier_x, inlier_y)

    b0 = lr.intercept_
    b1 = lr.coef_[0]
    return b0, b1, xrange, len(inlier_mask), 
