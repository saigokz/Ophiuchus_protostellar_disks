## Clean Up the Work directory (Delete unnecessary files)
# Delete unnecessary files generated during auto-selfcal and imaging.
# - For MS, keep only the .contsub and the averaged continuum (line-free) MS.
# - For selfcal, keep only the gain table and remove temporary files.
# - For imaging, keep the FITS, .residual, .psf, and .pd files.
# Created 2025 08 26 K.Saigo
# Revised 2025 10 06 K.Saigo
##
import numpy as np
from scipy import stats
import glob
import sys
import os
sys.path.append("./")
#from selfcal_helpers import *


## Name of Trash directory
Trash = "Trash"

## make Trash Directory
if os.path.exists(Trash):
    print(f"The Trash directory {Trash} already exists.")
    print(f"Is it okay to move unnecessary files to this Trash directory?")
    ans = input(f"Press Y or Enter to continue, or N to stop: ")
    if ans.strip().lower() in ["", "y", "yes"]:
        print("Continuing...")
    else:
        print("Execution stopped.")
        sys.exit() 
else:
    os.makedirs(Trash)


## If the saved image is in CASA image format, it will be converted to FITS.
print("First, if the saved image is in CASA image format, it will be converted to FITS format.")
convert_fits = []
convert_fits += glob.glob('*continuum*.mask')
convert_fits += glob.glob('*.residual')
for im_casa in convert_fits:
    im_fits = im_casa + '.fits'
    if not os.path.exists(im_fits):
        exportfits(imagename=im_casa,fitsimage=im_fits,overwrite=True,dropdeg=True)
        print(f'Converted {im_casa} to {im_fits}')
            

## Remove duplicated images created for the FITS file
fits_images = glob.glob("*.fits")
for fn in fits_images:
    fn_image, ext = os.path.splitext(fn)
    print(fn_image)  
    os.system('mv '+fn_image+' '+Trash)


##
filelist = []
filelist.extend(glob.glob("*.sumwt"))
filelist.extend(glob.glob("*.model"))
filelist.extend(glob.glob("*.residual"))
filelist.extend(glob.glob("*.mask"))
filelist.extend(glob.glob("*.psf"))
filelist.extend(glob.glob("*.pb"))
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
print(f"Is it okay to delete the Trash directory after running:  {cmd}")
ans = input("Press Enter of Y to delete it, or N to keep it: ")
if ans.strip().lower() in ["", "y", "yes"]:
    os.system(cmd)
    print("Command executed.")
else:
    print("Keep Trash directory.")


