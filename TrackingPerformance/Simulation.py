#!/usr/bin/env python

import os
import subprocess

DetectorModel = "FCCee_o1_v04"
Nevts = "1000"

# Get the name of the current Python script
script_filename = os.path.basename(__file__)
print(f"-----> running {script_filename} with Detector Model = {DetectorModel}, Nevts = {Nevts}")

# Get the value of $LCGEO
LCGEO = os.environ.get("LCGEO")

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
            print(f"running ddsim with Particle {Particle}-, Theta = {theta} deg, Momentum = {momentum} Gev")

            command = [
                "ddsim",
                "--compactFile",
                f"{DetectorModel}/{DetectorModel}.xml",
                "--outputFile", f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel}/SIM/SIM_{Particle}_{theta}deg_{momentum}GeV_1000evt_edm4hep.root",
                "--steeringFile", "CLICPerformance/fcceeConfig/fcc_steer.py",
                "--random.seed", "0123456789",
                "--enableGun",
                "--gun.particle", f"{Particle}-",
                "--gun.energy", f"{momentum}*GeV",
                "--gun.distribution", "uniform",
                "--gun.thetaMin", f"{theta}*deg",
                "--gun.thetaMax", f"{theta}*deg",
                "--crossingAngleBoost", "0",
                "--numberOfEvents", f"{Nevts}"
            ]

            subprocess.run(command, stdout=subprocess.DEVNULL)
