#!/usr/bin/env python

import sys
from math import ceil
from os import fspath, system  # for execution at the end
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
        config.rec_steering_file.exists()
    ), f"The file {config.rec_steering_file} does not exist"
    assert (
        config.detector_dir.exists()
    ), f"The folder {config.detector_dir} does not exist"

    # ==========================
    # Parameters Initialisation
    # ==========================

    n_para_sets = (
        len(config.detector_model_list)
        * len(config.particle_list)
        * len(config.theta_list)
        * len(config.momentum_list)
    )
    # number of parallel jobs with same parameter combination/set
    n_jobs_per_para_set = ceil(
        config.N_EVTS / config.N_EVTS_PER_JOB
    )  # Nevts is lower limit
    # total number of jobs, can be printed for debugging/information
    n_jobs = n_jobs_per_para_set * n_para_sets

    # ===========================
    # Directory Setup and Checks
    # ===========================

    # Define directories for input and output
    directory_jobs = (
        config.rec_condor_dir
        / f"{config.particle_list[0]}_{config.detector_model_list[0]}"
    )
    sim_eos_dir = config.data_dir / f"{config.detector_model_list[0]}" / "SIM"  # input
    rec_eos_dir = config.data_dir / f"{config.detector_model_list[0]}" / "REC"  # output

    # Enable output checks
    CHECK_OUTPUT = True  # Set to True to enable checks, False to disable
    # It will check if the ouputs exist and contain correct number of events
    # if not it will send job to rerun reconstruction

    # Check if the directory exists and exit if it does
    if directory_jobs.exists():
        print(
            f"Error: Directory '{directory_jobs}' already exists and should not be overwritten."
        )
        sys.exit(1)

    # Create output directories if they don't exist
    rec_eos_dir.mkdir(parents=True, exist_ok=True)
    directory_jobs.mkdir(parents=True, exist_ok=True)

    # =======================
    # Reconstruction Job Creation
    # =======================

    # Create all possible combinations
    import itertools

    iter_of_combined_variables = itertools.product(
        config.theta_list,
        config.momentum_list,
        config.particle_list,
        config.detector_model_list,
    )

    NEED_TO_CREATE_SCRIPTS = False

    for theta, momentum, part, dect in iter_of_combined_variables:
        for task_index in range(n_jobs_per_para_set):

            output_file_name_parts = [
                f"REC_{dect}",
                f"{part}",
                f"{theta}_deg",
                f"{momentum}_GeV",
                f"{config.N_EVTS_PER_JOB}_evts",
                f"{task_index}",
            ]
            output_file_name = "_".join(output_file_name_parts)

            input_file_name_parts = [
                f"SIM_{dect}",
                f"{part}",
                f"{theta}_deg",
                f"{momentum}_GeV",
                f"{config.N_EVTS_PER_JOB}_evts",
                f"{task_index}",
            ]
            input_file_path = Path("_".join(input_file_name_parts)).with_suffix(
                ".edm4hep.root"
            )
            input_file = sim_eos_dir / part / input_file_path

            # Check if the input file exists
            if not input_file.exists():
                print(f"Error: Input file {input_file} does not exist. Skipping job.")
                continue
            # Check if the output file already exists and has correct Nb of events
            output_dir = rec_eos_dir / part
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = (output_dir / output_file_name).with_suffix(".edm4hep.root")

            # FIXME: Issue #4
            if CHECK_OUTPUT and output_file.exists():
                root_file = ROOT.TFile(fspath(output_file), "READ")
                events_tree = root_file.Get("events")
                if events_tree and events_tree.GetEntries() == config.N_EVTS_PER_JOB:
                    root_file.Close()
                    continue
                root_file.Close()
            NEED_TO_CREATE_SCRIPTS = True

            # Create aida output Dir
            output_dir_aida = output_dir / "aida_outputs"
            output_dir_aida.mkdir(exist_ok=True)

            arguments = (
                f" --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/{config.detector_model_list[0]}/{config.detector_model_list[0]}.xml"
                + " --inputFiles "
                + fspath(input_file)
                + " --outputBasename  "
                + fspath(output_file_name)
                + " --trackingOnly"
                + " -n "
                + str(config.N_EVTS_PER_JOB)
            )
            command = f"k4run {config.rec_steering_file} " + arguments + " > /dev/null"

            # Write bash script for job execution
            bash_script = (
                "#!/bin/bash \n"
                f"source {config.setup} \n"
                "git clone https://github.com/key4hep/CLDConfig.git \n"  # FIXME: see issues
                "cd "
                + "CLDConfig/CLDConfig"  # FIXME: CLD should not be hardcoded
                + "\n"
                f"{command} \n"
                f"xrdcp {output_file_name}.edm4hep.root  root://eosuser.cern.ch/{output_dir} \n"
                f"xrdcp {output_file_name}_aida.root  root://eosuser.cern.ch/{output_dir_aida} \n"
            )
            bash_file_name_parts = [
                "bash_script",
                dect,
                part,
                f"{theta}_deg",
                f"{momentum}_GeV",
                str(task_index),
            ]
            bash_file_path = (
                directory_jobs / "_".join(bash_file_name_parts)
            ).with_suffix(".sh")

            with open(bash_file_path, "w", encoding="utf-8") as bash_file:
                bash_file.write(bash_script)
                bash_file.close()

    if not NEED_TO_CREATE_SCRIPTS:
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
    condor_file_path = directory_jobs / "condor_script.sub"
    with open(condor_file_path, "w", encoding="utf-8") as condor_file:
        condor_file.write(condor_script)
        condor_file.close()

    # ====================
    # Submit Job to Condor
    # ====================
    system(
        "cd " + fspath(directory_jobs) + "; condor_submit condor_script.sub"
    )  # FIXME: use subprocess instead?


if __name__ == "__main__":
    main()
