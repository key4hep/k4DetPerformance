#!/usr/bin/env python

from os import system  # for execution at the end
import sys
import ROOT
from pathlib import Path

verbose = False

# ==========================
# Import config
# ==========================
# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parent.parent
# Append the project root to sys.path if not already present
if project_root not in sys.path:
    sys.path.append(str(project_root))
# import config
import config

# ==========================
# Parameters Initialisation
# ==========================
# Define lists of parameters for reconstruction
thetaList_ = config.thetaList_
momentumList_ = config.momentumList_
particleList_ = config.particleList_

DetectorModelList_ = config.detectorModel
Nevts_ = config.Nevts_
Nevt_per_job = config.Nevt_per_job  # Set the desired number of events per job


total_events = int(Nevts_)
num_jobs_per_para_set = total_events // int(
    Nevt_per_job
)  # number of parallel jobs with same parameter combination/set
N_jobs = (
    num_jobs_per_para_set * len(particleList_) * len(thetaList_) * len(momentumList_)
)  # total number of jobs

# ===========================
# Directory Setup and Checks
# ===========================

# Define environment setup path
environ_path = config.setup

# Define directories for input and output
directory_jobs = config.SIMcondorDir / f"{particleList_[0]}_{DetectorModelList_[0]}"
SIMEosDir = config.dataDir / f"{DetectorModelList_[0]}" / "SIM"  # output

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
try:
    directory_jobs.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print(
        f"Error: Directory '{directory_jobs}' already exists and should not be overwritten."
    )
    sys.exit(1)

SIMEosDir.mkdir(
    parents=True, exist_ok=True
)  # This will create the directory if it doesn't exist, without raising an error if it does


# =======================
# Simulation Job Creation
# =======================
# Create all possible combinations
import itertools

iter_of_combined_variables = itertools.product(
    thetaList_, momentumList_, particleList_, DetectorModelList_
)

need_to_create_scripts = False

if verbose:
    print(f"1st of {N_jobs} different parameter combinations starts")
for counter, (theta, momentum, part, dect) in enumerate(iter_of_combined_variables):
    for task_index in range(num_jobs_per_para_set):

        output_file_name_parts = [
            f"SIM_{dect}",
            f"{part}",
            f"{theta}_deg",
            f"{momentum}_GeV",
            f"{Nevt_per_job}_evts",
            f"{task_index}",
        ]
        output_file_name = "_".join(output_file_name_parts)
        output_file_path = Path(output_file_name).with_suffix(".edm4hep.root")

        # Check if the output file already exists and has correct Nb of events
        output_dir = SIMEosDir / part / output_file_path
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / output_file_name
        if check_output and output_file.exists():
            root_file = ROOT.TFile(output_file, "READ")
            events_tree = root_file.Get("events")
            if events_tree:  # FIXME: why no else?
                if events_tree.GetEntries() == int(Nevt_per_job):
                    root_file.Close()
                    continue
            root_file.Close()
        else:
            need_to_create_scripts = True

        # if len(DetectorModelList_) != 1 or DetectorModelList_[0] != "ILD_l5_v11":
        #     raise ValueError("so far only ILD_l5_v11 possible")

        # Build ddsim command
        arguments = [
            # f" --compactFile /afs/cern.ch/work/g/gasadows/k4geo/FCCee/CLD/compact/{DetectorModelList_[0]}_3T/{DetectorModelList_[0]}.xml "
            f" --compactFile $k4geo_DIR/{config.detModPaths['ILD_l5_v11']}",  # Note the change to use double quotes for the dictionary key
            f"--outputFile {output_file_name}",
            f"--steeringFile {config.sim_steering_file}",  # "CLDConfig/CLDConfig/cld_steer.py "
            # TODO: FIX
            # "--enableGun",
            # f"--gun.particle {part}-",
            # f"--gun.energy {momentum}*GeV",
            # "--gun.distribution uniform",
            # f"--gun.thetaMin {theta}*deg",
            # f"--gun.thetaMax {theta}*deg",
            # "--crossingAngleBoost 0",
            # f"--numberOfEvents {Nevt_per_job}",
        ]
        command = f"ddsim {' '.join(arguments)} > /dev/null"

        # Write bash script for job execution
        bash_script = (
            "#!/bin/bash \n"
            f"source {environ_path} \n"
            "git clone https://github.com/Victor-Schwan/TrackingStudies.git \n"
            f"{command} \n"
            f"xrdcp {output_file_name} root://eosuser.cern.ch/{output_dir} \n"
        )
        bash_file_name_parts = [
            "bash_script",
            dect,
            part,
            f"{theta}_deg",
            f"{momentum}_GeV",
            str(task_index),
        ]
        bash_file = (directory_jobs / "_".join(bash_file_name_parts)).with_suffix(".sh")

        with open(bash_file, "w") as file:
            file.write(bash_script)
            file.close()

        if verbose:
            print(f"    {task_index+1} of {num_jobs_per_para_set} parallel jobs done")

    if verbose:
        print(f"{counter+1} of {N_jobs} different parameter combinations done")

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
condor_file = directory_jobs / "condor_script.sub"
with open(condor_file, "w") as file2:
    file2.write(condor_script)
    file2.close()

# ====================
# Submit Job to Condor
# ====================
system(
    "cd " + str(directory_jobs) + "; condor_submit condor_script.sub"
)  # FIXME: use subprocess instead?
