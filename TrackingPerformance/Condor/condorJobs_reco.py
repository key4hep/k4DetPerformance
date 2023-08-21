#!/usr/bin/env python

import os
import argparse
import subprocess
import time;
ts = time.time()

thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
momentumList_      = [ "1", "2", "5", "10", "20", "50", "100", "200"]
#particleList_      = [ "mu", "e", "pi"]
#thetaList_         = ["10", "20"]
#momentumList_      = [ "1", "2"]
particleList_      = [ "mu"]
DetectorModelList_ = [ "FCCee_o2_v02"]
Nevts_             = "10000"
CondorDirectory = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor"
InputDirectory = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModelList_[0]}/SIM/"
SteeringFile = "/afs/cern.ch/user/g/gasadows/FullSim/fccRec_lcio_input_trackers.py"
#setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2023-06-22/x86_64-centos7-gcc12.2.0-opt/key4hep-stack/2023-06-22-4kk5ro/setup.sh"
setup = "/cvmfs/sw.hsf.org/key4hep/setup.sh"
CLICdir = "/afs/cern.ch/user/g/gasadows/CLICPerformance"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModelList_[0]}/REC/"
ResVDXValuesU_ = ['0.003']
ResVDXValuesV_ = ['0.003']
ResITValuesU_ = ['0.005','0.006','0.007','0.008','0.009']   #ResITValuesU_ = ['0.007']
ResITValuesV_ = ['0.07','0.08','0.09','0.10','0.11']    #ResITValuesV_ = ['0.09']
ResOTValuesU_ = ['0.007']
ResOTValuesV_ = ['0.09']
DetectorModelPath = f"/FCCee/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml"
Config_Value_Path = "/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/"
run_reco_path = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor/run_reco.py"

# Create EosDir is it does not exist
if not os.path.exists(EosDir):
    os.makedirs(EosDir)
# Create the Condor jobs submission directory 
if not os.path.exists(CondorDirectory):
    os.makedirs(CondorDirectory)

# Split tasks into chunks of 200
def chunk_tasks(tasks_list, chunk_size=200):
    for i in range(0, len(tasks_list), chunk_size):
        yield tasks_list[i:i + chunk_size]

# Create the Condor submit script and submit jobs in chunks
condor_file_template = '''
executable = bash_script.sh
output = output.$(ClusterId).out
error = error.$(ClusterId).err
log = log.$(ClusterId).log
+JobFlavour = "longlunch"
queue {}
'''
#+JobFlavour = "microcentury"   # 1 hour
#+JobFlavour = "longlunch"     # 2 hours
#+JobFlavour = "workday"        # 8 hours

total_tasks = len(DetectorModelList_) * len(particleList_) * len(thetaList_) * len(momentumList_)
task_chunks = list(chunk_tasks(range(total_tasks)))

# Create the Condor jobs submission directory for each set of resolution values
for VXDBarrelResU, VXDBarrelResV in zip(ResVDXValuesU_, ResVDXValuesV_):
    for ITBarrelResU, ITBarrelResV in zip(ResITValuesU_, ResITValuesV_):
        for OTBarrelResU, OTBarrelResV in zip(ResOTValuesU_, ResOTValuesV_):
            # Create a unique directory for this combination of resolution values
            res_set_directory = os.path.join(CondorDirectory, f"CondorJobs_VXD{VXDBarrelResU}_IT{ITBarrelResU}_OT{OTBarrelResU}")
            os.makedirs(res_set_directory, exist_ok=True)
    # Generate content for the config_values.py using the current resolution values
            config_content = f'''
DetectorModel = "{DetectorModelPath}"

VXDBarrelResU = "{VXDBarrelResU}"
VXDBarrelResV = "{VXDBarrelResV}"
VXDEndcapResU = "{VXDBarrelResU}"
VXDEndcapResV = "{VXDBarrelResV}"

ITBarrelResU = "{ITBarrelResU}"
ITBarrelResV = "{ITBarrelResV}"
ITEndcapResU = "{ITBarrelResU}"
ITEndcapResV = "{ITBarrelResV}"

OTBarrelResU = "{OTBarrelResU}"
OTBarrelResV = "{OTBarrelResV}"
OTEndcapResU = "{OTBarrelResU}"
OTEndcapResV = "{OTBarrelResV}"
    '''
            print(config_content)
            # Write the content to config_values.py
            with open(os.path.join(Config_Value_Path, "config_values.py"), "w") as config_file:
                config_file.write(config_content)

            # Loop over task chunks and create a Condor job submission for each chunk
            for i, chunk in enumerate(task_chunks):
                directory_jobs = os.path.join(res_set_directory, f"CondorJobs_{i}")
                os.makedirs(directory_jobs, exist_ok=True)

                bash_file = os.path.join(directory_jobs, "bash_script.sh")
                with open(bash_file, "w") as file:
                    file.write("#!/bin/bash \n")
                    file.write("source "+ setup + "\n")
                    file.write("cp -rf " + CLICdir + " ." + "\n")
                    file.write("cd " + "CLICPerformance/fcceeConfig" + "\n")
                    file.write("cp " +  run_reco_path + " . " + "\n")

                    # Loop over tasks in the current chunk
                    for task_id in chunk:
                        dect, part, theta, momentum = [
                            DetectorModelList_[task_id // (len(particleList_) * len(thetaList_) * len(momentumList_))],
                            particleList_[(task_id // (len(thetaList_) * len(momentumList_))) % len(particleList_)],
                            thetaList_[(task_id // len(momentumList_)) % len(thetaList_)],
                            momentumList_[task_id % len(momentumList_)]
                        ]

                        output_file = "REC_" + dect + "_" + "resIT_U_" + str(int(float(ITBarrelResU)*1000)) + "_V_" + str(int(float(ITBarrelResV)*1000)) + "mic_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts_edm4hep.root"
                        input_file= os.path.join(InputDirectory, "SIM_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts.slcio")

                        time.sleep(1)
                        seed = str(time.time()%1000)
                        arguments = " -Nevts " + Nevts_ + " -OutputPath " + output_file+ " -InputPath " + input_file + " -SteeringFile " + SteeringFile
                        command = "python run_reco.py " + arguments

                        file.write(command + "\n")
                        file.write("cp " + output_file + " " + EosDir + "\n")

                os.chmod(bash_file, 0o755)

                # Create the Condor submit script for this chunk
                condor_file = os.path.join(directory_jobs, "condor_script.sub")
                with open(condor_file, "w") as file2:
                    file2.write(condor_file_template.format(len(chunk)))

                # Submit the Condor job for this chunk
                os.system(f"cd {directory_jobs}; condor_submit condor_script.sub")



