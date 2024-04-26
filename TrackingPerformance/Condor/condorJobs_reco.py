#!/usr/bin/env python

import os
import sys
import ROOT  
import argparse
import subprocess

# ==========================
# Parameters Initialisation
# ==========================
# Define lists of parameters for reconstruction
thetaList_ = ["10", "20", "30", "40", "50", "60", "70", "80", "89"] 
#thetaList_ = ["70", "80", "89"] 
momentumList_ = ["1", "2", "5", "10", "20", "50", "100", "200"] 
#momentumList_ = ["1", "10", "100"] 
particleList_ = ["mu"]#,"e" ,"pi"]  
#ResVDX_UV_ = ['0.001']

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
directory_jobs = f"CondorJobs/Rec_{particleList_[0]}_{DetectorModelList_[0]}"
setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh"
#InputDirectory = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/SIM/3T/"
InputDirectory = f"/eos/experiment/fcc/users/g/gasadows/TrackingPerformance/{DetectorModelList_[0]}/SIM/3T/"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/REC/3T/"

#steering_file = "CLDReconstruction.py"
steering_file = "/afs/cern.ch/user/g/gasadows/CLDConfig/CLDConfig/CLDReconstruction_3T.py"

# Enable output checks
check_output = True  # Set to True to enable checks, False to disable
                     # It will check if the ouputs exist and contain correct number of events
                     # if not it will send job to rerun reconstruction

JobFlavour = "tomorrow"
# Job flavours:
#   espresso     = 20 minutes
#   microcentury = 1 hour
#   longlunch    = 2 hours
#   workday      = 8 hours
#   tomorrow     = 1 day
#   testmatch    = 3 days
#   nextweek     = 1 week

# Set default value if ResVDX_UV_ is not defined or empty
try:
    if not ResVDX_UV_:
        ResVDX_UV_ = ['0.003']
except NameError:
    ResVDX_UV_ = ['0.003']

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

        outputFileName = f"REC_{dect}"
        outputFileName+= f"_{part}"
        outputFileName+= f"_{theta}_deg"
        outputFileName+= f"_{momentum}_GeV"
        outputFileName+= f"_{Nevt_per_job}_evts"
        outputFileName+= f"_{task_index}"

        inputFile= os.path.join(InputDirectory + f"/{part}", f"SIM_{dect}_{part}_{theta}_deg_{momentum}_GeV_{Nevt_per_job}_evts_{task_index}_edm4hep.root")  
        #inputFile= os.path.join(InputDirectory + f"/{part}", f"SIM_{dect}_{part}_{theta}_deg_{momentum}_GeV_{Nevt_per_job}_evts_edm4hep.root")  
        #input_file= os.path.join(InputDirectory, "SIMTest_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts.slcio")

        # Check if the input file exists
        if not os.path.exists(inputFile):
            print(f"Error: Input file {inputFile} does not exist. Skipping job.")
            continue 
        # Check if the output file already exists and has correct Nb of events
        output_dir = os.path.join(EosDir, part); os.makedirs(output_dir, exist_ok=True)
        output_file = output_dir +"/"+ outputFileName + "_edm4hep.root"
        if check_output and os.path.exists(output_file):
            root_file = ROOT.TFile(output_file, "READ")
            events_tree = root_file.Get("events")
            if events_tree and events_tree.GetEntries() == int(Nevt_per_job):
                root_file.Close()
                continue
            root_file.Close()
        need_to_create_scripts = True

        # Create aida output Dir
        output_dir_aida = os.path.join(output_dir, "aida_outputs"); os.makedirs(output_dir_aida, exist_ok=True)

        arguments = (
            f" --GeoSvc.detectors=/afs/cern.ch/work/g/gasadows/k4geo/FCCee/CLD/compact/CLD_o2_v05_3T/CLD_o2_v05.xml"+
            #f" --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml"+
            " --inputFiles " + inputFile + " --outputBasename  " + outputFileName+ 
            f" --VXDDigitiserResUV={ResVDX_UV_[0]}" + 
            " --trackingOnly" + 
            " -n " + Nevt_per_job
        )
        command = f"k4run {steering_file} " + arguments + " > /dev/null"

        # Write bash script for job execution
        bash_script = (
            "#!/bin/bash \n"
            f"source {setup} \n"
            "git clone https://github.com/gaswk/CLDConfig.git \n"
            "cd " + "CLDConfig/CLDConfig" + "\n"
            f"{command} \n"
            f"xrdcp {outputFileName}_edm4hep.root  root://eosuser.cern.ch/{output_dir} \n"
            f"xrdcp {outputFileName}_aida.root  root://eosuser.cern.ch/{output_dir_aida} \n"
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



