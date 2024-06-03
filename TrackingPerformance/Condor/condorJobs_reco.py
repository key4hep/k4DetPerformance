#!/usr/bin/env python

import sys
from os import system  # for execution at the end
from pathlib import Path

import ROOT
from utils import load_config, parse_args

# ==========================
# Load specified config file
# ==========================

args = parse_args()
config = load_config(args.config)


# ==========================
# Parameters Initialisation
# ==========================
# Define lists of parameters for reconstruction
thetaList_ = config.thetaList_
momentumList_ = config.momentumList_
particleList_ = config.particleList_

DetectorModelList_ = config.detectorModel
Nevts_ = config.Nevts_

Nevt_per_job = config.Nevt_per_job
N_jobs = (
    int(int(Nevts_) / int(Nevt_per_job))
    * len(particleList_)
    * len(thetaList_)
    * len(momentumList_)
)
total_events = int(Nevts_)
num_jobs = total_events // int(Nevt_per_job)

# ===========================
# Directory Setup and Checks
# ===========================

# Define environment setup path
environ_path = config.setup

# Define directories for input and output
directory_jobs = config.RECcondorDir / f"{particleList_[0]}_{DetectorModelList_[0]}"
# InputDirectory = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/SIM/3T/"
SIMEosDir = config.dataDir / f"{DetectorModelList_[0]}" / "SIM"  # input
RECEosDir = config.dataDir / f"{DetectorModelList_[0]}" / "REC"  # output

# steering_file = "CLDReconstruction.py"
steering_file = config.rec_steering_file

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
        ResVDX_UV_ = ["0.003"]
except NameError:
    ResVDX_UV_ = ["0.003"]

# Check if the directory exists and exit if it does
if directory_jobs.exists():
    print(
        f"Error: Directory '{directory_jobs}' already exists and should not be overwritten."
    )
    sys.exit(1)

# Create output directories if they don't exist
RECEosDir.mkdir(parents=True, exist_ok=True)
directory_jobs.mkdir(parents=True, exist_ok=True)

# =======================
# Simulation Job Creation
# =======================
# Create all possible combinations
import itertools

list_of_combined_variables = itertools.product(
    thetaList_, momentumList_, particleList_, DetectorModelList_
)

need_to_create_scripts = False

for theta, momentum, part, dect in list_of_combined_variables:
    for task_index in range(num_jobs):

        output_file_name_parts = [
            f"REC_{dect}",
            f"{part}",
            f"{theta}_deg",
            f"{momentum}_GeV",
            f"{Nevt_per_job}_evts",
            f"{task_index}",
        ]
        output_file_name = "_".join(output_file_name_parts)

        input_file_name_parts = [
            f"SIM_{dect}",
            f"{part}",
            f"{theta}_deg",
            f"{momentum}_GeV",
            f"{Nevt_per_job}_evts",
            f"{task_index}",
        ]
        input_file_name = "_".join(input_file_name_parts)
        input_file_path = Path(input_file_name).with_suffix(".edm4hep.root")
        inputFile = (
            SIMEosDir / part / input_file_path
        )  # FIXME: reasonable that part is twice in the path?

        # Check if the input file exists
        if not inputFile.exists():
            print(f"Error: Input file {inputFile} does not exist. Skipping job.")
            continue
        # Check if the output file already exists and has correct Nb of events
        output_dir = RECEosDir / part
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = (output_dir / output_file_name).with_suffix("_edm4hep.root")

        if check_output and output_file.exists():
            root_file = ROOT.TFile(output_file, "READ")
            events_tree = root_file.Get("events")
            if events_tree and events_tree.GetEntries() == int(Nevt_per_job):
                root_file.Close()
                continue
            root_file.Close()
        need_to_create_scripts = True

        # Create aida output Dir
        output_dir_aida = output_dir / "aida_outputs"
        output_dir_aida.mkdir(exist_ok=True)

        arguments = (
            # f" --GeoSvc.detectors=/afs/cern.ch/work/g/gasadows/k4geo/FCCee/CLD/compact/{DetectorModelList_[0]}_3T/{DetectorModelList_[0]}.xml"+
            f" --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml"
            + " --inputFiles "
            + inputFile
            + " --outputBasename  "
            + output_file_name
            + f" --VXDDigitiserResUV={ResVDX_UV_[0]}"
            + " --trackingOnly"
            + " -n "
            + Nevt_per_job
        )
        command = f"k4run {steering_file} " + arguments + " > /dev/null"

        # Write bash script for job execution
        bash_script = (
            "#!/bin/bash \n"
            f"source {environ_path} \n"
            "git clone https://github.com/gaswk/CLDConfig.git \n"  # FIXME: see issues
            "cd " + "CLDConfig/CLDConfig" + "\n"  # FIXME: CLD should not be hardcoded
            f"{command} \n"
            f"xrdcp {output_file_name}_edm4hep.root  root://eosuser.cern.ch/{output_dir} \n"
            f"xrdcp {output_file_name}_aida.root  root://eosuser.cern.ch/{output_dir_aida} \n"
        )
        bash_file = (
            directory_jobs
            + f"/bash_script_{dect}_{part}_{momentum}_{theta}_{task_index}.sh"
        )
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
    f'+JobFlavour = "{JobFlavour}" \n'
    "queue filename matching files *.sh \n"
)
condor_file = directory_jobs + "/condor_script.sub"
with open(condor_file, "w") as file2:
    file2.write(condor_script)
    file2.close()

# ====================
# Submit Job to Condor
# ====================
system(
    "cd " + str(directory_jobs) + "; condor_submit condor_script.sub"
)  # FIXME: use subprocess instead?
