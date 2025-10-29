import numpy as np
import numpy 
import scipy.stats
import scipy.signal
import math
import os
import glob
import sys

import casatools
from casaplotms import plotms
from casatasks import *
from casatools import image, imager
from casatools import msmetadata as msmdtool
from casatools import table as tbtool
from casatools import ms as mstool
from casaviewer import imview
from PIL import Image


ms = mstool()
tb = tbtool()
msmd = msmdtool()
ia = image()
im = imager()

sys.path.append("./")
from my_weblog_helpers import *
from my_config import *

###
###
###

beammajor = {}
beamminor = {}
beampa    = {}
rms       = {}
intflux   = {}
intflux_e = {}
peak      = {}

###
### get object name
###

object_list = glob.glob(cont_SB_directory+'/*.pbcor.tt0.fits')
header_list = imhead(object_list[0], mode='list') 
#print(header_list)
object_name = header_list['object']

###
###
###



from datetime import datetime
os.system('rm -rf '+directory)
os.system('mkdir '+directory)
os.system('mkdir '+directory+'/images')
htmlOut=open(directory+'/index.html','w')
htmlOut.writelines('<html>\n')
htmlOut.writelines('<title>Imaging Weblog</title>\n')
htmlOut.writelines('<head>\n')
htmlOut.writelines('</head>\n')
htmlOut.writelines('<body>\n')
htmlOut.writelines('<a name="top"></a>\n')
htmlOut.writelines('<h1>Imaging Weblog</h1>\n')
htmlOut.writelines('<h4>Weblog creation: '+datetime.today().strftime('%Y-%m-%d')+'</h4>\n')
htmlOut.writelines('<a href="continuum.html">Dust continuum images</a>\n')
htmlOut.writelines('<a href="mom0.html">Moment 0 images</a>\n')
htmlOut.writelines('<a href="mom8.html">Moment 8 images</a>\n')
htmlOut.writelines('<a href="mom1.html">Moment 1 images</a>\n')

# Close main weblog file
htmlOut.writelines('</body>\n')
htmlOut.writelines('</html>\n')
htmlOut.close()


htmlOut=open(directory+'/continuum.html','w')
htmlOut.writelines('<html>\n')
htmlOut.writelines('<title>Dust continuum</title>\n')
htmlOut.writelines('<head>\n')
htmlOut.writelines('</head>\n')
htmlOut.writelines('<body>\n')
target=object_name
htmlOut.writelines('<a name="'+target+'"></a>\n')
htmlOut.writelines('<h2>'+target+' Dust Continuum Summary</h2>\n')

###
###
###
print('')
print('Making continuum png files...')

molecule='continuum'
moment='tt0'
for baseline in cont_baselines:
    for robust in cont_robusts:
        if baseline == 'SB':
            baseline_directory = cont_SB_directory
        if baseline == 'LB':
            baseline_directory = cont_LB_directory
        if baseline == 'SBLB':
            baseline_directory = cont_SBLB_directory

        ###
        ### image statistics
        ### 
        #print(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0')
        
        image_stats=imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits')
        
        ###
        ### beam shape
        ###

        header_list = imhead(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits', mode='list') 
        #print(header_list)
        beammajor[baseline+str(robust)+molecule+moment] = header_list['beammajor']['value']
        beamminor[baseline+str(robust)+molecule+moment] = header_list['beamminor']['value']
        beampa[baseline+str(robust)+molecule+moment]    = header_list['beampa']['value']
        cell                            = header_list['cdelt2']*180.0/3.14159*3600.0
        beamarea                        = 3.14159*beammajor[baseline+str(robust)+molecule+moment]*beamminor[baseline+str(robust)+molecule+moment]/(4.0*np.log(2.0))
        pix_per_beam                    = beamarea/(cell**2)
        
        ###
        ### RMS
        ###

        im_mask                   = baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.mask.fits'
        rms[baseline+str(robust)+molecule+moment] = imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.image.tt0.fits',\
                                                           mask=f'"{im_mask}" == 0')['rms'][0]
        #print(imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.image.tt0'))
        #print(im_mask,rms)
        
        ###
        ### integrated flux
        ###

        intflux[baseline+str(robust)+molecule+moment] = imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                                                               mask=f'"{im_mask}" == 1')['flux'][0]
        npts                          = imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                                               mask=f'"{im_mask}" == 1')['npts'][0]
        n_beams                       = npts/pix_per_beam
        intflux_e[baseline+str(robust)+molecule+moment] =  (n_beams)**0.5*rms[baseline+str(robust)+molecule+moment]
        
        #print(baseline+str(robust),intflux[baseline+str(robust)],intflux_e[baseline+str(robust)],n_beams,pix_per_beam,npts)

        ###
        ### Peak intensity
        ###

        peak[baseline+str(robust)+molecule+moment] = imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                                                            mask=f'"{im_mask}" == 1')['max'][0]

        ###
        ### create png file
        ###
        plot_image(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                   baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                   directory+'/images/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.mask.png',\
                   min_val=0.0,max_val=image_stats['max'][0],\
                   contour='mask', \
                   zoom=zoom_cont,)
        
        plot_image(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                   baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                   directory+'/images/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.contour.png',\
                   min_val=0.0,max_val=image_stats['max'][0],\
                   contour='contour', stddev=rms[baseline+str(robust)+molecule+moment],\
                   zoom=zoom_cont,)


for robust in cont_robusts:
    render_summary_table(image_master_list,htmlOut,target,cont_baselines,robust,directory,intflux,intflux_e,rms,beammajor,beamminor,beampa,peak,molecule,moment,)

# Close main weblog file
htmlOut.writelines('</body>\n')
htmlOut.writelines('</html>\n')
htmlOut.close()

    
###
### line
###
for moment in moments:
    print('')
    print('Making '+moment+' png files...')
       
    for molecule in molecules:
         for baseline in line_baselines:
            for robust in line_robusts:
                if baseline == 'SB':
                    baseline_directory = line_SB_directory
                    cont_bl_directory  = cont_SB_directory
                if baseline == 'LB':
                    baseline_directory = line_LB_directory
                    cont_bl_directory  = cont_LB_directory
                if baseline == 'SBLB':
                    baseline_directory = line_SBLB_directory
                    cont_bl_directory  = cont_SBLB_directory
                    
                #print(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0')

                ###
                ### RMS
                ###

                logfile=glob.glob(baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.*.sig?_mom1_immoments.LOG')
                #print(logfile)
                with open(logfile[0], "r") as f:
                    entirefile=f.readlines()
                linestr=entirefile[1].split(" ")
                
                rms[baseline+str(robust)+molecule+moment] = float(linestr[9])
                #print(molecule,rms[baseline+str(robust)])
                #print(imstat(baseline_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.image.tt0'))
                #print(im_mask,rms)
                
                if moment == 'mom1':
                    ###
                    ### sig3
                    ###
                    # moment map to measure the max value
                    imagename=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image'
                    os.system('rm -rf '+imagename+'.sig3_mom1')
                    print('Making '    +imagename+'.sig3_mom1')
                    immoments(imagename=imagename+'.fits',moments=int(moment[3]),includepix=[3*rms[baseline+str(robust)+molecule+moment],1e5],chans=image_master_list[molecule]['chans'],outfile=imagename+'.sig3_mom1')
                    exportfits(imagename=imagename+'.sig3_'+moment,fitsimage=imagename+'.sig3_'+moment+'.fits',overwrite=True,dropdeg=True)
                    os.system('rm -rf ' +imagename+'.sig3_'+moment)
                    #print('rms: '+str(rms[baseline+str(robust)+molecule+moment]))
                    imgfile=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image.sig3_'+moment+'.fits'
                    image_stats=imstat(imgfile)
                    #print(imgfile[0],image_stats['min'][0],image_stats['max'][0])
                    if len(image_stats['min']) == 0:
                        min_val=0.0
                        max_val=1.0
                    else:
                        min_val=image_stats['min'][0]
                        max_val=image_stats['max'][0]
                    plot_image(imgfile,\
                               cont_bl_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                               directory+'/images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig3.'+moment+'.png',\
                               min_val=min_val,max_val=max_val,\
                               contour='dust_contour', stddev=rms[baseline+str(robust)+'continuumtt0'],\
                               zoom=zoom_line,)
                    ###
                    ### sig5
                    ###
                    # moment map to measure the max value
                    imagename=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image'
                    os.system('rm -rf '+imagename+'.sig5_mom1')
                    print('Making '+imagename+'.sig5_mom1')
                    immoments(imagename=imagename+'.fits',moments=int(moment[3]),includepix=[5*rms[baseline+str(robust)+molecule+moment],1e5],chans=image_master_list[molecule]['chans'],outfile=imagename+'.sig5_mom1')
                    exportfits(imagename=imagename+'.sig5_'+moment,fitsimage=imagename+'.sig5_'+moment+'.fits',overwrite=True,dropdeg=True)
                    os.system('rm -rf '+imagename+'.sig5_'+moment)
                    imgfile=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image.sig5_'+moment+'.fits'
                    image_stats=imstat(imgfile)
                    #print(imgfile[0])
                    #print(len(image_stats['min']),len(image_stats['max']))
                    #print(image_stats['min'][0],image_stats['max'][0])
                    if len(image_stats['min']) == 0:
                        min_val=0.0
                        max_val=0.0
                    else:
                        min_val=image_stats['min'][0]
                        max_val=image_stats['max'][0]
                    plot_image(imgfile,\
                               cont_bl_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                               directory+'/images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig5.'+moment+'.png',\
                               min_val=min_val,max_val=max_val,\
                               contour='dust_contour', stddev=rms[baseline+str(robust)+'continuumtt0'],\
                               zoom=zoom_line,)

                    header_list = imhead(imgfile, mode='list') 
                else:
                    # .image moment map to measure the max value
                    imagename=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image'
                    os.system('rm -rf '+imagename+'.'+moment+'*')
                    print('Making '+imagename+'.'+moment)
                    immoments(imagename=imagename+'.fits',moments=int(moment[3]), chans=image_master_list[molecule]['chans'], outfile=imagename+'.'+moment)
                    exportfits(imagename=imagename+'.'+moment,fitsimage=imagename+'.'+moment+'.fits',overwrite=True,dropdeg=True)
                    os.system('rm -rf '+imagename+'.'+moment)
                    image_stats=imstat(baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image.'+moment+'.fits')
                    #os.system('rm -rf ' + baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.image.'+moment+'.fits')
                    
                    # .pbcor moment map for creating png file
                    imagename=baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor'
                    os.system('rm -rf '+imagename+'.'+moment)
                    print('Making '+imagename+'.'+moment)
                    immoments(imagename=imagename+'.fits',moments=int(moment[3]), chans=image_master_list[molecule]['chans'], outfile=imagename+'.'+moment)
                    exportfits(imagename=imagename+'.'+moment,fitsimage=imagename+'.'+moment+'.fits',overwrite=True,dropdeg=True)
                    os.system('rm -rf '+imagename+'.'+moment)
                    
                    plot_image(baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.fits',\
                               cont_bl_directory+'/'+target+'_'+baseline+'_continuum_robust_'+str(robust)+'.pbcor.tt0.fits',\
                               directory+'/images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png',\
                               min_val=0.0,max_val=image_stats['max'][0],\
                               contour='dust_contour', stddev=rms[baseline+str(robust)+'continuumtt0'],\
                               zoom=zoom_line,)
                    

                    
                    header_list = imhead(baseline_directory+'/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.fits', mode='list') 
                    os.system('rm -rf '+imagename+'.'+moment)
                    
                    ###
                    ### Peak intensity
                    ###

                    peak[baseline+str(robust)+molecule+moment] = image_stats['max'][0]
                    
                ###
                ### beam shape
                ###
                
                #print(header_list)
                beammajor[baseline+str(robust)+molecule+moment] = header_list['beammajor']['value']
                beamminor[baseline+str(robust)+molecule+moment] = header_list['beamminor']['value']
                beampa[baseline+str(robust)+molecule+moment]    = header_list['beampa']['value']
                cell                            = header_list['cdelt2']*180.0/3.14159*3600.0
                beamarea                        = 3.14159*beammajor[baseline+str(robust)+molecule+moment]*beamminor[baseline+str(robust)+molecule+moment]/(4.0*np.log(2.0))
                pix_per_beam                    = beamarea/(cell**2)

for moment in moments:
    htmlOut=open(directory+'/'+moment+'.html','w')
    htmlOut.writelines('<html>\n')
    if moment == 'mom0':
        htmlOut.writelines('<title>Moment 0 images</title>\n')
    if moment == 'mom8':
        htmlOut.writelines('<title>Moment 8 images</title>\n')
    if moment == 'mom1':
        htmlOut.writelines('<title>Moment 1 images</title>\n')
    htmlOut.writelines('<head>\n')
    htmlOut.writelines('</head>\n')
    htmlOut.writelines('<body>\n')
    target=object_name
    htmlOut.writelines('<a name="'+target+'"></a>\n')
    if moment == 'mom0':
        htmlOut.writelines('<h2>'+target+' Moment 0 Summary</h2>\n')
    if moment == 'mom8':
        htmlOut.writelines('<h2>'+target+' Moment 8 Summary</h2>\n')
    if moment == 'mom1':
        htmlOut.writelines('<h2>'+target+' Moment 1 Summary</h2>\n')
 
    if moment == 'mom0':
        moment_name ='Moment 0'
    if moment == 'mom8':
        moment_name ='Moment 8'
    if moment == 'mom1':
        moment_name ='Moment 1'
        
    for molecule in molecules:
        target=object_name
        htmlOut.writelines('<h2>'+target+' '+molecule+' '+moment_name+' Summary</h2>\n')

        for robust in line_robusts:
            render_summary_table(image_master_list,htmlOut,target,line_baselines,robust,directory,intflux,intflux_e,rms,beammajor,beamminor,beampa,peak,molecule,moment)

    # Close main weblog file
    htmlOut.writelines('</body>\n')
    htmlOut.writelines('</html>\n')
    htmlOut.close()

print('')
print('All done !!')
