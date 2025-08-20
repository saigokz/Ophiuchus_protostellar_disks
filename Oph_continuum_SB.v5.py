#################################################################
## Imaging script (Imaging data) version 2 for Oph 2023.1.00545.S 
## This script was written for CASA 6.5.2 or later 
##
VERSION_KS = "5.0"
##
#################################################################
## Usage
## 1. Set the path of the MS(s) at Setting 1
##  If using SB or LB only, set the path for that dataset only.
##  If using SBLB (SB and LB), set the paths for both datasets.
##
## 2. The name of the MS are specified using the MS_name
##    (ex. MS_name = '*ms.ave.cont').
##  * Input MS(s) must contain only one field.
##  * All SPWs will be used, so it should be line free.
##
## 3. Set imaging paramters if necessary.
##
## 4. Run this script on CASA version 6.5.2 or later if possible.
##    (ex. execfile("Oph_continuum_LB.v2.py")
##
## Created by K.Saigo on 2025_08_01
## Modification History
##  v.1.0 2025_08_05: Modification of the parameter setting section by K.Saigo 
##  v.2.0 2025_08_07: Auto-threshold setting from MS*, export FITS by K.Saigo
##       * using get_sensitivity_nodata_params in eDisk reduction_utils3.py
##  v.2.1 2025_08_08: bug fix (delete nsigma option etc.) By J.Hashimoto
##  v.3.0 2025_08_10: logging, ajustment of imaging params By K.Saigo
##  v.4.0 2025_08_13: use get_sensitivity in selfcal_helpers By K.Saigo
##  v.5.0 2025_08_15: Estimattion of sigma from a temporary CLEAN image By K.Saigo
####
# Reduced by
Reducted_by = " "  # optional  ex. "John Smith"  (This is just written in the LOG file.)

### Import statements
import os
import glob
import numpy as np
import sys
import re
from casatools import msmetadata
from datetime import datetime, timezone
sys.path.append("./")        
#from selfcal_helpers import *

################################################################
################ SET DATA PATH/IMAING PARAMETERS  ##############
################ USERS NEED TO SET STUFF HERE     ##############
################################################################
### parallel mode? 
parallel   = False #True  


## Setting 1: Data Path and Search name
path_SB = './'
path_LB = './'
#path_7M = '/lwk/2023.1.01234.S/J162145.1_a_06_7M/calibrated/Work_SB_J162145.1'

## Setting 2: Search rule for MS data names
MS_name = '*.ms.ave.cont'  

## Setting 3: Data selection (select data)
data_select = 'SB'
#data_select = 'LB'
#data_select = 'SBLB'
#data_select = '7M'
#data_select = 'TM'


### Setting 4: Imaging Parameters
# If sigma0 = -1 is set, sigma is estimated by  atemporal CLEAN image.
sigma0      = -1 # or real number (Jy/Beam) (ex, set 4.4e-5 for 0.044 mJy/beam). 
scales      = -1 # scale = -1, the default value will be used.
cellsize    = -1 # cellsize = -1, the default value will be used.
imsize      = -1 # imsize = -1, the default value will be used.
datacolumn  = 'corrected' # or 'data'
robust_all  =  [-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0]  # ex. [0.5, 2.0]
uvtaper_all = [''] # or ['1000klambda', '2000klambda', '3000klambda']

## default imaging parameters
imaging_param = {
   'SB': {'scales': [0, 5, 30],
          'cellsize':'0.08arcsec',
          'imsize':640,
          'cont_spws':'25,27,29,31,33,35,37'},
   'LB': {'scales': [0, 5, 30],
          'cellsize':'0.02arcsec',
          'imsize':2500,
          'cont_spws':'25,27,29,31,33,35,37'},       
   'SBLB': {'scales': [0, 5, 30],
            'cellsize':'0.02arcsec',
            'imsize':2500,
          'cont_spws':''},           
   '7M': {'scales': [0, 5],
          'cellsize':'0.4arcsec',
          'imsize':256,
          'cont_spws':'25,27,29,31,33,35,37'},           
}

###############################################################
################## RUN A FINAL IMAGE SET ######################
###############################################################
## Generate a vislist
vislist1, vislist2, vislist3 = [], [], []
if data_select=='SB':
   vislist1=glob.glob(path_SB+'/'+MS_name)
if data_select=='LB':
   vislist1=glob.glob(path_LB+'/'+MS_name)
if data_select=='SBLB':
   vislist1=glob.glob(path_SB+'/'+MS_name)
   vislist2=glob.glob(path_LB+'/'+MS_name)
if data_select=='7M':
   vislist1=glob.glob(path_7M+'/'+MS_name)
#
vislist = vislist1 + vislist2 + vislist3
print(vislist)
if len(vislist) == 0:
   sys.exit('No Measurement sets found in current working directory, exiting')

## Get Field name from MS[0]
msmd = msmetadata()
msmd.open(vislist[0])
used_field_ids = list(set(msmd.fieldsforintent('*')))
# Check whether the MS contains only one field.
if len(used_field_ids) != 1:
    used_names = [msmd.fieldnames()[i] for i in used_field_ids]
    raise RuntimeError(f"Expected exactly 1 field, but found {len(used_names)} fields used: {used_names}")
field_id = used_field_ids[0]
field_name = msmd.fieldnames()[field_id]
pc_rad     = msmd.phasecenter(field_id)
print("Field name:", field_name)
msmd.done()
field   = field_name
prefix  = field_name 

## set default parameters
if scales == -1:  scales   = imaging_param[data_select]['scales']
if cellsize == -1:cellsize = imaging_param[data_select]['cellsize']
if imsize == -1:  imsize   = imaging_param[data_select]['imsize']

## set phasecenter (You can set phasecenter or swith coordinate systems) 
phasecenter = '' #the same as that of MSs 
#phasecenter = 'J2000 '+str(pc_rad['m0']['value'])+'rad '+str(pc_rad['m1']['value'])+'rad'
   
##########  tclean loop ########
for uvtaper in uvtaper_all:
   for robust in robust_all:
      imagename=prefix+'_'+data_select+'_continuum_robust_'+str(robust)
      ## Estimation of sigma for determining the threshold
      sigma = sigma0
      st_sigma = "User defined vale" # comment for LOG
      if sigma0 == -1: # estimation of sigma by temporary CLEAN
         st_sigma = "Estimated from a temporary CLEAN image"
         im_tmp = 'im_cont.dirty'
         nsigma = 5
         # 1st round 
         os.system('rm -rf '+im_tmp+'.*')
         tclean(vis         = vislist, 
                imagename   = im_tmp, 
                specmode    = 'mfs', 
                datacolumn  = datacolumn,
                savemodel   = 'none',
                phasecenter = phasecenter,
                deconvolver = 'mtmfs',
                nterms      = 2,
                scales      = scales, 
                weighting   ='briggs', 
                robust      = robust,
                imsize      = imsize,
                cell        = cellsize, 
                smallscalebias = 0.6, 
                niter       = 50000,  #we want to end on the threshold
                interactive = False,
                threshold   = 1,
                nsigma      = nsigma,
                gain        = 0.1,
                cycleniter  = 300,
                cyclefactor = 3,
                uvtaper     = uvtaper,
                uvrange     = '',
                mask        = '',
                usemask     = 'auto-multithresh',
                sidelobethreshold = 3.0,
                smoothfactor      = 1.0,
                parallel = parallel,
                startmodel  = '')
         im_mask = im_tmp+'.mask'
         sigma_tmp  = imstat(imagename=im_tmp+'.image.tt0',mask=f'"{im_mask}" == 0')['rms'][0]
         #2nd round with threshold = 5 * sigma_tmp
         os.system('rm -rf '+im_tmp+'.*')
         tclean(vis         = vislist, 
                imagename   = im_tmp, 
                specmode    = 'mfs', 
                datacolumn  = datacolumn,
                savemodel   = 'none',
                phasecenter = phasecenter,
                deconvolver = 'mtmfs',
                nterms      = 2,
                scales      = scales, 
                weighting   ='briggs', 
                robust      = robust,
                imsize      = imsize,
                cell        = cellsize, 
                smallscalebias = 0.6, 
                niter       = 50000,  #we want to end on the threshold
                interactive = False,
                threshold   = 5.0*sigma_tmp,
                gain        = 0.1,
                cycleniter  = 300,
                cyclefactor = 3,
                uvtaper     = uvtaper,
                uvrange     = '',
                mask        = '',
                usemask     = 'auto-multithresh',
                sidelobethreshold = 3.0,
                smoothfactor      = 1.0,
                parallel = parallel,
                startmodel  = '')
         im_mask = im_tmp+'.mask'
         sigma  = imstat(imagename=im_tmp+'.image.tt0',mask=f'"{im_mask}" == 0')['rms'][0]
         os.system('rm -rf '+im_tmp+'.*')         
      print(' ')
      print('------------         Start New Imaging        ---------------')
      print('imagename = '+imagename  )
      print(' - Robust = '+str(robust)+' uvtaper = '+uvtaper)
      print(f" - Expected sigma = {str(sigma)} Jy/Beam  ({st_sigma})")
      print(f" - scales = {scales}, cellsize = {cellsize}, imsize = {imsize}")
      #
      os.system('rm -rf '+imagename+'*  tclean.last')
      #
      tclean(vis         = vislist, 
             imagename   = imagename, 
             specmode    = 'mfs', 
             datacolumn  = datacolumn,
             savemodel   = 'none',
             phasecenter = phasecenter,
             deconvolver = 'mtmfs',
             nterms      = 2,
             scales      = scales, 
             weighting   ='briggs', 
             robust      = robust,
             imsize      = imsize,
             cell        = cellsize, 
             smallscalebias = 0.6, 
             niter       = 50000,  #we want to end on the threshold
             interactive = False,
             threshold   = 3.0*sigma,
             gain        = 0.1,
             cycleniter  = 300,
             cyclefactor = 3,
             uvtaper     = uvtaper,
             uvrange     = '',
             mask        = '',
             usemask     = 'auto-multithresh',
             sidelobethreshold = 3.0,
             smoothfactor      = 1.0,
             pbmask   = 0.1,
             pblimit  = 0.1,
             parallel = parallel,
             startmodel  = '')
      # Export FITS files (default: image, pbcor image)
      imname    = imagename+'.image.tt0'
      fitsname  = imagename+'.image.tt0.fits'
      pbname    = imagename+'.pb.tt0'
      pbcorname = imagename+'.pbcor.tt0'
      impbcor(imagename=imname,pbimage=pbname,outfile=pbcorname)
      exportfits(imagename=imname,fitsimage=imname+'.fits',overwrite=True,dropdeg=True)
      exportfits(imagename=pbcorname,fitsimage=pbcorname+'.fits',overwrite=True,dropdeg=True)
      # addtional exportfits (alpha, alpha.err)
      imname    = imagename+'.alpha'
      exportfits(imagename=imname,fitsimage=imname+'.fits',overwrite=True,dropdeg=True)
      imname    = imagename+'.alpha.error'
      exportfits(imagename=imname,fitsimage=imname+'.fits',overwrite=True,dropdeg=True)
      #
      ## tclean log
      utc_now = datetime.now(timezone.utc)
      cwd = os.getcwd()
      ver_line = casalog.version()
      im_mask =imagename+'.mask'
      sigma_final = imstat(imagename=imagename+'.image.tt0',mask=f'"{im_mask}" == 0')['rms'][0]
      Flux_final  = imstat(imagename=imagename+'.image.tt0',mask=f'"{im_mask}" == 1')['flux'][0]
      Peak_final  = imstat(imagename=imagename+'.image.tt0')['max'][0]
      Peak_Pos_final  = imstat(imagename=imagename+'.image.tt0')['maxposf']
      im_final = imagename+'.image.tt0'
      bmaj      = imhead(imagename=im_final)['restoringbeam']['major']['value']
      bmaj_unit = imhead(imagename=im_final)['restoringbeam']['major']['unit']
      bmin      = imhead(imagename=im_final)['restoringbeam']['minor']['value']
      bpa       = imhead(imagename=im_final)['restoringbeam']['positionangle']['value']
      bpa_unit  = imhead(imagename=im_final)['restoringbeam']['positionangle']['unit']   
      st_log=[]
      st_log.append(f"########################################################")
      st_log.append(f"## - Imaging script version: {VERSION_KS}")
      st_log.append(f"## - Image Name  : {imagename}")     
      st_log.append(f"## - CASA version:{ver_line}")
      st_log.append(f"## - Reducted by : {Reducted_by}")        
      st_log.append(f"## - Working directory: {cwd}")
      st_log.append(f"## - Execution   : {str(utc_now)} (UTC)")
      st_log.append(f"## Imaging Setting ")
      st_log.append(f"## - field_name = {field_name}")
      st_log.append(f"## - robust = {robust}, uvtaper = {uvtaper}")
      st_log.append(f"## - cellsize = {cellsize}, imsize = {imsize}, scales = {scales} ")
      st_log.append(f"## - sigma_temporal to determine threshold ({st_sigma}) = {str(sigma)}")
      st_log.append(f"## ")
      st_log.append(f"## Measurements from the Final Image (XX.image.tt0) ")
      st_log.append(f"## - Restoring Beam: {bmaj} x {bmin} ({bmaj_unit}) PA = {bpa} {bpa_unit}")
      st_log.append(f"## - sigma_final (Measured outside the masked region) = {str(sigma_final)} Jy/Beam")
      st_log.append(f"## - Peak brightness =  {str(Peak_final)} Jy/Beam")
      st_log.append(f"## - Peak Position   =  {str(Peak_Pos_final)} ")
      st_log.append(f"## - Flux (Integration within the masked region) = {str(Flux_final)} Jy")
      st_log.append(f"########################################################")
      st_log.append(f"# ")
      #
      #   :os.system('rm -rf '+imagename+fn_del)
      fn_log = imagename+'.tclean.LOG'
      for item in st_log: print(item)
      if os.path.exists('tclean.last'):
         os.system('cp -f tclean.last '+fn_log)
      else:
         open(fn_log, "w").write("Since no tclean.last file was generated, only the log will be output. \n")
      for item in reversed(st_log): os.system("sed -i '1i "+ item+" ' "+fn_log)
      print(" export LOG file: "+fn_log)
      print("------------ finish imaging of "+imagename+" ---------------")



###############################################################
########################### CLEANUP ###########################
###############################################################

"""
### Remove extra image products
os.system('rm -rf *.residual* *.psf* *.model* *dirty* *.sumwt* *.gridwt* *.workdirectory')
"""

