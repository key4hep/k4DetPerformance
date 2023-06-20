#!/usr/bin/env python

import os
import subprocess

DetectorModel = "FCCee_o2_v02"
Nevts = "1000"

# Get the name of the current Python script
script_filename = os.path.basename(__file__)
print(f"-----> running {script_filename} with Detector Model = {DetectorModel}, Nevts = {Nevts}")

# Define lists
ParticleList = ["mu", "e", "pi"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]

# Iterate over the lists
for Particle in ParticleList:
    for momentum in MomentumList:
        if momentum in ["1", "10", "100"]:
            ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
        else:
            ThetaList = ["10", "30", "50", "70", "89"]

        for theta in ThetaList:
            print(f"running fccanalysis with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

            input_file = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel}/REC/REC_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root"

            if not os.path.exists(input_file):
                print(f"/!\ Warning: Input file {input_file} does not exist. Skipping it.")
                continue

            command = [
                   "fccanalysis", "run",
                    "FullSim/TrackingPerformance/CLD_pref_getTree.py",
                    "--output",
                    f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel}/Analysis/{Particle}_{theta}deg_{momentum}GeV_1000evt.root",
                    "--files-list",
                    input_file,
                   ]

            subprocess.run(command)#, stdout=subprocess.DEVNULL)