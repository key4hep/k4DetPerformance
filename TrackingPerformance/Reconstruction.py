#!/usr/bin/env python

import os
import subprocess

os.chdir("CLICPerformance/fcceeConfig/")

# Define lists
ParticleList = ["mu", "e", "pi"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]
ThetaList = ["10", "30", "50", "70", "89"]

# Get the value of $LCGEO
LCGEO = os.environ.get("LCGEO")

# Iterate over the lists
for Particle in ParticleList:
    for momentum in MomentumList:
        for theta in ThetaList:
            print(f"running k4run with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

            command = [
                "k4run",
                    "../../FullSim/fccRec_e4h_input.py",
                    "--EventDataSvc.input",
                    f"/eos/user/g/gasadows/Output/TrackingPerformance/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root",
                    "--filename.PodioOutput",
                    f"/eos/user/g/gasadows/Output/TrackingPerformance/REC/REC_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root",
                    "-n", "1000"
            ]

            subprocess.run(command, stdout=subprocess.DEVNULL)

import os

os.chdir("../..")

