#!/usr/bin/env python

import os
import sys
import ROOT 
import argparse
import subprocess
import time;

ts = time.time()    # Get current timestamp for unique identifiers

# ==========================
# Parameters Initialisation
# ==========================
# Define lists of parameters for reconstruction
thetaList_ = ["10", "20", "30", "40", "50", "60", "70", "80", "89"] 
momentumList_ = ["1", "2", "5", "10", "20", "50", "100", "200"] 
#momentumList_ = ["1", "10", "100"] 
particleList_ = ["mu"]#,"e" ,"pi"]  

DetectorModelList_ = ["CLD_o3_v01"]  #  FCCee_o1_v04    CLD_o2_v05    CLD_o3_v01
Nevts_ = "10000"  

Nevt_per_job = "1000"  # Set the desired number of events per job
N_jobs = int(int(Nevts_) / int(Nevt_per_job)) * len(particleList_) * len(thetaList_) * len(momentumList_)
total_events = int(Nevts_)
num_jobs = total_events // int(Nevt_per_job)

# ===========================
# Directory Setup and Checks
# ===========================
# Define directories for input and output
directory_jobs = f"CondorJobs/Sim_mu_{DetectorModelList_[0]}"
#setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh" # nightlies
setup = "/cvmfs/sw.hsf.org/key4hep/setup.sh"            # stable
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/SIM/3T"

# Enable output checks
check_output = True  # Set to True to enable checks, False to disable
                     # It will check if the ouputs exist and contain correct number of events
                     # if not it will send job to rerun simulation

JobFlavour = "testmatch"
# Job flavours:
#   espresso     = 20 minutes
#   microcentury = 1 hour
#   longlunch    = 2 hours
#   workday      = 8 hours
#   tomorrow     = 1 day
#   testmatch    = 3 days
#   nextweek     = 1 week


# Check if the directory exists and exit if it does
if os.path.exists(directory_jobs):
    print(f"Error: Directory '{directory_jobs}' already exists and should not be overwritten.")
    sys.exit(1)

# Create output directories if they don't exist
[os.makedirs(directory, exist_ok=True) for directory in [EosDir, directory_jobs]]

# =======================
# Simulation Job Creation 
# =======================
# Create all possible combinations
import itertools
list_of_combined_variables = itertools.product(thetaList_, momentumList_, particleList_, DetectorModelList_)

need_to_create_scripts = False

for theta, momentum, part, dect in list_of_combined_variables:
    for task_index in range(num_jobs):

        output_file_name = f"SIM_{dect}"
        output_file_name+= f"_{part}"
        output_file_name+= f"_{theta}_deg"
        output_file_name+= f"_{momentum}_GeV"
        output_file_name+= f"_{Nevt_per_job}_evts"
        output_file_name+= f"_{task_index}"
        output_file_name+= f"_edm4hep.root"

        # Check if the output file already exists and has correct Nb of events
        output_dir = os.path.join(EosDir, part); os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, output_file_name)
        if check_output and os.path.exists(output_file):
            root_file = ROOT.TFile(output_file, "READ")
            events_tree = root_file.Get("events")
            if events_tree:
                if events_tree.GetEntries() == int(Nevt_per_job):
                    root_file.Close()
                    continue
            root_file.Close()
        else:
            need_to_create_scripts = True
        
        time.sleep(1)
        seed = str(time.time()%1000)
        
        arguments = (
                #f" --compactFile /afs/cern.ch/work/g/gasadows/k4geo/FCCee/CLD/compact/{DetectorModelList_[0]}_3T/{DetectorModelList_[0]}.xml "
                f" --compactFile ${K4GEO}/FCCee/CLD/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml "    
                "--outputFile " + output_file_name + " "
                "--steeringFile " + "CLDConfig/CLDConfig/cld_steer.py "
                "--random.seed " + seed + " "
                "--enableGun "
                "--gun.particle " + part + "- "
                "--gun.energy " + momentum + "*GeV "
                "--gun.distribution uniform "
                "--gun.thetaMin " + theta + "*deg "
                "--gun.thetaMax " + theta + "*deg "
                "--crossingAngleBoost 0 "
                "--numberOfEvents " + Nevt_per_job 
            )
        command = "ddsim " + arguments + " > /dev/null"

        # Write bash script for job execution
        bash_script = (
            "#!/bin/bash \n"
            f"source {setup} \n"
            "git clone https://github.com/gaswk/CLDConfig.git \n"
            f"{command} \n"
            f"xrdcp {output_file_name} root://eosuser.cern.ch/{output_dir} \n"
        )
        bash_file = directory_jobs + f"/bash_script_{dect}_{part}_{momentum}_{theta}_{task_index}.sh"
        with open(bash_file, "w") as file:
            file.write(bash_script)
            file.close()

if not need_to_create_scripts:
    print("All output files are correct.")
    sys.exit(0)

# ============================
# Condor Submission Script
# ============================
# Write the condor submission script
condor_script = (
    "executable = $(filename) \n"
    "arguments = $(ClusterId) $(ProcId) \n"
    "output = output.$(ClusterId).$(ProcId).out \n"
    "error = error.$(ClusterId).$(ProcId).err \n"
    "log = log.$(ClusterId).log \n"
    f"+JobFlavour = \"{JobFlavour}\" \n"  
    "queue filename matching files *.sh \n"
)
condor_file = directory_jobs + "/condor_script.sub"
with open(condor_file, "w") as file2:
    file2.write(condor_script)
    file2.close()

# ====================
# Submit Job to Condor
# ====================
os.system("cd "+ directory_jobs + "; condor_submit condor_script.sub")


