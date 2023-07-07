#!/usr/bin/env python

import os
import subprocess
from multiprocessing import Pool
import argparse

os.chdir("CLICPerformance/fcceeConfig/")

# Set Detector Model and numder of events
#Nevts = "1000"
#DetectorModel = "FCCee_o1_v04"
# Define the command-line argument parser
parser = argparse.ArgumentParser(description="Script for plotting Detector Performances")
parser.add_argument("-DetectorModel", help="Detector model: FCCee_o1_v04 \n FCCee_o2_v02 \n FCCee_o1_v04_lcio", required=True)
parser.add_argument("-Nevts", help="Number of events", required=True)
args = parser.parse_args()

# Get the name of the current Python script
script_filename = os.path.basename(__file__)
print(f"-----> running {script_filename} with Detector Model = {args.DetectorModel}, Nevts = {args.Nevts}")

# Get the value of $LCGEO
LCGEO = os.environ.get("LCGEO")

# Create the output directories if they don't exist
output_directory_1 = f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/"
output_directory_2 = f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/REC/"
if not os.path.exists(output_directory_1):
    os.makedirs(output_directory_1)
if not os.path.exists(output_directory_2):
    os.makedirs(output_directory_2)

# Define lists
ParticleList = ["mu"]    #["mu", "e", "pi"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]

# Create a function to process each combination of parameters
def process_combination(params):
    Particle, momentum, theta = params
    print(f"running k4run with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

    input_file = f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_{args.Nevts}evts.slcio"

    if not os.path.exists(input_file):
        print(f"/!\ Warning: Input file {input_file} does not exist. Skipping it.")
        return

    command = [
        "k4run",
        "../../FullSim/fccRec_lcio_input.py",
        "--LcioEvent.Files",
        input_file,
        "--filename.PodioOutput",
        f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/REC/REC_{Particle}_{theta}deg_{momentum}GeV_{args.Nevts}evts_edm4hep.root",
        "-n", f"{args.Nevts}"
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL)

    # Print completion message
    print(f"Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev -----> finished processing.")

# Create a list of combinations of parameters
combinations = []
for Particle in ParticleList:
    for momentum in MomentumList:
        if momentum in ["1", "10", "100"]:
            ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
        else:
            ThetaList = ["10", "30", "50", "70", "89"]

        for theta in ThetaList:
            combinations.append((Particle, momentum, theta))

# Create a pool of worker processes
pool = Pool()

# Process combinations in parallel
pool.map(process_combination, combinations)

# Close the pool and wait for the processes to finish
pool.close()
pool.join()

import os

os.chdir("../..")
