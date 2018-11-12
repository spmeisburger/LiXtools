#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 22:13:13 2018

@author: steve
"""

import h5py
import fabio
import os

# det_names dictionary copied from py4xs.local
det_names = {"_SAXS": "pil1M_image",
              "_WAXS1": "pilW1_image",
              "_WAXS2": "pilW2_image"}

def info(fn):
    fh5 = h5py.File(fn, "r+")
    samples = list(fh5.keys())
    print("%s contains %d sample(s):" % (fn,len(samples)))
    for sn in samples:
        print("  %s:" % sn)
        for ext in list(det_names.keys()):
            imshape = fh5["%s/primary/data/%s" % (sn, det_names[ext])].shape
            if len(imshape)>3:
                imshape = imshape[-3:]       # quirk of suitcase
            print("    %s: %d images" % (ext,imshape[0]))

def unpack(fn):

    fh5 = h5py.File(fn, "r+")

    samples = list(fh5.keys())
    print(samples)

    dirout = fn.split(".h5")[0] # use h5 file base name for output directory
    
    if not(os.path.exists(dirout)):
        os.mkdir(dirout)

    for sn in samples:
        images = {}
        for ext in list(det_names.keys()):
            #print("loading %s detector images from sample %s" % (ext,sn))
            try:
                ti = fh5["%s/primary/data/%s" % (sn, det_names[ext])].value
                if len(ti.shape)>3:
                    ti = ti.reshape(ti.shape[-3:])      # quirk of suitcase
                images[ext] = ti
                for n in range(images[ext].shape[0]): # loop over images
                    im = images[ext][n,:,:]
                
                    # make a new cbf image, no header
                    imcbf = fabio.cbfimage.CbfImage(data=im)
                
                    fncbf = "%s/%s_%05d%s.cbf" % (dirout, sn, n+1, ext)
                    print(fncbf)
                    imcbf.write(fncbf)
            except:
                print("WARNING: couldn't find image %s/primary/data/%s" % (sn, det_names[ext]))
            
            
            