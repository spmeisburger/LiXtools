#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 12:53:58 2018

Test out fabio

@author: steve
"""

import fabio
import os
from matplotlib import pyplot
from numpy import median
import numpy.ma as ma

waxs_extension = '_WAXS1.cbf'
header_extension = '_SAXS.txt'
roi = [330,370,180,330]

def convert(filepath,all = False):
    if all:
        fn = getfilenames(filepath)
    else:
        fn = getnewfilenames(filepath)
    
    print('converting %d %s files in directory %s' % (len(fn),waxs_extension,filepath))
    print('writing mean value in ROI [%d:%d,%d:%d] to %s header file' % (roi[0],roi[1],roi[2],roi[3],header_extension))
    
    j = 0
    for x in fn:
        j = j + 1
        print('%d of %d' % (j,len(fn)))
        roimean(x,saveheader=True)
        
    if fn:
        print('done!')
    else:
        print('(no files to convert)')

def getnewfilenames(filepath):
    ''' list waxs2 files that don't have corresponding saxs.txt files '''
    fl = []
    filenames = getfilenames(filepath)
    for x in filenames:
        if not(os.path.isfile(file2headername(x))):
            fl.append(x)
    return fl

def getfilenames(filepath):
    
    fl =[]
    for x in os.listdir(filepath):
        if waxs_extension in x:
            fl.append(filepath + '/' + x)
    return fl

def file2headername(filename):
    headerfilename = filename.split(waxs_extension)[-2] + header_extension
    return headerfilename


def roimean(filename,saveheader=False,showim=False):
    
    im = fabio.open(filename);
    print('  loaded image %s' % filename)
    # this is the part of the WAXS2 image that contains the water ring.
    imROI = im.data[roi[0]:roi[1],roi[2]:roi[3]];
    imROImasked = ma.masked_less(imROI,0);
    # mean excluding points equal to -2
    meanROI = imROImasked.compressed().mean();
    #meanROI = imROI.mean();
    print('  ROI = [%d,%d,%d,%d]' % (roi[0],roi[1],roi[2],roi[3]))
    print('  excluded %d bad pixels' % imROImasked.mask.sum())
    print('  ROI mean = %f' % meanROI)
    
    if showim:
        maxintensity = 2*median(im.data)
        pyplot.subplot(1,2,1)
        pyplot.imshow(im.data,vmin=0,vmax=maxintensity)
        pyplot.gca().add_patch(pyplot.Rectangle((roi[2], roi[0]),
                              roi[3] - roi[2],
                              roi[1] - roi[0], fill=False,
                              edgecolor='r', linewidth=3))
        pyplot.subplot(1,2,2)
        pyplot.imshow(imROI,vmin=0,vmax=maxintensity)
        pyplot.show()
    
    if saveheader:
        # write a header file in the BL19U2, SSRF file format
        # (this works with RAW version 1.5)
        headerfilename = file2headername(filename)
        f = open(headerfilename,'w');
        f.write('roimean: %f' % meanROI);
        f.close();
        print('  saved header file %s' % headerfilename)
        