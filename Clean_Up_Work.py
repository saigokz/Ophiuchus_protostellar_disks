## Clean Up the Work directory (Delete unnecessary files)
# Delete unnecessary files generated during auto-selfcal and imaging.
# - For MS, keep only the .contsub and the averaged continuum (line-free) MS.
# - For selfcal, keep only the gain table and remove temporary files.
# - For imaging, keep the FITS, .residual, .psf, and .pd files.
# Created 2025 08 26 K.Saigo
##
import numpy as np
from scipy import stats
import glob
import sys
sys.path.append("./")
from selfcal_helpers import *

## Base name of Trash
Trash_base = "Trash"

## make Trash Directory
Trash = Trash_base
if os.path.exists(Trash_base):
    _Trash = Trash_base
    counter = 1
    while os.path.exists(_Trash):
        _Trash = f"{Trash_base}{counter}"
        counter += 1
    #
    print(f"The directory {Trash_base} already exists.")
    print(f"Do you want to create a new one, {_Trash}?  ") 
    ans = input(f"Press Enter or Y to create {_Trash}, N use {Trash_base}: ")   
    if ans.strip().lower() in ["", "y", "yes"]:
        Trash = _Trash
        os.makedirs(Trash)



## Remove duplicated images created for the FITS file
fits_images = glob.glob("*.fits")
for fn in fits_images:
    fn_image, ext = os.path.splitext(fn)
    print(fn_image)  
    os.system('mv '+fn_image+' '+Trash)


filelist = []
filelist.extend(glob.glob("*.sumwt"))
filelist.extend(glob.glob("*.model"))
#filelist.extend(glob.glob("*.residual"))
filelist.extend(glob.glob("*.mask"))
#filelist.extend(glob.glob("*.psf"))
#filelist.extend(glob.glob("*.pb"))
filelist.extend(glob.glob("*.tt0"))
filelist.extend(glob.glob("*.tt1"))
filelist.extend(glob.glob("*.tt2"))
for fn in filelist:
    os.system('mv '+fn+' '+Trash)


## Remove original ms and flagversions
filelist = []
filelist.extend(glob.glob("*_targets.ms"))
filelist.extend(glob.glob("*.flagversions"))
for fn in filelist:
    os.system('mv '+fn+' '+Trash)

# Remove Temporal file of auto-selfcal expet for gain tables
filelist = []
filelist.extend(glob.glob("Target_*"))
filelist = [f for f in filelist if not f.endswith(".g")]
for fn in filelist:
    os.system('mv '+fn+' '+Trash)



### Remove Trash or not
cmd = 'rm -r '+Trash
print(f"About to execute: {cmd}")
ans = input("Do you want to continue? (Press Enter or Y to confirm, N to cancel): ")

if ans.strip().lower() in ["", "y", "yes"]:
    os.system(cmd)
    print("Command executed.")
else:
    print("Cancelled.")



