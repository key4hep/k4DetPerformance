#!/usr/bin/env python

import os
import subprocess
from multiprocessing import Pool
import argparse

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
output_directory_2 = f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/SIM/"
if not os.path.exists(output_directory_1):
    os.makedirs(output_directory_1)
if not os.path.exists(output_directory_2):
    os.makedirs(output_directory_2)

# Define lists
ParticleList = ["mu", "e", "pi"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]

# Create a function to process each combination of parameters
def process_combination(params):
    Particle, momentum, theta = params
    print(f"running ddsim with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

    command = [
        "ddsim",
        "--compactFile",
        f"{LCGEO}/FCCee/compact/FCCee_o1_v04/FCCee_o1_v04.xml",
        "--outputFile", f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_{args.Nevts}evts.slcio",
        "--steeringFile", "CLICPerformance/fcceeConfig/fcc_steer.py",
        "--random.seed", "0123456789",
        "--enableGun",
        "--gun.particle", f"{Particle}-",
        "--gun.energy", f"{momentum}*GeV",
        "--gun.distribution", "uniform",
        "--gun.thetaMin", f"{theta}*deg",
        "--gun.thetaMax", f"{theta}*deg",
        "--crossingAngleBoost", "0",
        "--numberOfEvents", f"{args.Nevts}"
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL)

    # Print completion message
    output_file = f"/eos/user/g/gasadows/Output/TrackingPerformance/{args.DetectorModel}/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_{args.Nevts}evts.slcio"
    print(f"File {output_file}  -----> finished processing")

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
