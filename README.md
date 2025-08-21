## Ophiuchus Protostellar Disk Survey Imaging Scripts
This is the default set of imaging scripts for the Ophiuchus protostellar disk survey project, 2023.1.00545.S.
As a post-processing step of auto-selfcal (https://github.com/jjtobin/auto_selfcal), it split continuum MS (with line channels flagged), and performing continuum and line imagings. By adjusting the script settings, it can be applied to any project.

After the series of processes in auto-selfcal is completed, in the Work directory, apart from the self-calibration scripts and log files, the following should be present. These serve as the starting point for imaging.
- *_targets.ms (self-calibrated data stored in the CORRECTED column)
- *_targets.contsub.ms (the continuum-subtracted MS data)
- cont.dat　

## Imaging Procedure
1. Download this imaging scripts: git clone https://github.com/saigokz/Ophiuchus_protostellar_disks    or download ZIP file from this page
2. Move into the Work directory and copy all *.py files to the Work directory from the Ophiuchus_protostellar_disks directory.
3. Preparation of continuum imaging: execfile('make_contMS.py')  in CASA (version 6.5.2 or later)
- This generates *_targets.ms.ave.cont, in which spectral line channel ranges are flagged and the channels are averaged to a width of 10 kHz.
- This script reads the cont.dat file.
5. Continuum imaging: [Example] execfile('Oph_continuum_LB.v5.py')  in CASA (version 6.5.2 or later)
- When running SB (Short Baseline data, i.e., TM2) or LB (Long Baseline data, i.e., TM1) in the Work directory, simply execute the corresponding script (e.g., Oph_continuum_SB.v5.py for SB, Oph_continuum_LB.v5.py for LB). For SBLB, please edit the Setting section in the script before execution to specify the path to the data directory.
- By default: with robust = -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0,  without uvtaper
- If you wish to run parallel processing, edit the script and set parallel=True. The default value is False
6. Line imaging [Example] execfile('Oph_spectral_lines_LB.v5.py')  in CASA (version 6.5.2 or later)
- When running SB (Short Baseline data, i.e., TM2) or LB (Long Baseline data, i.e., TM1) in the Work directory, simply execute the corresponding script (e.g., Oph_spectral_lines_SB.v5.py for SB, Oph_spectral_lines_LB.v5.py for LB). For SBLB, please edit the Setting section in the script  before execution to specify the path to the data directory.
- By default: C18O(2-1), 13CO(2-1), 12CO(2-1), SiO, SO, H2CO,etc. with robust = -0.5, 0.0, 0.5, 2.0, without uvtaper
- If you wish to run parallel processing, edit the script and set parallel=True. The default value is False

