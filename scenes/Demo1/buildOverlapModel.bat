openscad GenerateStereoView.scad -o StereoViewOverlap.stl ^
-D "resolution=[2448,2048]" ^
-D "pixelPitch=0.00000345" ^
-D "focalLength=0.008" ^
-D "range=3" ^
-D "baseline=0.3" ^
-D "overlap_only=true"