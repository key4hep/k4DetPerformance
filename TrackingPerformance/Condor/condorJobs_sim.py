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
#momentumList_      = [ "1"]#, "2"]
#particleList_      = [ "mu"]
DetectorModelList_ = [ "FCCee_o2_v02"]
Nevts_             = "10"
runningDirectory = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor"
SteeringFile = "/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/fcc_steer.py"
setup = "/cvmfs/sw.hsf.org/key4hep/setup.sh"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModelList_[0]}/SIM/Test_splitting"
run_sim_path = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor/run_ddsim.py"

# Create EosDir is it does not exist
if not os.path.exists(EosDir):
    os.makedirs(EosDir)

# Function to split the tasks into chunks of 200
def chunk_tasks(tasks_list, chunk_size=200):
    for i in range(0, len(tasks_list), chunk_size):
        yield tasks_list[i:i + chunk_size]

# Create the Condor submit script and submit jobs in chunks
condor_file_template = '''
executable = bash_script.sh
arguments = $(ClusterId) $(ProcId)
output = output.$(ClusterId).$(ProcId).out
error = error.$(ClusterId).$(ProcId).err
log = log.$(ClusterId).log
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
        file.write("cp " +  run_sim_path + " . " + "\n")

        # Loop over tasks in the current chunk
        for task_id in chunk:
            dect, part, theta, momentum = [DetectorModelList_[task_id // (len(particleList_) * len(thetaList_) * len(momentumList_))],
                                           particleList_[(task_id // (len(thetaList_) * len(momentumList_))) % len(particleList_)],
                                           thetaList_[(task_id // len(momentumList_)) % len(thetaList_)],
                                           momentumList_[task_id % len(momentumList_)]]

            output_file = "SIM_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts.slcio"

            time.sleep(1)
            seed = str(time.time() % 1000)
            arguments = "-DetectorModel " + dect + " -Nevts " + Nevts_ + " -Particle " + part + " -Momentum " + momentum + " -Theta " + theta + " -Seed " + seed + " -OutputPath " + output_file + " -SteeringFile " + SteeringFile
            command = "python run_ddsim.py " + arguments

            file.write(command + "\n")
            file.write("cp " + output_file + " " + EosDir + "\n")

    os.chmod(bash_file, 0o755)

    # Create the Condor submit script for this chunk
    condor_file = os.path.join(directory_jobs, "condor_script.sub")
    with open(condor_file, "w") as file2:
        file2.write(condor_file_template.format(len(chunk)))

    # Submit the Condor job for this chunk
    os.system(f"cd {directory_jobs}; condor_submit condor_script.sub")


