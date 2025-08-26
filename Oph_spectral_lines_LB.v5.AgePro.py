#################################################################
## Spectral Lines Imaging script version 2 for Oph 2023.1.00545.S 
## This script was written for CASA 6.5.2 or later 
##
VERSION_KS = "5.0.AgePro"
##
###############################################################
## Usage
## 1. Set the path of the MS(s) at Setting 1
##  If using SB or LB only, set the path for that dataset only.
##  If using SBLB (SB and LB), set the paths for both datasets.
##
## 2. The name of the MS are specified using the MS_name
##    (ex. MS_name = '*.ms.ave.cont' )
##  * Input MS(s) must contain only one field.
##  * All SPWs will be used, so it should be line free.
##
## 3. Set imaging paramters if necessary.
##
## 4. Run this script on CASA version 6.5.2 or later if possible.
##    (ex. execfile("Oph_spectral_line.v2.py")
##
## Created by K.Saigo 2025_08_03
## Modification History
##  v.1.0 2025_08_05: Modification of the parameter setting section   by K.Saigo
##  v.2.0 2025_08_07: Auto-threshold setting from MS*, export FITS  by K.Saigo
##       * using get_sensitivity_nodata_params in eDisk reduction_utils3.py
##  v.2.1 2025_08_08: bug fix (delete nsigma option etc.) By J.Hashimoto
##  v.3.0 2025_08_10: Estimating sigma from a temporary dirty map By K.Saigo
##  v.4.0 2025_08_13: Parallel setting and Remove unused imports By K.Saigo  
##  v.5.0 2025_08_18: Update moment 1 map By K.Saigo
##  v.5.0.AgePro 2025_08_20: Age-Pro spectral setting By K.Saigo
####
#
## Sample of Spectral Windows of 2021.1.00128.L (AGE PRO)
# ID Name Chans CtrFreq(MHz)  [range]      TotBW(kHz) Wid(kHz) 
# 25 BB1_1  960 217.235GHz [217.205-217.264] 58.6MHz 61.kHz(84m/s) DCN_J=3-2    
# 27 BB1_2  960 218.218GHz [218.189-218.248] 58.6MHz 61.kHz(84m/s) H2CO_3(0,3)-2(0,2)
# 29 BB2_1  960 219.556GHz [219.527-219.586] 58.6MHz 61.kHz(83m/s) C18O_2-1 
# 31 BB2_2  960 220.39GHz  [220.365-220.424] 58.6MHz 61.kHz(83m/s) 13CO_2-1	
# 33 BB3_1  960 230.53GHz  [230.505-230.563] 58.6MHz 61.kHz(79m/s) CO_2-1 	
# 35 BB3_2  960 231.318GHz [231.288-231.347] 58.6MHz 61.kHz(79m/s) N2D+_3-2 	
# 37 BB4_1 1920 234.007GHz [233.070-234.945] 1.875GHz               continuum
##
# Reduced by
Reducted_by = " "  # optional   ex. "John Smith" (This is just written in the LOG file.)


### Import statements
import os
import glob
import numpy as np
import sys
import re
from casatools import msmetadata
from datetime import datetime, timezone
#sys.path.append("./")
#from selfcal_helpers import *

################################################################
################ SET DATA PATH/IMAING PARAMETERS  ##############
################ USERS NEED TO SET STUFF HERE     ##############
################################################################
### parallel mode? 
parallel   = False #True  

## Setting 1: Data Path 
path_SB = './'
path_LB = './'
#path_7M = '/lwk/saigo/2021.1.00128.L/'

## Setting 2: Search rule for MS data names
MS_name = '*_targets.contsub.ms'

## Setting 3: Data selection (select data)
#data_select = 'SB'
data_select = 'LB'
#data_select = 'SBLB'
#data_select = '7M'
#data_select = 'TM'


### Setting 4: Imaging Parameters
# If sigma0 = -1 is set, sigma is estimated by temporary dirty map (channel 1~2)
# Alternatively, set a specific value for sigma0 (ex. 1.2e-4) [unit is Jy/Beam]
sigma0      = -1 # 
scales      = -1 # scale = -1, the default value will be used.
cellsize    = -1 # cellsize = -1, the default value will be used.
imsize      = -1 # imsize = -1, the default value will be used.
datacolumn  = 'corrected' # or 'data'
robust      = [-0.5, 0.0, 0.5, 2.0] #
uvtaper     = [''] # or ['1000klambda', '2000klambda']

## default imaging parameters
# 'cont_spws' does not use in spectral line imaging
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
          'cont_spws':'25,27,29,31,33,35,37'},
   '7M': {'scales': [0, 5],
          'cellsize':'0.4arcsec',
          'imsize':256,
          'cont_spws':'25,27,29,31,33,35,37'},
}
### Setting 5: imaging line setting 
## line set for eDisk
#image_list = ["C18O","12CO","13CO","SO","H2CO_3_21-2_20_218.76GHz","SiO",
#               "H2CO_3_03-2_02_218.22GHz","H2CO_3_22-2_21_218.47GHz",
#               "c-C3H2_217.82","cC3H2_217.94","cC3H2_218.16","DCN","CH3OH"]

## line set for AGE-PRO data
image_list = ["C18O","12CO","13CO","H2CO_3_03-2_02_218.22GHz","DCN","N2Dp"]



## master list of line setting 
image_master_list = {
   ### C18O images
   "C18O":dict(chanstart='-5.5km/s', chanwidth='0.167km/s',
               nchan=120, linefreq='219.56035410GHz', linespw='29',
               robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### 13CO images
   "13CO":dict(chanstart='-5.5km/s', chanwidth='0.1675km/s',
               nchan=120, linefreq='220.39868420GHz', linespw='31',
               robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### 12CO images
   "12CO":dict(chanstart='-30.0km/s', chanwidth='0.167km/s', 
               nchan=360, linefreq='230.538GHz', linespw='33',
               robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper), 
   ### 12CO images
   #"12CO":dict(chanstart='-100.0km/s', chanwidth='0.635km/s', 
   #            nchan=315, linefreq='230.538GHz', linespw='33',
   #            robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper), 
   #### SO Images
   #"SO":dict(chanstart='-5.5km/s', chanwidth='0.167km/s', 
   #          nchan=120, linefreq='219.94944200GHz', linespw='31',
   #          robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper), 
   ### H2CO 3(2,1)-2(2,0) Images
   #"H2CO_3_21-2_20_218.76GHz":dict(chanstart='-5.5km/s',chanwidth='0.32km/s',
   #         nchan=60, linefreq='218.76006600GHz', linespw='29',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### H2CO 3(0,3)-2(0,2) Images
   "H2CO_3_03-2_02_218.22GHz":dict(chanstart='-5.5km/s',chanwidth='0.167km/s',
            nchan=120, linefreq='218.22219200GHz', linespw='27',
            robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### H2CO 3(0,3)-2(0,2) Images
   #"H2CO_3_03-2_02_218.22GHz":dict(chanstart='-10km/s',chanwidth='1.34km/s',
   #         nchan=23, linefreq='218.22219200GHz', linespw='27',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### H2CO 3(2,2)-2(2,1) Images
   #"H2CO_3_22-2_21_218.47GHz":dict(chanstart='-10km/s',chanwidth='1.34km/s', 
   #         nchan=23, linefreq='218.47563200GHz', linespw='25', 
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### c-C3H2 217.82 GHz Images
   #"c-C3H2_217.82":dict(chanstart='-10km/s', chanwidth='1.34km/s',
   #         nchan=23, linefreq='217.82215GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### c-C3H2 217.94 GHz Images
   #"cC3H2_217.94":dict(chanstart='-10km/s', chanwidth='1.34km/s', 
   #         nchan=23, linefreq='217.94005GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### c-C3H2 218.16 GHz Images
   #"cC3H2_218.16":dict(chanstart='-10km/s', chanwidth='1.34km/s', 
   #         nchan=23, linefreq='218.16044GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),
   ### DCN Images
   "DCN":dict(chanstart='-5.5km/s', chanwidth='0.167km/s',
            nchan=120, linefreq='217.2386GHz', linespw='25',
            robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),     
   ### DCN Images
   #"DCN":dict(chanstart='-10km/s', chanwidth='1.34km/s',
   #         nchan=23, linefreq='217.2386GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),     
   ### CH3OH Images
   #"CH3OH":dict(chanstart='-10km/s', chanwidth='1.34km/s',
   #         nchan=23, linefreq='218.44006300GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),     
   ### SiO Images
   #"SiO":dict(chanstart='-100km/s', chanwidth='1.34km/s', nchan=150, 
   #          linefreq='217.10498000GHz', linespw='25',
   #         robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper),     
   ### N2D+ 3-2 images !!AGE PRO only
   "N2Dp":dict(chanstart='-5.5km/s', chanwidth='0.167km/s', 
               nchan=120, linefreq='231.321635GHz', linespw='35',
               robust=robust,imsize=imsize,cellsize=cellsize,uvtaper=uvtaper), 
        }

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

vislist = vislist1 + vislist2 + vislist3
print(vislist)
if len(vislist) == 0:
   sys.exit('No Measurement sets found in current working directory, exiting')

## Get Field name from MS0 
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
if scales == -1:  scales = imaging_param[data_select]['scales']
if cellsize == -1:cellsize = imaging_param[data_select]['cellsize']
if imsize == -1:  imsize = imaging_param[data_select]['imsize']

## set phasecenter (You can set phasecenter or swith coordinate systems) 
phasecenter = '' #the same as that of MSs 
#phasecenter = 'J2000 '+str(pc_rad['m0']['value'])+'rad '+str(pc_rad['m1']['value'])+'rad'


### Loop through the spectral line images and make images.
for line in image_list:
   spw   = image_master_list[line]["linespw"]
   start = image_master_list[line]['chanstart']
   width = image_master_list[line]['chanwidth']
   nchan = image_master_list[line]['nchan']
   restfreq = image_master_list[line]['linefreq']
   #
   for uvtaper in image_master_list[line]["uvtaper"]:
      for robust in image_master_list[line]["robust"]:
         imagename = prefix+'_'+data_select+'_'+line+'_robust_'+str(robust)
         msmd.open(vislist[0])
         chan_width_Hz=abs( msmd.chanwidths(int(spw))[0]) #channel width [Hz]
         msmd.close()
         freq_GHz = float(restfreq.replace("GHz","") )
         chan_width_kms = chan_width_Hz*2.99792458e10/(freq_GHz*1e9) *1e-5  # km/s
         width_kms      = float(width.replace("km/s",""))
         #
         ## Estimation of sigma for determining the threshold
         st_sigma = "User defined vale" # comment for LOG
         sigma = sigma0
         if sigma0 == -1:  # by tempprary dirty map
            st_sigma = "Estimated from temporary dirty map ch1~cn2"
            im_tmp = 'im.dirty'
            nchan_tmp = 3
            os.system('rm -rf '+im_tmp+'.*')
            tclean(vis         = vislist, 
                   spw         = spw,
                   imagename   = im_tmp, 
                   datacolumn  = datacolumn,
                   savemodel   = 'none',
                   phasecenter = phasecenter,
                   specmode    = 'cube',
                   start       = start,
                   width       = width,
                   restfreq    = restfreq,
                   nchan       = nchan_tmp,
                  restoringbeam = 'common',
                   deconvolver = 'multiscale',
                   scales      = scales, 
                   weighting   ='briggs', 
                   robust      = robust,
                   imsize      = imsize,
                   cell        = cellsize, 
                   niter       = 0,  #dirty
                   interactive = False,
                   threshold   = 1,
                   uvtaper     = uvtaper,
                   uvrange     = '',
                   #usemask     = 'auto-multithresh',
                   parallel    = parallel,
                   startmodel  = '')
            sigma = imstat(imagename=im_tmp+'.image',chans='1~2')['rms'][0] # for sigma
            os.system('rm -rf '+im_tmp+'.*')
         #
         print(' ')
         print('------------         Start New Imaging        ---------------')
         print('imagename = '+imagename  )
         print(' - Robust = '+str(robust)+' uvtaper = '+uvtaper)
         print(f" - Expected sigma = {str(sigma)} Jy/Beam  ({st_sigma})")
         print(f" - cellsize = {cellsize}, imsize = {imsize}, scales = {scales}")
         print(f" - line {line} at SPW = {spw} (Rest Frequency = {str(freq_GHz)+' GHz'})")
         print(f" - width = {width_kms} km/s, start = {start}, nchan = {str(nchan)}")
         print(f"  (data channel width of the MS = {chan_width_Hz} Hz = {chan_width_kms} km/s)")
         #
         ## delte old image data
         os.system('rm -rf '+imagename+'.* tclean.last')
         ## tclean main
         tclean(vis         = vislist, 
                spw         = spw,
                imagename   = imagename, 
                datacolumn  = datacolumn,
                savemodel   = 'none',
                phasecenter = phasecenter,
                specmode    = 'cube',
                start       = start,
                width       = width,
                restfreq    = restfreq,
                nchan       = nchan,
                restoringbeam = 'common',
                deconvolver = 'multiscale',
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
                sidelobethreshold = 2.0,
                noisethreshold    = 4.0,
                lownoisethreshold = 1.5, 
                smoothfactor      = 1.0,
                pbmask      = 0.1,
                pblimit     = 0.1,
                parallel    = parallel,
                startmodel  = '')
         #
         ## Export FITS files (default: image, pbcor image)
         imname    = imagename+'.image'
         pbname    = imagename+'.pb'
         pbcorname = imagename+'.pbcor' # export pbcor image 
         #os.system('rm -rf '+pbcorname+'.*')
         impbcor(imagename=imname,pbimage=pbname,outfile=pbcorname)
         exportfits(imagename=imname,fitsimage=imname+'.fits',overwrite=True,dropdeg=True)
         exportfits(imagename=pbcorname,fitsimage=pbcorname+'.fits',overwrite=True,dropdeg=True)
         #
         ## additional Export FITS files moment maps
         sigma_final = imstat(imagename=imagename+'.image',chans='1~2')['rms'][0] # for mom 1
         im_mom = pbcorname # image name of input immomnet (mom0, mom8)
         # mom 0 map
         immoments(imagename=im_mom,moments=0,outfile=im_mom+'.mom0')
         exportfits(imagename=im_mom+'.mom0',fitsimage=im_mom+'.mom0.fits',overwrite=True,dropdeg=True)
         # mom 8 map
         immoments(imagename=im_mom,moments=8,outfile=im_mom+'.mom8')
         exportfits(imagename=im_mom+'.mom8',fitsimage=im_mom+'.mom8.fits',overwrite=True,dropdeg=True)
         #
         #im_mom = imagename+'.image' # image name of input immomnet (mom1)
         im_mom = pbcorname  # image name of input immomnet (mom1) !!
         # mom 1 maps ( >3 simag ) and export LOG
         immoments(imagename=im_mom,moments=1,includepix=[3*sigma_final,1e5],outfile=im_mom+'.sig3_mom1')
         exportfits(imagename=im_mom+'.sig3_mom1',fitsimage=im_mom+'.sig3_mom1.fits',overwrite=True,dropdeg=True)
         st_log = []
         st_log.append(f"## Moment 1 map including pixels with > 3 sigma")
         st_log.append(f"## sigma (measured in chan 1 ~ 2) = {str(sigma_final)}")
         for item in reversed(st_log): os.system("sed -i '1i "+ item+" ' immoments.last")
         os.system('cp -f immoments.last '+im_mom+'.sig3_mom1'+'_immoments.LOG')

         # mom 1 maps ( >5 simag ) and export LOG
         immoments(imagename=im_mom,moments=1,includepix=[5*sigma_final,1e5],outfile=im_mom+'.sig5_mom1')
         exportfits(imagename=im_mom+'.sig5_mom1',fitsimage=im_mom+'.sig5_mom1.fits',overwrite=True,dropdeg=True)
         st_log = []
         st_log.append(f"## Moment 1 map including pixels with > 5 sigma")
         st_log.append(f"## sigma (measured in chan 1 ~ 2) = {str(sigma_final)}")
         for item in reversed(st_log): os.system("sed -i '1i "+ item+" ' immoments.last")
         os.system('cp -f immoments.last '+im_mom+'.sig5_mom1'+'_immoments.LOG')
         #
         ## Export tclean LOG
         sigma_final = imstat(imagename=imagename+'.image',chans='1~2')['rms'][0] #
         utc_now  = datetime.now(timezone.utc)
         cwd      = os.getcwd()
         ver_line = casalog.version()
         im_final = imagename+'.image'
         bmaj      = imhead(imagename=im_final)['restoringbeam']['major']['value']
         bmaj_unit = imhead(imagename=im_final)['restoringbeam']['major']['unit']
         bmin      = imhead(imagename=im_final)['restoringbeam']['minor']['value']
         bpa       = imhead(imagename=im_final)['restoringbeam']['positionangle']['value']
         bpa_unit  = imhead(imagename=im_final)['restoringbeam']['positionangle']['unit']
         #
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
         st_log.append(f"## - line {line} at SPW = {spw} (Rest Frequency = {str(freq_GHz)+' GHz'})")
         st_log.append(f"## - width = {width_kms} km/s, start = {start}, nchan = {str(nchan)}")
         st_log.append(f"##  (channel width of the SPW = {chan_width_Hz} Hz = {chan_width_kms} km/s)")
         st_log.append(f"## - robust = {robust}, uvtaper = {uvtaper}")
         st_log.append(f"## - cellsize = {cellsize}, imsize = {imsize}, scales = {scales} ")
         st_log.append(f"## - sigma_temporal to determine threshold ({st_sigma}) = {str(sigma)}")
         st_log.append(f"## ")
         st_log.append(f"## Measurements from the Final Image (XX.image) ")
         st_log.append(f"## - Restoring Beam: {bmaj} x {bmin} ({bmaj_unit}) PA = {bpa} {bpa_unit}")
         st_log.append(f"## - sigma_final (Measured in channel 1 ~ 2) = {str(sigma_final)} Jy/Beam")
         st_log.append(f"########################################################")
         st_log.append(f"# ")
         #
         fn_log = imagename+'.tclean.LOG'
         for item in st_log: print(item)
         os.system('cp -f tclean.last '+fn_log)      
         for item in reversed(st_log): os.system("sed -i '1i "+ item+" ' "+fn_log)
         print(" export LOG file: "+fn_log)
         print("------------ finish imaging of "+imagename+" ---------------")

         
###############################################################
################       CLEANUP            #####################
###############################################################
