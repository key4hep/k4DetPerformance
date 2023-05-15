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
            print(f"running ddsim with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

            command = [
                "ddsim",
                "--compactFile",
                f"{LCGEO}/FCCee/compact/FCCee_o2_v02/FCCee_o2_v02.xml",
                "--outputFile", f"/eos/user/g/gasadows/Output/TrackingPerformance/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root",
                "--steeringFile", "CLICPerformance/fcceeConfig/fcc_steer.py",
                "--random.seed", "0123456789",
                "--enableGun",
                "--gun.particle", f"{Particle}-",
                "--gun.energy", f"{momentum}*GeV",
                "--gun.distribution", "uniform",
                "--gun.thetaMin", f"{theta}*deg",
                "--gun.thetaMax", f"{theta}*deg",
                "--crossingAngleBoost", "0",
                "--numberOfEvents", "1000"
            ]

            subprocess.run(command, stdout=subprocess.DEVNULL)
