## Split & Concat v1 K. Saigo 2025/07/12
## Split & Concat v2 K. Saigo 2025/07/19 for Tobin's Auto-Selfcal
## Split & Concat v3 K. Saigo 2025/08/21 minor updata about option 
##
import os
import pprint
import datetime
from casatools import msmetadata
from casatools import table

## 1.  setting 1
data_select = 'SB'
#data_select = 'LB'
#data_select = '7M'
#data_select = 'TM'

dir_SB      = './'
dir_LB      = './'
#dir_TM      = './'
#dir_7M      = './'
 
search_word = '_targets.ms'   #ex. uid___A002_X11c9ad1_X763f_targets.ms
split_column  = 'corrected' #  split datacolumn
#search_word = '.ms.split.cal'   #
#split_column  = 'data' #  split datacolumn

output_log  = 'Targets_Split.Log'


### Step 1 Collect info. of all EBs and create the database, data_all ###
## select data
dir = './'
dir_org = os.getcwd()
if data_select == 'SB' :dir = dir_org+'/'+dir_SB
if data_select == 'LB' :dir = dir_org+'/'+dir_LB
if data_select == 'TM' :dir = dir_org+'/'+dir_TM
if data_select == '7M' :dir = dir_org+'/'+dir_7M

## make a MS names list
ms_list = sorted([name for name in os.listdir(dir)
    if name.endswith(search_word) and os.path.isdir(os.path.join(dir, name))
])

## make a data list (data_all)
data_all={}
MJD_epoch = 40587.0  # MJD corresponding to 1970-01-01
FieldName = ms_list[0]
for i, vis in enumerate(ms_list):
    vis_in = dir+'/'+vis
    key = data_select + str(i+1)
    if os.path.exists(vis_in):
        MJD0 = listobs(vis=vis_in)['BeginTime']
        MJD1 = listobs(vis=vis_in)['EndTime']
        unix_time = (MJD0 - MJD_epoch) * 86400.0
        Time0 = datetime.datetime.utcfromtimestamp(unix_time)
        Time0_yyyymmdd = Time0.strftime('%Y/%m/%d/%H:%M:%S')
        unix_time = (MJD1 - MJD_epoch) * 86400.0
        Time1 = datetime.datetime.utcfromtimestamp(unix_time)
        Time1_yyyymmdd = Time1.strftime('%Y/%m/%d/%H:%M:%S')
        print(key +f' {vis} obs = '+Time0_yyyymmdd + '~' + Time1_yyyymmdd)
        #
        # get MS info I (field,spw)
        msmd.open(vis_in)
        sci_field_ids = msmd.fieldsforintent('OBSERVE_TARGET*')
        sci_field_names = [msmd.fieldnames()[n] for n in sci_field_ids]
        sci_spw = msmd.spwsforintent('OBSERVE_TARGET*')
        msmd.close()
        # get MS info II (datacolumn)
        tb = table()
        tb.open(vis_in)
        column_all =tb.colnames()
        tb.close()
        wanted = ['DATA', 'CORRECTED_DATA' , 'MODEL_DATA']
        datacolumn = [col for col in column_all if col in wanted]
        # 
        data_all[key]= {"vis":vis_in,
                        "Time":[Time0_yyyymmdd,Time1_yyyymmdd],
                        "Fields":sci_field_names,
                        "SPWs":sci_spw,
                        "datacolumn":datacolumn}
    else:
        print(f'File not found: {vis_in}')
        #f.write(f'File not found: {vis_in}'+"\n")


## make list of all science field 
sci_field_all=[]
for i in list(data_all.keys()):
    for name in data_all[i]["Fields"]:
        if name not in sci_field_all:sci_field_all.append(name)
        sci_spw_st = ', '.join(map(str, data_all[key]['SPWs']))
print(sci_field_all)
print(sci_spw_st)


## output log file
if os.path.exists(output_log): os.system('rm '+output_log)
now = datetime.datetime.now()
now_st = now.strftime("%Y-%m-%d %H:%M:%S")
with open(output_log, "x", encoding="utf-8") as f:
    f.write("## Split & Concatination (K.Saigo 2025/7/12) \n")
    f.write("#Execution on : "+now_st +"\n")
    f.write("## Data Selection \n")
    f.write("#working directory: "+dir +"\n")
    f.write("#data_select: "+data_select +"\n")
    f.write("#data directory: "+dir +"\n")
    f.write("## Split settings \n")
    f.write("#search word: "+search_word +"\n")
    f.write("#split column : "+split_column +"\n")
    f.write("#Science SPWs : "+sci_spw_st+"\n")
    f.write("#Science Fields: "+str(sci_field_all)+"\n")
    f.write("## Summary of all EBs \n")
    f.write("#data_all = \n")
    f.write(pprint.pformat(data_all))
    f.write('\n')


##### Step 2 split & concatination ########
Exec_Split = True
Concat_TMP = False  #Concatination all Splitted MS
Delete_TMP = False  #Delete temporary splitted MS after concatination
if Exec_Split:
    dir_org = os.getcwd() # recored original work directory
    #for Fname in sci_field_all[0:1]:
    for Fname in sci_field_all:
        print('Split and concatination of '+Fname)
        dir_data = 'Work_'+data_select+'_'+Fname
        dir_tmp = os.path.join(dir_org, dir_data)
        #
        if not os.path.exists(dir_tmp):
            os.mkdir(dir_tmp)
            print(f"{dir_tmp}  created")
        else:
            print(f"{dir_tmp}  exist")
            if os.path.exists(dir_tmp+'.OLD'):os.system('rm -rf '+dir_tmp+'.OLD')
            os.system('mv '+dir_tmp+' '+dir_tmp+'.OLD')
            os.mkdir(dir_tmp)
        #
        os.chdir(dir_tmp)
        EB_list=[]
        EB_list_org=[]
        for key in list(data_all.keys()):
            vis        = data_all[key]['vis']
            if not os.path.isabs(vis):  vis = os.path.abspath(vis) #abs. path
            outputvis  = key+'_'+Fname+'_targets.ms'
            sci_spw_st = ', '.join(map(str, data_all[key]['SPWs']))
            EB_list.append(outputvis)
            EB_list_org.append(vis) 
            print(' Split:'+outputvis)
            mstransform(vis=vis, spw = sci_spw_st, field=Fname, datacolumn=split_column, outputvis=outputvis, reindex=False)
        #
        # Conatination
        if Concat_TMP:
            concatvis = 'Concat_'+data_select+'_'+Fname            
            print('Concatination: '+concatvis)
            print(EB_list)
            if os.path.exists(concatvis): os.system('rm -r '+concatvis)
            concat(vis=EB_list, concatvis=concatvis)
            if os.path.exists(concatvis+'.listobs'): os.system('rm -r '+concatvis+'.listobs')
            listobs(vis=concatvis, listfile=concatvis+'.listobs')
        # Output Logfiles
        LogFile   = 'Work_'+data_select+'_'+Fname+'.Log'
        if os.path.exists(LogFile): os.system('rm '+LogFile)
        with open(LogFile, "x", encoding="utf-8") as f:
            f.write("#Execution   : "+now_st +"\n")
            f.write("#Split Field : "+Fname +"\n")
            f.write("#Science SPWs: "+sci_spw_st+"\n")
            f.write("#split column: "+split_column +"\n")
            if Concat_TMP:f.write("#Concat MS   : "+concatvis +"\n")    
            if Concat_TMP:f.write("#concatinated EBs \n")
            for item in EB_list_org: f.write(item + '\n')
        #
        # Delete temporary splitted MS after concatination
        if Delete_TMP:
            print('Delete temporary splitted MS after concatination')
            for tmp in EB_list:
                print(tmp)
                os.system('rm -rf '+tmp)
        #
        os.chdir(dir_org)

##################################################################



