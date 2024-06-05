#!/usr/bin/env python

import sys
from math import ceil
from os import system  # for execution at the end
from pathlib import Path

import ROOT
from utils import load_config, parse_args


def main():

    # ==========================
    # Load specified config file
    # ==========================

    args = parse_args()
    config = load_config(args.config)

    # ==========================
    # Check paths
    # ==========================

    assert (
        config.sim_steering_file.exists()
    ), f"The file {config.sim_steering_file} does not exist"
    assert (
        config.rec_steering_file.exists()
    ), f"The file {config.rec_steering_file} does not exist"
    assert (
        config.detectorDIR.exists()
    ), f"The folder {config.detectorDIR} does not exist"

    # ==========================
    # Parameters Initialisation
    # ==========================

    assert isinstance(config.Nevts_, int), "config.Nevts_ must be of type integer"
    assert isinstance(
        config.Nevts_per_job, int
    ), "config.Nevts_per_job must be of type integer"

    N_para_sets = (
        len(config.detectorModelList)
        * len(config.particleList_)
        * len(config.thetaList_)
        * len(config.momentumList_)
    )
    # number of parallel jobs with same parameter combination/set
    N_jobs_per_para_set = ceil(
        config.Nevts_ / config.Nevts_per_job
    )  # Nevts is lower limit
    # total number of jobs, can be printed for debugging/information
    N_jobs = N_jobs_per_para_set * N_para_sets

    # ===========================
    # Directory Setup and Checks
    # ===========================

    # Define directories for input and output
    directory_jobs = (
        config.SIMcondorDir / f"{config.particleList_[0]}_{config.detectorModelList[0]}"
    )
    SIMEOSDir = config.dataDir / f"{config.detectorModelList[0]}" / "SIM"  # output

    # Enable output checks
    CHECK_OUTPUT = True
    """
    Set to True to enable checks, False to disable
    It will check if the ouputs exist and contain correct number of events
    if not it will send job to rerun simulation
    """

    # Check if the directory exists and exit if it does
    try:
        directory_jobs.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(
            f"Error: Directory '{directory_jobs}' already exists and should not be overwritten."
        )
        sys.exit(1)

    SIMEOSDir.mkdir(
        parents=True, exist_ok=True
    )  # This will create the directory if it doesn't exist, without raising an error if it does

    # =======================
    # Simulation Job Creation
    # =======================

    # Create all possible combinations
    import itertools

    iter_of_combined_variables = itertools.product(
        config.thetaList_,
        config.momentumList_,
        config.particleList_,
        config.detectorModelList,
    )

    need_to_create_scripts = False

    for theta, momentum, part, dect in iter_of_combined_variables:
        for task_index in range(N_jobs_per_para_set):

            output_file_name_parts = [
                f"SIM_{dect}",
                f"{part}",
                f"{theta}_deg",
                f"{momentum}_GeV",
                f"{config.Nevts_per_job}_evts",
                f"{task_index}",
            ]
            output_file_name = Path("_".join(output_file_name_parts)).with_suffix(
                ".edm4hep.root"
            )

            # Check if the output file already exists and has correct Nb of events
            output_dir = SIMEOSDir / part
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = output_dir / output_file_name
            if CHECK_OUTPUT and output_file_path.exists():
                root_file = ROOT.TFile(output_file_path, "READ")
                events_tree = root_file.Get("events")
                if events_tree:  # FIXME: why no else?
                    if events_tree.GetEntries() == config.Nevts_per_job:
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
                "--enableGun",
                f"--gun.particle {part}-",
                f"--gun.energy {momentum}*GeV",
                "--gun.distribution uniform",
                f"--gun.thetaMin {theta}*deg",
                f"--gun.thetaMax {theta}*deg",
                "--crossingAngleBoost 0",
                f"--numberOfEvents {config.Nevts_per_job}",
            ]
            command = f"ddsim {' '.join(arguments)} > /dev/null"

            # Write bash script for job execution
            bash_script = (
                "#!/bin/bash \n"
                f"source {config.setup} \n"
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
            bash_file = (directory_jobs / "_".join(bash_file_name_parts)).with_suffix(
                ".sh"
            )

            with open(bash_file, "w", encoding="utf-8") as b_file:
                b_file.write(bash_script)
                b_file.close()

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
        f'+JobFlavour = "{config.JOB_FLAVOR}" \n'
        "queue filename matching files *.sh \n"
    )
    condor_file = directory_jobs / "condor_script.sub"
    with open(condor_file, "w", encoding="utf-8") as c_file:
        c_file.write(condor_script)
        c_file.close()

    # ====================
    # Submit Job to Condor
    # ====================

    system(
        "cd " + str(directory_jobs) + "; condor_submit condor_script.sub"
    )  # FIXME: use subprocess instead?


if __name__ == "__main__":
    main()
