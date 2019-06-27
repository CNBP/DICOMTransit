#!/usr/bin/env python

# Script adopted from: https://simpleitk.readthedocs.io/en/master/Examples/N4BiasFieldCorrection/Documentation.html
# ;

from __future__ import print_function

import SimpleITK as sitk
import sys
import os


# When input has no argument, provide help. Exit.
if len(sys.argv) < 2:
    print(
        "Usage: N4BiasFieldCorrection: \n"
        "inputImage: Argument 1, the input image"
        "outputImage: Argument 2, the output image"
        "[shrinkFactor]: Argument 3,  shrink or enlarge the image. "
        "[maskImage]: Argument 4, "
        "[numberOfIterations]: Argument 5, "
        "[numberOfFittingLevels]: argument 6"
    )
    sys.exit(1)

# FIRST argument (first argv is the command) is the input image.
inputImage = sitk.ReadImage(sys.argv[1])

# If mask image is indicated, read mask image. Otherwise, use default mask.
if len(sys.argv) > 4:
    maskImage = sitk.ReadImage(sys.argv[4], sitk.sitkUint8)
else:
    maskImage = sitk.OtsuThreshold(inputImage, 0, 1, 200)

# If shrink factor is indicated, shrink the images to the matching size.
if len(sys.argv) > 3:
    inputImage = sitk.Shrink(inputImage, [int(sys.argv[3])] * inputImage.GetDimension())
    maskImage = sitk.Shrink(maskImage, [int(sys.argv[3])] * inputImage.GetDimension())

# Case inptu image into a particular F32 format.
inputImage = sitk.Cast(inputImage, sitk.sitkFloat32)

# Inovke the corrector.
corrector = sitk.N4BiasFieldCorrectionImageFilter()

# Default fitting level.
numberFittingLevels = 4

# If more fitting level specified.
if len(sys.argv) > 6:
    numberFittingLevels = int(sys.argv[6])

# If a manual interation is specified.
if len(sys.argv) > 5:
    corrector.SetMaximumNumberOfIterations([int(sys.argv[5])] * numberFittingLevels)

# Execute the N4 correction using input image based on the mask image using the iteration set.
output = corrector.Execute(inputImage, maskImage)

# Write the image out to the path specified.
sitk.WriteImage(output, sys.argv[2])

# Whether or not visualize the image.
# if not "SITK_NOSHOW" in os.environ:
#    sitk.Show(output, "N4 Corrected")
