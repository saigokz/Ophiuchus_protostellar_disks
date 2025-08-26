#########################################################
## Prepation of continuum imaging data (line flagging => averaging => split)
##
##  This script generates new MS with line channel range flagged according to the information in cont.dat (Channel averaging can also be performed during this process). The original MS remains unchanged, and the output MS will have the extension .ave.cont.
##
## Note: This script requires selfcal_helpers.py from J. Tobin's auto_selfcal repository. Please download it from the above GitHub repository and place the *.py files in your working directory.
##
## Created: 2025_07_30 by Kazuya Saigo
## Modifycation history:
##  - 2025_08_01 Introduction of statwt by Kazuya Saigo
##  - 2025_08_22 Handle No CORRECTED column case by Kazuya Saigo
##
## Usage:
## 1. Place the MS data set (containing only one science target field and sharing the same SPWs) and cont.dat in the same work directory. This is Not support concatenated data sets.
## 2. Place selfcal_helpers.py from auto_selfcal (J Tobin) in the same directory (or set Python path).
## 3. Modify Setting Part in thsi script if necessary.
## 4. Run the script with CASA version 6.5.2 or later
##    execfile("make_contMS.py")
##
#############################################################
import numpy as np
from scipy import stats
import glob
import sys
sys.path.append("./")
from selfcal_helpers import *

### Setting 1
# To flag line channels, plase set use_contdotdat=True and place cont.dat in the directory. 
use_contdotdat         = True  
export_average_contMS  = True  # export XXXXX.ms.ave.cont


### Setting 2  Data name and spectral setting 
# Please check the listobs and edit. cont_avg_width control chanel averaging.

MS_search_word  = '*_target.ms'   # MS data name

cont_spws       = '25, 27, 29, 31, 33, 35, 37'

#cont_avg_width  = [10, 80, 40, 80, 80, 40, 10]  # 2023.1.00545.S => 5MHz channels
cont_avg_width  = [80, 80, 80, 80, 80, 80, 5] # AGE-PRO 2021.00128.S => 5MHz channels


################################################################

## Get list of MS files in directory
vislist=glob.glob(MS_search_word)
if len(vislist) == 0:
   vislist=glob.glob('*_targets.ms')   # adaptation for PL2022 output
   if len(vislist)==0:
      vislist=glob.glob('*_cont.ms')   # adaptation for PL2022 output
   elif len(vislist)==0:
      sys.exit('No Measurement sets found in current working directory, exiting')


## set datacolumn: corrected or data column
tb.open(vislist[:1][0])
exists = 'CORRECTED_DATA' in tb.colnames()
tb.close()
print('CORRECTED_DATA exists:', exists)
if exists:
   datacolumn='corrected'
else:
   datacolumn='data'
   print('#################  Important Note  ###############################')
   print('This data does not contain a CORRECTED column.')
   print('The averaging and splitting will be performed using the DATA column ')
   print("  ")
   print("Press Enter to continue...")
   input()  #
   print("Continuing the script...")

   
## Get infomation 
print('checking data info.')
telescope = get_telescope(vislist[0])
all_targets, targets_vis, vis_for_targets, vis_missing_fields, vis_overflagged=fetch_targets(vislist, telescope)

## Check path of cont.dat
print('checking cont.dat')
if use_contdotdat:
   if os.path.exists("cont.dat"):
      #os.system("cp cont.dat cont.dat.original")
      if np.any([len(parse_contdotdat('cont.dat',target)) == 0 for target in all_targets]):
         print("Found existing cont.dat, but it is missing targets!!")
         sys.exit(" Error 1: Stop Execution at reading cont.dat") #!!
   else:
      sys.exit(" Error 2: Stop Execution can not find cont.dat file") 


## make spwsarray_dict for line flagging
selfcal_library, selfcal_plan, gaincalibrator_dict = {}, {}, {}
bands = vis_for_targets[all_targets[0]]['Bands']
_, tmp =get_bands(vislist, all_targets, telescope)

   
## split averaging line flagged MS
print('flaging, averaging, splitting')
if export_average_contMS:
   for vis in vislist:
      vis_tmp   = vis+'.tmp'
      outputvis = vis+'.ave.cont'
      if os.path.isdir(vis_tmp):
         os.system('rm -rf '+vis_tmp)
      if os.path.isdir(vis_tmp+'.flagversions'):
         os.system('rm -rf '+vis_tmp+'.flagversions')
      os.system('cp -r '+vis + '  '+vis_tmp)
      spwsarray_dict = {vis_tmp: np.concatenate([tmp[vis][band]['spwarray'] for band in bands])}
      print(spwsarray_dict)
      #flag line
      flag_spectral_lines([vis_tmp],all_targets,spwsarray_dict)
      print('split averaged cont MS: '+outputvis)
      if os.path.exists(outputvis):
         os.system('rm -rf '+outputvis)
      if os.path.exists(outputvis+'.flagversions'):
         os.system('rm -rf '+outputvis+'.flagversions')
      mstransform(vis=vis_tmp, outputvis=outputvis,spw=cont_spws,chanaverage = True , chanbin=cont_avg_width ,datacolumn = datacolumn ,reindex=False)
      statwt(vis=outputvis, datacolumn = 'data')  ## for WEIGHT_SPECTRUM  
      #print(flag_name_dict[vis])
      #flagmanager(vis=vis, mode='restore', versionname=flag_name_dict[vis])
      os.system('rm -rf '+vis_tmp+' '+vis_tmp+'.flagversions '+outputvis+'.flagversions ') 


