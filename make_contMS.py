#########################################################
## Prepation of continuum imaging data (line flagging => averaging => split)
##
##  This script generates new MS with line channel range flagged according to the information in cont.dat (Channel averaging can also be performed during this process). The original MS remains unchanged, and the output MS will have the extension .ave.cont.
##
## Note: This script requires selfcal_helpers.py from J. Tobin's auto_selfcal repository. Please download it from the above GitHub repository and place the *.py files in your working directory.
##
## Created: 2025_07_30 by Kazuya Saigo
## Modifycation history:
##    - 2025_08_01  by Kazuya Saigo: introduction of statwt
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

## Setting 
use_contdotdat         = True
export_average_contMS  = True  #ms.ave.cont

MS_search_word  = '*_target.ms'
cont_spws       = '25, 27, 29, 31, 33, 35, 37' 
cont_avg_width  = [10, 80, 40, 80, 80, 40, 10] #n channels to average; approximately aiming for 5 MHz channels
#cont_avg_width  = '5MHz'

################################################################

## Get list of MS files in directory
vislist=glob.glob(MS_search_word)
if len(vislist) == 0:
   vislist=glob.glob('*_targets.ms')   # adaptation for PL2022 output
   if len(vislist)==0:
      vislist=glob.glob('*_cont.ms')   # adaptation for PL2022 output
   elif len(vislist)==0:
      sys.exit('No Measurement sets found in current working directory, exiting')

## Get infomation 
telescope = get_telescope(vislist[0])
all_targets, targets_vis, vis_for_targets, vis_missing_fields, vis_overflagged=fetch_targets(vislist, telescope)

## check path of cont.dat
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
spwsarray_dict = dict(zip(vislist,[np.concatenate([tmp[vis][band]['spwarray'] for band in bands]) for vis in vislist]))

flag_name_dict = dict()
for vis in vislist:
   flag_name = vis+'.before_temp_flag'
   flag_name_dict[vis] = flag_name
   versions = flagmanager(vis=vis, mode='list')
   existing = [versions[i]['name'] for i in versions if isinstance(i, int)]
   if flag_name in existing:
      flagmanager(vis=vis, mode='delete', versionname=flag_name)
   flagmanager(vis=vis, mode='save', versionname=flag_name, comment='Before temporary channel flagging')

## temporary flaging
flag_spectral_lines(vislist,all_targets,spwsarray_dict)

## split averaging line flagged MS
if export_average_contMS:
   for vis in vislist:
      outputvis=vis+'.ave.cont'
      print('split averaged cont MS: '+outputvis)
      if os.path.exists(outputvis):os.system('rm -rf '+outputvis)
      mstransform(vis=vis, outputvis=outputvis,spw=cont_spws,chanaverage = True , chanbin=cont_avg_width ,datacolumn = 'corrected' ,reindex=False)
      statwt(vis=vis, datacolumn='corrected')  ## for WEIGHT_SPECTRUM  
      print(flag_name_dict[vis])
      flagmanager(vis=vis, mode='restore', versionname=flag_name_dict[vis])


                  

                  
