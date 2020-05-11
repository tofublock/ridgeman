#! /usr/bin/python

import os
import gdal
import numpy as np
import matplotlib.pyplot as plt
import elevation
import math

ANGLE = math.pi/4
SUBSAMPLE = 10
SCALE = 100
LINEWIDTH = 1
STRETCH = 1

elevation.clip(bounds=(9.780159,43,9.866812,43.077846),output="out.tif",margin="5%",cache_dir=".")
elevation.clean(cache_dir=".")

filename = "SRTM1/out.tif"

ds = gdal.Open(filename)
band = ds.GetRasterBand(1)

print("Reading band into array")
rasterArray = band.ReadAsArray()

print("Masking NoData entries: ", band.GetNoDataValue())
rasterArray = np.ma.masked_values(rasterArray, band.GetNoDataValue())

print("Normalising array")
fullscale = rasterArray.max() - rasterArray.min()
rasterArray = rasterArray / fullscale
rasterSize = abs(ds.GetGeoTransform()[1])

#output = np.full((int(rasterArray.shape[1]*STRETCH),rasterArray.shape[0]), 1)

## missing scaling to rastersize in z
##output = np.full((int(rasterArray.shape[0]*math.sin(ANGLE)+fullscale*rasterSize*math.cos(ANGLE))+LINEWIDTH-1,rasterArray.shape[1]), 1)
output = np.full((int(rasterArray.shape[0]*STRETCH)+LINEWIDTH-1, rasterArray.shape[1]), 1)

print("Processing image")
for y in range(0,rasterArray.shape[0],int(SUBSAMPLE)):
	for x in range(0,rasterArray.shape[1]):
		if rasterArray[y,x]:
				## missing scaling to rastersize in z
				##newy = int( fullscale*math.cos(ANGLE) + y*math.sin(ANGLE) - rasterArray[y,x]*fullscale*rasterSize*math.cos(ANGLE) )
				newy = int( (y*STRETCH) - (rasterArray[y,x]*SCALE) )
				try:
					for i in range(0,LINEWIDTH):
						if (newy-LINEWIDTH/2)+i < rasterArray.shape[1]*math.cos(ANGLE):
							output[newy-int(LINEWIDTH/2)+i,x] = 0
					output[newy-int(LINEWIDTH/2)-1,x] = .5
					output[newy+int(LINEWIDTH/2)+1:,x] = 1
				except:
					print("y", y, "x", x, "newy", newy)



print("Plotting")
#fig, (ax1, ax2) = plt.subplots(1, 2)
#ax1.imshow(rasterArray)
#ax2.imshow(output, cmap=plt.cm.bone)
plt.imshow(output, cmap=plt.cm.bone)
plt.show()

