include <include/stereocameraview.scad>

resolution=[2448,2048]; //image resolution
pixelPitch=0.00000345; //m
focalLength=0.008; //m
range=3; //m
baseline=0.3; //m
overlap_only=false;

rotate(a=[-90,0,0])
stereoCameraView(resolution,pixelPitch,focalLength,range,overlap_only);