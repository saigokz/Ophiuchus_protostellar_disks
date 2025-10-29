###
### set directory
###

# output directory. You can change name when you want to keep images with different parameters.
#directory='weblog_CO_channel'
directory='weblog_SO_channel'
#directory='weblog_ALL_channel'
### for test
#directory='weblog_test'

# Continuum directory where you ran the imaging script 
cont_SB_directory  = '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/sb/cont'
cont_LB_directory  = '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/lb/cont'
cont_SBLB_directory= '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/comb/cont'

# Line directory where you ran the imaging script 
line_SB_directory  = '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/sb/line'
line_LB_directory  = '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/lb/line'
line_SBLB_directory= '/almabeegfs/scratch/jhashimoto/alma/oph/2023.1.00545.S/comb/line'

###
### display parameter. Large number results in large zooming-up.
###

zoom_cont = 10
zoom_line = 2

###
### channels used for moment maps
###

### ALL channels
#chans_C18O = ''
#chans_12CO = ''
#chans_13CO = ''
#chans_SO = ''
#chans_H2CO_3_21_2_20_218_76GHz = ''
#chans_SiO = ''
#chans_H2CO_3_03_2_02_218_22GHz = ''
#chans_H2CO_3_22_2_21_218_47GHz = ''
#chans_c_C3H2_217_82 = ''
#chans_cC3H2_217_94 =''
#chans_cC3H2_218_16 =''
#chans_DCN = ''
#chans_CH3OH = ''

### CO
#chans_C18O = '29~44'
#chans_12CO = '156~160'
#chans_13CO = '29~44'
#chans_SO = '29~44'
#chans_H2CO_3_21_2_20_218_76GHz = '7~8'
#chans_SiO = '7~8'
#chans_H2CO_3_03_2_02_218_22GHz = '7~8'
#chans_H2CO_3_22_2_21_218_47GHz = '7~8'
#chans_c_C3H2_217_82 = '7~8'
#chans_cC3H2_217_94 = '7~8'
#chans_cC3H2_218_16 = '7~8'
#chans_DCN = '7~8'
#chans_CH3OH = '7~8'


### SO
chans_C18O = '44~53'
chans_12CO = '161~163'
chans_13CO = '44~53'
chans_SO = '44~53'
chans_H2CO_3_21_2_20_218_76GHz = '9~11'
chans_SiO = '9~11'
chans_H2CO_3_03_2_02_218_22GHz = '9~11'
chans_H2CO_3_22_2_21_218_47GHz = '9~11'
chans_c_C3H2_217_82 = '9~11'
chans_cC3H2_217_94 ='9~11'
chans_cC3H2_218_16 ='9~11'
chans_DCN = '9~11'
chans_CH3OH = '9~11'

### ALL channels
#chans_C18O = ''
#chans_12CO = ''
#chans_13CO = ''
#chans_SO = ''
#chans_H2CO_3_21_2_20_218_76GHz = ''
#chans_SiO = ''
#chans_H2CO_3_03_2_02_218_22GHz = ''
#chans_H2CO_3_22_2_21_218_47GHz = ''
#chans_c_C3H2_217_82 = ''
#chans_cC3H2_217_94 =''
#chans_cC3H2_218_16 =''
#chans_DCN = ''
#chans_CH3OH = ''

################################################################################
################################################################################
################################################################################
##############################  Do not edit below  #############################
################################################################################
################################################################################
################################################################################



###
### imaging parameter for dust continuum
###

cont_robusts = [-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0]
cont_baselines = ['SB','LB','SBLB']
### for test
#cont_robusts = ['2.0']
#cont_baselines = ['SB',]
#cont_baselines = ['SB','LB']
#cont_baselines = ['SB','SBLB']


###
### imaging parameter for lines
###

molecules = ["C18O","12CO","13CO","SO","H2CO_3_21-2_20_218.76GHz","SiO",
             "H2CO_3_03-2_02_218.22GHz","H2CO_3_22-2_21_218.47GHz",
             "c-C3H2_217.82","cC3H2_217.94","cC3H2_218.16","DCN","CH3OH"]
line_robusts   = [-0.5, 0.0, 0.5, 2.0] 
line_baselines = ['SB','LB','SBLB']
moments = ['mom0','mom8','mom1']
##  for test
#molecules = ["C18O","12CO","13CO",]
#line_robusts   = [2.0] 
#line_baselines = ['SB',]
#line_baselines = ['SB','LB']
#line_baselines = ['SB','SBLB']
#moments=['mom0','mom8','mom1']


###
### line-imaging master list
###
image_master_list = {
    ### C18O images
    "C18O":dict(chanstart='-5.5km/s', chanwidth='0.167km/s',
                nchan=120, linefreq='219.56035410GHz', chans=chans_C18O),
    ### 13CO images
    "13CO":dict(chanstart='-5.5km/s', chanwidth='0.1675km/s',
                nchan=120, linefreq='220.39868420GHz', chans=chans_13CO),
    ### 12CO images
    "12CO":dict(chanstart='-100.0km/s', chanwidth='0.635km/s', 
                nchan=315, linefreq='230.538GHz', chans=chans_12CO), 
    ### SO Images
    "SO":dict(chanstart='-5.5km/s', chanwidth='0.167km/s', 
              nchan=120, linefreq='219.94944200GHz', chans=chans_SO), 
    ### H2CO 3(2,1)-2(2,0) Images
    "H2CO_3_21-2_20_218.76GHz":dict(chanstart='-5.5km/s',chanwidth='0.32km/s',
                                    nchan=60, linefreq='218.76006600GHz', chans=chans_H2CO_3_21_2_20_218_76GHz),
    ### H2CO 3(0,3)-2(0,2) Images
    "H2CO_3_03-2_02_218.22GHz":dict(chanstart='-10km/s',chanwidth='1.34km/s',
                                    nchan=23, linefreq='218.22219200GHz', chans=chans_H2CO_3_03_2_02_218_22GHz),
    ### H2CO 3(2,2)-2(2,1) Images
    "H2CO_3_22-2_21_218.47GHz":dict(chanstart='-10km/s',chanwidth='1.34km/s', 
                                    nchan=23, linefreq='218.47563200GHz', chans=chans_H2CO_3_22_2_21_218_47GHz),
    ### c-C3H2 217.82 GHz Images
    "c-C3H2_217.82":dict(chanstart='-10km/s', chanwidth='1.34km/s',
                         nchan=23, linefreq='217.82215GHz', chans=chans_c_C3H2_217_82),
    ### c-C3H2 217.94 GHz Images
    "cC3H2_217.94":dict(chanstart='-10km/s', chanwidth='1.34km/s', 
                        nchan=23, linefreq='217.94005GHz', chans=chans_cC3H2_217_94),
    ### c-C3H2 218.16 GHz Images
    "cC3H2_218.16":dict(chanstart='-10km/s', chanwidth='1.34km/s', 
                        nchan=23, linefreq='218.16044GHz', chans=chans_cC3H2_218_16),
    ### DCN Images
    "DCN":dict(chanstart='-10km/s', chanwidth='1.34km/s',
               nchan=23, linefreq='217.2386GHz', chans=chans_DCN),     
    ### CH3OH Images
    "CH3OH":dict(chanstart='-10km/s', chanwidth='1.34km/s',
                 nchan=23, linefreq='218.44006300GHz', chans=chans_CH3OH),
    ### SiO Images
    "SiO":dict(chanstart='-100km/s', chanwidth='1.34km/s', nchan=150, 
               linefreq='217.10498000GHz', chans=chans_SiO),     
}
