#! /usr/bin/python

import os
from osgeo import gdal
from pyproj import Transformer
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import drawSvg as draw
import sys


ANGLE = math.pi/4
SUBSAMPLE = 10
SCALE = 120
LINEWIDTH = 4
STRETCH = .4

# Bounding box for image
lat1, lon1 = 38.625287, -28.861890
lat2, lon2 = 38.569045, -28.557980

# Transform lat lon coordinates to Copernicus projection
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
x1,y1 = transformer.transform(lon1, lat1)
x2,y2 = transformer.transform(lon2, lat2)

# Open DEM data file, read elevation data into numpy array and mask NoDataValue entries
DEMfile = "eu_dem_v11_E10N20/eu_dem_v11_E10N20.TIF"
ds = gdal.Open(DEMfile)
gt = ds.GetGeoTransform()
band = ds.GetRasterBand(1)

# Calculate pixel values from coordinates
px1, py1 = int( (x1 - gt[0]) / gt[1] ), int( (y1 - gt[3]) / gt[5] )
px2, py2 = int( (x2 - gt[0]) / gt[1] ), int( (y2 - gt[3]) / gt[5] )

print("Reading band into array")
rasterArray = band.ReadAsArray(px1,py1,abs(px2-px1),abs(py2-py1), resample_alg=gdal.gdalconst.GRIORA_Cubic)

print("Masking NoData entries: ", band.GetNoDataValue())
rasterArray = np.ma.masked_values(rasterArray, band.GetNoDataValue())

fullscale = rasterArray.max() - rasterArray.min()
rasterArray = rasterArray / fullscale

d = draw.Drawing(rasterArray.shape[1], int(rasterArray.shape[0]*STRETCH)+LINEWIDTH-1, displayInline=False)

# Frontier for determining if pixels are blocked from view, frontier is all the way at the bottom of the screen at the start
frontier = np.full(rasterArray.shape[1], 0)

print("Processing image")

# Array of segments allows multiple paths per line
paths = []

# Go through image from bottom to top
for y in range(rasterArray.shape[0]-1,-1,int(SUBSAMPLE)*-1):
	# Array of coordinates make up a path
	segments = []
	# Initialise new line
	line = []
	for x in range(0,rasterArray.shape[1]):
		# Only look at points that are not masked
		if rasterArray[y,x]:

			# Calculate projection
			yProjectedVector = int( d.height - (y*STRETCH) + (rasterArray[y,x]*SCALE) )

			# If new coordinate lies frontier line ends here
			if frontier[x] > yProjectedVector:
				# Only add point if it is the endpoint of a line
				if len(line):
					line.append([frontier[x], x])
				segments.append(line)
				line = []
			# Pixel is visible, add it to the line
			else:
				frontier[x] = yProjectedVector
				line.append([yProjectedVector, x])

	# Only add non-empty lines to segments
	if len(line):
		segments.append(line)
		line = []
	# Only add non-empty segments to paths
	if len(segments):
		paths.append(segments)
		segments = []

# Step through all coordinates of all segments and draw paths
print("Plotting")
if len(paths):
	for p in paths:
		for s in p:
			path = draw.Path(stroke_width=LINEWIDTH, stroke='black', fill='none')
			for i, c in enumerate(s):
				if not i:
					path.M(c[1], c[0])
				else:
					path.l(c[1]-s[i-1][1], c[0]-s[i-1][0])
			d.append(path)

# Save as vector graphic
d.saveSvg('output.svg')

# Draw white background, insert as first element, rasterize and save as png
d.insert(0, draw.Rectangle(0,0,800,800, fill='white'))
d.setPixelScale(1)
r = d.rasterize()
r.savePng('output.png')
plt.imshow(mpimg.imread('output.png'))
plt.axis('off')
plt.show()
