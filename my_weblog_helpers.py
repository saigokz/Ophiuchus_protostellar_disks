### Update information
###
### 2025.Oct.08 Compatible with the Clean up script. 
### 2025.Oct.03 Addining parameters to select channels for moment 0, 1, 8 maps.
### 2025.Sep.19 Addining parameters to select channels for moment 1 maps.
###


import numpy as np
import numpy 
import scipy.stats
import scipy.signal
import math
import os

import casatools
from casaplotms import plotms
from casatasks import *
from casatools import image, imager
from casatools import msmetadata as msmdtool
from casatools import table as tbtool
from casatools import ms as mstool
from PIL import Image

ms = mstool()
tb = tbtool()
msmd = msmdtool()
ia = image()
im = imager()


    

def plot_image(filename,contname,outname,min_val=None,max_val=None,zoom=2,contour='mask', stddev=-1):
   import matplotlib
   matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   header=imhead(filename)
   '''
   tb.open(filename)
   image_data=np.rot90(tb.getcol('map').squeeze())   # rotate the image 90 degrees and get rid of degenerate axes
   tb.close()
   tb.open(contname)
   continuum_data=np.rot90(tb.getcol('map').squeeze())   # rotate the image 90 degrees and get rid of degenerate axes
   tb.close()
   '''
   
   ia.open(filename)
   image_data = np.rot90(ia.getchunk())
   ia.close()
   #print(filename,image_data.shape)

   ia.open(contname)
   continuum_data = np.rot90(ia.getchunk())
   ia.close()
   #print(contname,continuum_data.shape)
   
   size=np.max(header['shape'])
   cell=header['incr'][1]*3600.0*180.0/3.14159        #get pixel size from header declination direction
   halfsize_arcsec=size/zoom/2.0*cell
   fig=plt.figure(figsize=(10,8))
   ax=fig.add_subplot(1,1,1)

   ll=int(size/2.-size/(zoom*2))
   ul=int(size/2.+size/(zoom*2))

   #print(contname,halfsize_arcsec,ll,ul)

   if contour=='mask':
      '''
      tb.open(filename.replace('pbcor.tt0','mask'))
      #print(filename)
      #print(filename.replace('pbcor.tt0','mask'))
      mask_data=np.flipud(np.rot90(tb.getcol('map').squeeze()))   # rotate the image 90 degrees and get rid of degenerate axes
                                                                  #extra flip is needed for the mask data for some reason to match the casaviewer view
      tb.close()
      '''
      ia.open(filename.replace('pbcor.tt0','mask'))
      mask_data = np.flipud(np.rot90(ia.getchunk()))
      ia.close()
      #print(filename.replace('pbcor.tt0','mask'),mask_data.shape)
      
      img=ax.imshow(image_data[ll:ul,ll:ul],extent=[halfsize_arcsec,-halfsize_arcsec,-halfsize_arcsec,halfsize_arcsec],vmin=min_val,vmax=max_val)
      conts=ax.contour(mask_data[ll:ul,ll:ul],levels=[0.5], colors='white', extent=[halfsize_arcsec,-halfsize_arcsec,-halfsize_arcsec,halfsize_arcsec])

   if contour=='contour':
      #print(ll,ul,halfsize_arcsec)
      img=ax.imshow(image_data[ll:ul,ll:ul],extent=[halfsize_arcsec,-halfsize_arcsec,-halfsize_arcsec,halfsize_arcsec],vmin=min_val,vmax=max_val)      
      conts=ax.contour(np.flip(continuum_data[ll:ul,ll:ul],0),levels=[3*stddev,10*stddev,30*stddev], colors='white', extent=[halfsize_arcsec,-halfsize_arcsec,-halfsize_arcsec,halfsize_arcsec])

   if contour=='dust_contour':
      #print(filename,halfsize_arcsec)
      img=ax.imshow(image_data[ll:ul,ll:ul],extent=[halfsize_arcsec,-halfsize_arcsec,-halfsize_arcsec,halfsize_arcsec],vmin=min_val,vmax=max_val)
      if '_SB_continuum_' in contname:
         conts=ax.contour(np.flip(continuum_data[256:384,256:384],0),levels=[3*stddev,10*stddev,30*stddev], colors='white', extent=[5.12,-5.12,-5.12,5.12])
      else:
         conts=ax.contour(np.flip(continuum_data[1000:1500,1000:1500],0),levels=[3*stddev,10*stddev,30*stddev], colors='white', extent=[5.00,-5.00,-5.00,5.00])
   
   ax.set_xlabel('Offset (arcsec)',fontsize=18)
   ax.set_ylabel('Offset (arcsec)',fontsize=18)
   ax.tick_params(axis='both', which='major', labelsize=16)
   cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
   cbar=plt.colorbar(img,cax=cax)
   cbar.ax.tick_params(labelsize=16)
   if 'mom0' in filename:
      cbar.set_label('Intensity (mJy/beam*km/s)')
   elif 'sig3' in filename or 'sig5' in filename :
      cbar.set_label('Velocity (km/s)')
   else:
      cbar.set_label('Intensity (mJy/beam)')
   plt.savefig(outname,dpi=300.0)
   plt.close()


def render_summary_table(image_master_list,htmlOut,target,baselines,robust,directory,intflux,intflux_e,rms,beammajor,beamminor,beampa,peak,molecule,moment):


   if moment == 'tt0':
      cont_or_gas = 'Dust continuum'
   else:
      cont_or_gas = molecule
   
   # SUMMARY TABLE FOR FINAL IMAGES
   htmlOut.writelines('<table cellspacing="0" cellpadding="0" border="0" bgcolor="#000000">\n')
   htmlOut.writelines('	<tr>\n')
   htmlOut.writelines('		<td>\n')
   line='<table>\n  <tr bgcolor="#ffffff">\n    <th>Data:</th>\n    '
   for baseline in baselines:
      line+='<th>'+cont_or_gas+' '+baseline+' robust '+str(robust)+'</th>\n    '
   line+='</tr>\n'
   htmlOut.writelines(line)
    
   quantities=['Image','Image+mask','Image+contour','sig3','sig5','intflux','Flux SNR','Peak','Peak SNR','RMS','Beam']
   for key in quantities:
      if moment == 'tt0':
         if key =='Image':
            line=''
         if key =='Image+mask':
            line='<tr bgcolor="#ffffff">\n    <td>Image+mask: </td>\n'
         if key =='Image+contour':
            line='<tr bgcolor="#ffffff">\n    <td>Image+contour<br>(3,10,30 sigma):</td>\n'
         if key =='Flux SNR':
            line='<tr bgcolor="#ffffff">\n    <td>Int.Flux SNR: </td>\n'
         if key =='intflux':
            line='<tr bgcolor="#ffffff">\n    <td>Integrated Flux: </td>\n'
         if key =='RMS':
            line='<tr bgcolor="#ffffff">\n    <td>RMS: </td>\n'
         if key =='Beam':
            line='<tr bgcolor="#ffffff">\n    <td>Beam: </td>\n'
         if key =='Peak':
            line='<tr bgcolor="#ffffff">\n    <td>Peak: </td>\n'
         if key =='Peak SNR':
            line='<tr bgcolor="#ffffff">\n    <td>Peak SNR: </td>\n'
         if key =='sig3':
            line=''
         if key =='sig5':
            line=''
      if moment == 'mom0':
         if key =='Image':
            line='<tr bgcolor="#ffffff">\n    <td>Mom.0 image +<br>  dust contour<br>(3,10,30 sigma): </td>\n'
         if key =='Image+mask':
            line=''
         if key =='Image+contour':
            line=''
         if key =='Flux SNR':
            line=''
         if key =='intflux':
            line=''
         if key =='RMS':
            line='<tr bgcolor="#ffffff">\n    <td>RMS: </td>\n'
         if key =='Beam':
            line='<tr bgcolor="#ffffff">\n    <td>Beam: </td>\n'
         if key =='Peak':
            line='<tr bgcolor="#ffffff">\n    <td>Peak: </td>\n'
         if key =='Peak SNR':
            line='<tr bgcolor="#ffffff">\n    <td>Peak SNR: </td>\n'
         if key =='sig3':
            line=''
         if key =='sig5':
            line=''
      if moment == 'mom8':
         if key =='Image':
            line='<tr bgcolor="#ffffff">\n    <td>Mom.8 image +<br>  dust contour<br>(3,10,30 sigma): </td>\n'
         if key =='Image+mask':
            line=''
         if key =='Image+contour':
            line=''
         if key =='Flux SNR':
            line=''
         if key =='intflux':
            line=''
         if key =='RMS':
            line='<tr bgcolor="#ffffff">\n    <td>RMS: </td>\n'
         if key =='Peak SNR':
            line='<tr bgcolor="#ffffff">\n    <td>Peak SNR: </td>\n'
         if key =='Beam':
            line='<tr bgcolor="#ffffff">\n    <td>Beam: </td>\n'
         if key =='Peak':
            line='<tr bgcolor="#ffffff">\n    <td>Peak: </td>\n'
         if key =='sig3':
            line=''
         if key =='sig5':
            line=''
      if moment == 'mom1':
         if key =='Image':
            line=''
         if key =='Image+mask':
            line=''
         if key =='Image+contour':
            line=''
         if key =='Flux SNR':
            line=''
         if key =='intflux':
            line=''
         if key =='RMS':
            line=''
         if key =='Peak SNR':
            line=''
         if key =='Beam':
            line='<tr bgcolor="#ffffff">\n    <td>Beam: </td>\n'
         if key =='Peak':
            line=''
         if key =='sig3':
            line='<tr bgcolor="#ffffff">\n    <td>Mom1. sig3 +<br>  dust contour<br>(3,10,30 sigma): </td>\n'
         if key =='sig5':
            line='<tr bgcolor="#ffffff">\n    <td>Mom1. sig5 +<br>  dust contour<br>(3,10,30 sigma): </td>\n'

      for baseline in baselines:
         if moment == 'tt0':
            if key =='Image+mask':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.mask.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.mask.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            #print('images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png')
            if key =='Image+contour':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.contour.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.contour.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            #print('images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png')
            if key =='Flux SNR':
               line+='    <td>{:0.3f} </td>\n'.format(intflux[baseline+str(robust)+molecule+moment]/intflux_e[baseline+str(robust)+molecule+moment])
            if key =='intflux':
               line+='    <td>{:0.3f} +/- {:0.3f} mJy</td>\n'.format(intflux[baseline+str(robust)+molecule+moment]*1e3,intflux_e[baseline+str(robust)+molecule+moment]*1e3)
            if key =='Peak SNR':
               line+='    <td>{:0.3f} </td>\n'.format(peak[baseline+str(robust)+molecule+moment]/rms[baseline+str(robust)+molecule+moment])
            if key =='Peak':
               line+='    <td>{:0.3f} +/- {:0.3f} mJy/beam</td>\n'.format(peak[baseline+str(robust)+molecule+moment]*1e3,rms[baseline+str(robust)+molecule+moment]*1e3)
            if key =='RMS':
               line+='    <td>{:0.3f} mJy/beam </td>\n'.format(rms[baseline+str(robust)+molecule+moment]*1e3)
            if key =='Beam':
               line+='    <td>{:0.3f}"x{:0.3f}" at {:0.3f} deg </td>\n'.format(beammajor[baseline+str(robust)+molecule+moment],beamminor[baseline+str(robust)+molecule+moment],beampa[baseline+str(robust)+molecule+moment])
         if moment == 'mom0':
            if key =='Image':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            #print('images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png')
            if key =='Peak SNR':
               line+='    <td>{:0.3f} </td>\n'.format(peak[baseline+str(robust)+molecule+moment]/(rms[baseline+str(robust)+molecule+moment]*math.sqrt(image_master_list[molecule]['nchan'])*(float(image_master_list[molecule]['chanwidth'].replace('km/s','')))))
            if key =='Peak':
               line+='    <td>{:0.3f} +/- {:0.3f} mJy/beam*km/s</td>\n'.format(peak[baseline+str(robust)+molecule+moment]*1e3,rms[baseline+str(robust)+molecule+moment]*1e3*math.sqrt(image_master_list[molecule]['nchan'])*float(image_master_list[molecule]['chanwidth'].replace('km/s','')))
            if key =='RMS':
               line+='    <td>{:0.3f} mJy/beam*km/s </td>\n'.format(rms[baseline+str(robust)+molecule+moment]*1e3*math.sqrt(image_master_list[molecule]['nchan'])*float(image_master_list[molecule]['chanwidth'].replace('km/s','')))
            if key =='Beam':
               line+='    <td>{:0.3f}"x{:0.3f}" at {:0.3f} deg </td>\n'.format(beammajor[baseline+str(robust)+molecule+moment],beamminor[baseline+str(robust)+molecule+moment],beampa[baseline+str(robust)+molecule+moment])
         if moment == 'mom8':
            if key =='Image':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            #print('images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.'+moment+'.png')
            if key =='Peak':
               line+='    <td>{:0.3f} +/- {:0.3f} mJy/beam</td>\n'.format(peak[baseline+str(robust)+molecule+moment]*1e3,rms[baseline+str(robust)+molecule+moment]*1e3)
            if key =='Peak SNR':
               line+='    <td>{:0.3f} </td>\n'.format(peak[baseline+str(robust)+molecule+moment]/rms[baseline+str(robust)+molecule+moment])
            if key =='RMS':
               line+='    <td>{:0.3f} mJy/beam</td>\n'.format(rms[baseline+str(robust)+molecule+moment]*1e3)
            if key =='Beam':
               line+='    <td>{:0.3f}"x{:0.3f}" at {:0.3f} deg </td>\n'.format(beammajor[baseline+str(robust)+molecule+moment],beamminor[baseline+str(robust)+molecule+moment],beampa[baseline+str(robust)+molecule+moment])
         if moment == 'mom1':
            if key =='sig3':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig3.'+moment+'.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig3.'+moment+'.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            if key =='sig5':
               line+='<td><a href="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig5.'+moment+'.png"><img src="images/'+target+'_'+baseline+'_'+molecule+'_robust_'+str(robust)+'.pbcor.sig5.'+moment+'.png" ALT="'+baseline+' robust '+str(robust)+' image" WIDTH=500 HEIGHT=400></a> </td>\n'
            if key =='Beam':
               line+='    <td>{:0.3f}"x{:0.3f}" at {:0.3f} deg </td>\n'.format(beammajor[baseline+str(robust)+molecule+moment],beamminor[baseline+str(robust)+molecule+moment],beampa[baseline+str(robust)+molecule+moment])
      line+='</tr>\n'
      #print(line)
      htmlOut.writelines(line)
   htmlOut.writelines('</table>\n')
   htmlOut.writelines('	</td>\n')
   htmlOut.writelines('	</tr>\n')
   htmlOut.writelines('</table>\n')
