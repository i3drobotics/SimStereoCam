import os, time
import cv2
from Stereo3D import Stereo3D, StereoCalibration
from Stereo3D.StereoCapture import *

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

def processImages(image_folder,lr_image_list,stcal,stmatcher):
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
        '''
        while(True):
            exit_code = s3D.run_frame()
            if (exit_code == s3D.EXIT_CODE_QUIT):
                break
        '''
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


LOAD_MODE_CHANGES_ONLY = 0
LOAD_MODE_ALL = 1

# define camera parameters
resolution = [2448,2048]
pixel_pitch=0.00000345
focal_length=0.008
baseline=0.3
# define load mode
load_mode = LOAD_MODE_ALL
# define folder
folder = "."

# setup cal files for generating 3d
stcal = genCal(resolution,pixel_pitch,focal_length,baseline)
# setup stereo matcher
#stmatcher = "BM"
'''
stmatcher = cv2.StereoBM_create()
default_min_disp = 1037
default_num_disparities = 30
default_block_size = 8
default_uniqueness_ratio = 15
default_texture_threshold = 60
default_speckle_size = 30
default_speckle_range = 1000
calc_block = (2 * default_block_size + 5)
stmatcher.setBlockSize(calc_block)
stmatcher.setMinDisparity(int(default_min_disp - 1000))
stmatcher.setNumDisparities(16*(default_num_disparities+1))
stmatcher.setUniquenessRatio(default_uniqueness_ratio)
stmatcher.setTextureThreshold(default_texture_threshold)
stmatcher.setSpeckleWindowSize(default_speckle_size)
stmatcher.setSpeckleRange(default_speckle_range)
'''
#stmatcher = "SGBM"
stmatcher = cv2.StereoSGBM_create()
default_min_disp = 1037
default_num_disparities = 30
default_block_size = 5
default_uniqueness_ratio = 15
default_texture_threshold = 60
default_speckle_size = 30
default_speckle_range = 1000
calc_block = (2 * default_block_size + 5)
stmatcher.setBlockSize(calc_block)
stmatcher.setMinDisparity(int(default_min_disp - 1000))
stmatcher.setNumDisparities(16*(default_num_disparities+1))
stmatcher.setUniquenessRatio(default_uniqueness_ratio)
stmatcher.setSpeckleWindowSize(default_speckle_size)
stmatcher.setSpeckleRange(default_speckle_range)

if (load_mode == LOAD_MODE_CHANGES_ONLY):
    # check for new files in folder
    
    before = dict ([(f, None) for f in os.listdir (folder)])
    added = []
    while 1:
        time.sleep (10)
        after = dict ([(f, None) for f in os.listdir (folder)])
        added = [f for f in after if not f in before]
        #removed = [f for f in before if not f in after]
        if added: 
            print("Added: ", ", ".join (added))
            lr_image_list = getImagesToProcess(added)
            processImages(folder+"/",lr_image_list,stcal,stmatcher)
        #if removed: 
        #    print ("Removed: ", ", ".join (removed))
        before = after
elif (load_mode == LOAD_MODE_ALL):
    files = dict ([(f, None) for f in os.listdir (folder)])
    added = [f for f in files if (os.path.splitext(f)[1]==".png")]
    lr_image_list = getImagesToProcess(added)
    processImages(folder+"/",lr_image_list,stcal,stmatcher)