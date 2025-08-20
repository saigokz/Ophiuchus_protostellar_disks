Ophiuchus Protostellar Disk Survey Imaging Scripts
This is the default set of imaging scripts for the Ophiuchus protostellar disk survey (2023.1.00545.S).
As a post-processing step of auto-selfcal (https://github.com/jjtobin/auto_selfcal), it enables splitting of continuum MS (with line channels flagged), and performing continuum and line imaging.
By adjusting the script settings, it can be applied to any project.
After the series of processes in auto-selfcal is completed, the CORRECTED column in *_targets.ms within the Work directory contains the self-calibrated data, and the continuum-subtracted MS data *_targets.contsub.ms is generated.
In addition, the cont.dat file used for these processes should also be present.
Imaging Procedure
Download imaging scripts
Clone the repository or download the ZIP file:
git clone https://github.com/saigokz/Ophiuchus_protostellar_disks
Copy scripts into the Work directory
Move into the Work directory and copy all *.py files from the Ophiuchus_protostellar_disks directory.
Create continuum MS
Run in CASA (version 6.5.2 or later):
execfile('make_contMS.py')
This generates *_targets.ms.ave.cont, in which spectral line channel ranges are flagged and the channels are averaged to a width of 10 kHz.
This script reads the cont.dat file.
Continuum imaging
Imaging with robust = ?2.0, ?1.0, ?0.5, 0.0, 0.5, 1.0, 2.0. Example:
execfile('Oph_continuum_LB.v5.py')
When running SB (Short Baseline data, i.e., TM2) or LB (Long Baseline data, i.e., TM1) in the Work directory, simply execute the corresponding script (e.g., Oph_continuum_SB.v5.py for SB, Oph_continuum_LB.v5.py for LB).
For SBLB, edit the Setting section in the script to specify the path to the data directory.
Line imaging
Imaging of C18O, 12CO, etc. with robust = ?0.5, 0.0, 0.5, 2.0 (without uvtaper). Example:
execfile('Oph_spectral_lines_LB.v5.py')
When running SB (Short Baseline data, i.e., TM2) or LB (Long Baseline data, i.e., TM1) in the Work directory, simply execute the corresponding script (e.g., Oph_spectral_lines_SB.v5.py for SB, Oph_spectral_lines_LB.v5.py for LB).
For SBLB, edit the Setting section in the script to specify the path to the data directory.
