#!/usr/bin/env python

import os
import subprocess

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
            print(f"running FCCAnalyses with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

            command = [
                "fccanalysis", "run",
                    "FullSim/TrackingPerformance/CLD_pref_getTree.py",
                    "--output",
                    f"/eos/user/g/gasadows/Output/TrackingPerformance/Analysis/{Particle}_{theta}deg_{momentum}GeV_1000evt.root",
                    "--files-list",
                    f"/eos/user/g/gasadows/Output/TrackingPerformance/REC/REC_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root",
            ]

            subprocess.run(command)#, stdout=subprocess.DEVNULL)


