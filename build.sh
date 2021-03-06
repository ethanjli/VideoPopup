#!/bin/bash

#compile libs

CWD=$(pwd)

#broxMalik tracks
cd ./libs/BroxMalik/trackingLinux64
make
cd $CWD

#read and write tracks
cd ./libs/read_write_tracks/python_tracks
make
cd $CWD

#build neighborhood structure
cd ./libs/nhood/python_neighbors
make
cd $CWD

#graph cut segmentation
cd ./libs/segmentation_rui_new
make
cd $CWD

#ceres solver optimization for orthographic bundle adjustment
cd ./libs/ceres-solver-mex_new
make
cd $CWD

#OpenSfM for perspective reconstruction
cd ./libs/mapillary/OpenSfM
python setup.py build
cd $CWD
