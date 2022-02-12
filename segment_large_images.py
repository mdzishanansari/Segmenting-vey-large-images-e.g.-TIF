# -*- coding: utf-8 -*-
"""Segment Large Images.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mW5lzHIOO1EbjIcXoH-XSZ6PFQyvW56L
"""

!pip install patchify



import tensorflow as tf
from tensorflow import keras

import cv2
import numpy as np
from tensorflow.keras.utils import normalize
from PIL import Image
from matplotlib import pyplot as plt
from skimage import measure, color, io
from patchify import patchify, unpatchify

model = keras.models.load_model('/content/drive/MyDrive/Local')

model.load_weights('/content/drive/MyDrive/Local')

model.summary()

large_image = cv2.imread('/content/drive/MyDrive/Dataset/Mitochondria/training.tif', 0)

patches = patchify(large_image, (256, 256), step = 256)

predicted_patches = []
for i in range(patches.shape[0]):
  for j in range(patches.shape[1]):
    print(i, j)

    single_patch = patches[i, j, :, :]
    single_patch_norm = np.expand_dims(normalize(np.array(single_patch), axis=1), 2)
    single_patch_input = np.expand_dims(single_patch_norm, 0)


#Predict and threshold for values above 0.5 probability

    single_patch_prediction = (model.predict(single_patch_input)[0, :, :, 0] > 0.5).astype(np.uint8)
    predicted_patches.append(single_patch_prediction)

predicted_patches = np.array(predicted_patches)

predicted_patches_reshaped = np.reshape(predicted_patches, (patches.shape[0], patches.shape[1], 256, 256))
reconstructed_image = unpatchify(predicted_patches_reshaped, large_image.shape)
plt.imshow(reconstructed_image, cmap = 'gray')

plt.hist(reconstructed_image.flatten())

plt.figure(figsize=(8, 8))
plt.subplot(221)
plt.title('Large Image')
plt.imshow(large_image, cmap='gray')
plt.subplot(222)
plt.title('Prediction of large Image')
plt.imshow(reconstructed_image, cmap='gray')
plt.show()

from skimage import measure, color, io

#Watershed
img = cv2.imread('/content/drive/MyDrive/Dataset/Mitochondria/testing.tif')  #Read as color (3 channels)
img_grey = img[:,:,0]

kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(img_grey,cv2.MORPH_OPEN,kernel, iterations = 2)

sure_bg = cv2.dilate(opening,kernel,iterations=10)
dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)

ret2, sure_fg = cv2.threshold(dist_transform, 0.5*dist_transform.max(),255,0)

sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

ret3, markers = cv2.connectedComponents(sure_fg)
markers = markers+10

markers[unknown==255] = 0

markers = cv2.watershed(img, markers)
img[markers == -1] = [0,255,255]

img2 = color.label2rgb(markers, bg_label=0)

cv2_imshow(large_image)
cv2_imshow( img2)
cv2.waitKey(0)

props = measure.regionprops_table(markers, intensity_image=img_grey, 
                              properties=['label',
                                          'area', 'equivalent_diameter',
                                          'mean_intensity', 'solidity'])

import pandas as pd
df = pd.DataFrame(props)
df = df[df.mean_intensity > 100]  #Remove background or other regions that may be counted as objects
   
print(df.head())



from google.colab.patches import cv2_imshow



from google.colab import drive
drive.mount('/content/drive')