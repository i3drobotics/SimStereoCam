import os, time
import cv2
from Stereo3D import Stereo3D, StereoCalibration
from Stereo3D.StereoCapture import *

LOAD_MODE_CHANGES_ONLY = 0
LOAD_MODE_ALL = 1

def getImagesToProcess(added):
    added_no_extension = [os.path.splitext(f)[0] for f in added]
    lr_image_list = []
    for i in range(0, len(added_no_extension), 2):
        f = added_no_extension[i]
        f_l = f[:-1] + "l"
        f_r = f[:-1] + "r"
        lr_image_list.append([f_l,f_r])
    return lr_image_list

def genCal(resolution,pixel_pitch,focal_length,baseline):
    stcal = StereoCalibration()
    stcal.get_cal_from_ideal(resolution, pixel_pitch, focal_length, baseline)
    return stcal

def processImages(image_folder,lr_image_list,stcal,stmatcher,showPreviewGUI=False):
    for f_lr in lr_image_list:
        f_l,f_r = f_lr
        f_d = f_l[:-1] + "d"
        f_p = f_l[:-1] + "points.ply"
        f_l = image_folder+f_l + ".png"
        f_r = image_folder+f_r + ".png"
        f_d = image_folder+f_d + ".png"
        stcap = StereoCapture("Image",[f_l,f_r])
        s3D = Stereo3D(stcap,stcal,stmatcher)
        connected = s3D.connect()
        if showPreviewGUI:
            while(True):
                exit_code = s3D.run_frame()
                if (exit_code == s3D.EXIT_CODE_QUIT):
                    break
        res,disp = s3D.grab3D(False)
        if (res):
            disp_scaled = s3D.scale_disparity(disp)
            disp_black_mask = disp_scaled <= 0
            # apply color map to disparity
            colormap=cv2.COLORMAP_JET
            disp_colormap = cv2.applyColorMap(disp_scaled, colormap)
            disp_colormap[disp_black_mask != 0] = [0, 0, 0]
            cv2.imwrite(f_d,disp_colormap)
            print("Saved disparty to: "+f_d)
            s3D.save_point_cloud(disp,s3D.rect_image_left,image_folder,f_p,False)
        else:
            print("Failed to generate 3D")

def gen3d(resolution,pixel_pitch,focal_length,baseline,load_mode,stmatcher,showPreviewGUI=False):
    # initalise calibration for generating 3d from camera parameters
    stcal = genCal(resolution,pixel_pitch,focal_length,baseline)

    if (load_mode == LOAD_MODE_CHANGES_ONLY):
        # check for new files in folder
        
        before = dict ([(f, None) for f in os.listdir (folder)])
        added = []
        while True:
            time.sleep (1)
            after = dict ([(f, None) for f in os.listdir (folder)])
            added = [f for f in after if not f in before]
            if added: 
                print("Added: ", ", ".join (added))
                lr_image_list = getImagesToProcess(added)
                processImages(folder+"/",lr_image_list,stcal,stmatcher,showPreviewGUI)
            before = after
    elif (load_mode == LOAD_MODE_ALL):
        files = dict ([(f, None) for f in os.listdir (folder)])
        added = [f for f in files if (os.path.splitext(f)[1]==".png")]
        lr_image_list = getImagesToProcess(added)
        processImages(folder+"/",lr_image_list,stcal,stmatcher,showPreviewGUI)

# define camera parameters
resolution = [2448,2048] # pixels
pixel_pitch=0.00000345 # meters
focal_length=0.008 # meters
baseline=0.3 # meters
# define load mode
load_mode = LOAD_MODE_ALL
# define folder
folder = "."
# define show preview GUI
showPreviewGUI = False

# define stereo matcher
#stmatcher = cv2.StereoBM_create() # faster / less accurate
stmatcher = cv2.StereoSGBM_create() # slower / more accurate

# define stereo matcher parameters
min_disp = 1037
num_disparities = 30
block_size = 5
uniqueness_ratio = 15
speckle_size = 30
speckle_range = 1000

# initalise stereo matcher matcher
calc_block = (2 * block_size + 5)
stmatcher.setBlockSize(calc_block)
stmatcher.setMinDisparity(int(min_disp - 1000))
stmatcher.setNumDisparities(16*(num_disparities+1))
stmatcher.setUniquenessRatio(uniqueness_ratio)
stmatcher.setSpeckleWindowSize(speckle_size)
stmatcher.setSpeckleRange(speckle_range)

# run 3d generation
gen3d(resolution,pixel_pitch,focal_length,baseline,load_mode,stmatcher,showPreviewGUI)