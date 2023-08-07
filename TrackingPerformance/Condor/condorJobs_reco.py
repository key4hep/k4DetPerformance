#!/usr/bin/env python

import os
import argparse
import subprocess
import time;
ts = time.time()

thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
momentumList_      = [ "1", "2", "5", "10", "20", "50", "100", "200"]
particleList_      = [ "mu", "e", "pi"]
#thetaList_         = ["10", "20"]
#momentumList_      = [ "1", "2"]
#particleList_      = [ "mu"]
DetectorModelList_ = [ "FCCee_o2_v02"]
Nevts_             = "10"
CondorDirectory = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor"
InputDirectory = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModelList_[0]}/SIM/"
SteeringFile = "/afs/cern.ch/user/g/gasadows/FullSim/fccRec_lcio_input_trackers.py"
#setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2023-06-22/x86_64-centos7-gcc12.2.0-opt/key4hep-stack/2023-06-22-4kk5ro/setup.sh"
setup = "/cvmfs/sw.hsf.org/key4hep/setup.sh"
CLICdir = "/afs/cern.ch/user/g/gasadows/CLICPerformance"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModelList_[0]}/REC/Test_splitting"
ResVDXValuesU_ = ['0.003']
ResVDXValuesV_ = ['0.003']
ResITValuesU_ = ['0.007']
ResITValuesV_ = ['0.09']
ResOTValuesU_ = ['0.007']
ResOTValuesV_ = ['0.09']
DetectorModelPath = f"/FCCee/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml"
Config_Value_Path = "/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/"
run_reco_path = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor/run_reco.py"

# Create EosDir is it does not exist
if not os.path.exists(EosDir):
    os.makedirs(EosDir)

# Create config file with Detector model and resolution for Vertex Detector
for (VXDBarrelResU, VXDBarrelResV, VXDEndcapResU, VXDEndcapResV,
     ITBarrelResU, ITBarrelResV, ITEndcapResU, ITEndcapResV,
     OTBarrelResU, OTBarrelResV, OTEndcapResU, OTEndcapResV) in zip(ResVDXValuesU_, ResVDXValuesV_, ResVDXValuesU_, ResVDXValuesV_,
                                                                  ResITValuesU_, ResITValuesV_, ResITValuesU_, ResITValuesV_,
                                                                  ResOTValuesU_, ResOTValuesV_, ResOTValuesU_, ResOTValuesV_):
    # Create the content for config_values.py
    content = f'''
DetectorModel = "{DetectorModelPath}"

VXDBarrelResU = "{VXDBarrelResU}"
VXDBarrelResV = "{VXDBarrelResV}"
VXDEndcapResU = "{VXDEndcapResU}"
VXDEndcapResV = "{VXDEndcapResV}"

ITBarrelResU = "{ITBarrelResU}"
ITBarrelResV = "{ITBarrelResV}"
ITEndcapResU = "{ITEndcapResU}"
ITEndcapResV = "{ITEndcapResV}"

OTBarrelResU = "{OTBarrelResU}"
OTBarrelResV = "{OTBarrelResV}"
OTEndcapResU = "{OTEndcapResU}"
OTEndcapResV = "{OTEndcapResV}"
    '''

    # Write the content to config_values.py and overwrite the file if it already exists
    with open(f"{Config_Value_Path}config_values.py", "w") as file:
        file.write(content)

# Run Reco
# Function to split the tasks into chunks of 200
def chunk_tasks(tasks_list, chunk_size=200):
    for i in range(0, len(tasks_list), chunk_size):
        yield tasks_list[i:i + chunk_size]

# Create the Condor submit script and submit jobs in chunks
condor_file_template = '''
executable = bash_script.sh
output = output.$(ClusterId).$(Process).out
error = error.$(ClusterId).$(Process).err
log = log.$(ClusterId).log
+JobFlavour = "longlunch"
queue {}
'''
#+JobFlavour = "microcentury"   # 1 hour
#+JobFlavour = "longlunch"     # 2 hours
#+JobFlavour = "workday"        # 8 hours

# Calculate the total number of tasks
total_tasks = len(DetectorModelList_) * len(particleList_) * len(thetaList_) * len(momentumList_)

# Split tasks into chunks of 200
task_chunks = list(chunk_tasks(range(total_tasks)))

# Loop over task chunks and create a Condor job submission for each chunk
for i, chunk in enumerate(task_chunks):
    directory_jobs = f"CondorJobs_{i}"
    os.system(f"mkdir -p {directory_jobs}")

    bash_file = os.path.join(directory_jobs, "bash_script.sh")
    with open(bash_file, "w") as file:
        file.write("#!/bin/bash \n")
        file.write("source "+ setup + "\n")
        file.write("cp -rf " + CLICdir + " ." + "\n")
        file.write("cd " + "CLICPerformance/fcceeConfig" + "\n")
        file.write("cp " +  run_reco_path + " . " + "\n")

        # Loop over tasks in the current chunk
        for task_id in chunk:
            dect, part, theta, momentum = [DetectorModelList_[task_id // (len(particleList_) * len(thetaList_) * len(momentumList_))],
                                           particleList_[(task_id // (len(thetaList_) * len(momentumList_))) % len(particleList_)],
                                           thetaList_[(task_id // len(momentumList_)) % len(thetaList_)],
                                           momentumList_[task_id % len(momentumList_)]]

            output_file = "REC_" + dect + "_" + "resVXD_" + str(int(float(VXDBarrelResU)*1000)) + "mic_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts_edm4hep.root"
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












