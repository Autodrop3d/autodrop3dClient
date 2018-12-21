# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 17:57:51 2018

@author: ifrommer
#This is awsome code

WARNING: THIS IS QUICK AND DIRTY.
I DID A LITTLE TESTING BUT IT LIKELY NEEDS SOME WORK.
"""
import numpy as np


class CoordTransformer:
    #
    #                  A
    #
    #                  y
    #
    #
    #                  O      x
    #
    #
    #
    #      B                      C
    #

    # Use as follows!
    # import coordsTransform
    # inst = coordsTransform.CoordTransformer([[0,50,10],[-50,-50,-10],[50,-50,-10]])
    # print(inst.Transform([0,0,0]))
    # print(inst.Transform([0,-50,0]))
    # print(inst.Transform([0,0,50]))

    m2 = None
    newCenter = None

    def __init__(self, ptsList):

        # Convert pts list to np arrays
        npPtsList = self.PtsToNPs(ptsList)

        # Get new center
        self.newCenter = self.GetCenter(npPtsList[0],npPtsList[1],npPtsList[2])

        # Get new coordinate axes
        newCoordAxes = self.NewCoordAxes(npPtsList[0],npPtsList[1],npPtsList[2])

        self.m2 = np.array(newCoordAxes).T

    # Main function to call
    def Transform(self, coordsToTransform):

        # Convert object points to np arrays
        coordsToTransform = self.PtsToNPs(coordsToTransform)
        # Compute transformed coords
        newPt = self.newCenter + self.m2.dot(coordsToTransform)
        return newPt  

    # Compute new coordinate axes given 3 points on the plane
    # @ ptA, ptB, and ptC are numpy arrays of coords for 3 points
    def NewCoordAxes(self, ptA, ptB, ptC):
        ptO = self.newCenter
        vectOA = ptA - ptO      
        vectOy = vectOA / np.linalg.norm(vectOA)    
        vectBC = ptC - ptB     
        vectOx = vectBC / np.linalg.norm(vectBC)    
        vectOz = np.cross(vectOx,vectOy)    

        # Return the new coordinate axis vectors
        return (vectOx, vectOy, vectOz)

    # Convert list of points to np array
    def PtsToNPs(self, pt):
        return np.array(pt)

    # Get the new origin - very simplistic, may want to replace
    def GetCenter(self, npA, npB, npC):
        midBC = (npB+npC)/2
        center = (npA+midBC)/2
        return center
    
