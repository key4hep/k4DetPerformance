#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser(description="Script for plotting Detector Performances")
parser.add_argument("-DetectorModel", help="Detector model: FCCee_o1_v04 \n FCCee_o2_v02", required=True)
parser.add_argument("-Nevts", help="Number of events", required=True)
parser.add_argument("-Particle", help="particles: [mu, e, pi]", required=True)
parser.add_argument("-Momentum", help="momentum ", required=True)
parser.add_argument("-Theta", help="theta ", required=True)
parser.add_argument("-Seed", help="gen Seed ", required=True)
parser.add_argument("-OutputPath", help="Output file path", required=True)
parser.add_argument("-SteeringFile", help="Steering file", required=True)

args = parser.parse_args()

output_file = os.path.join(args.OutputPath, "SIMTest_" + args.DetectorModel + "_" + args.Particle + "_" + args.Theta + "_deg_" + args.Momentum + "_GeV_" + args.Nevts + "_evts.slcio")

command = (
    "ddsim --compactFile ${LCGEO}/FCCee/compact/" + args.DetectorModel + "/" + args.DetectorModel + ".xml "
    "--outputFile " + output_file + " "
    "--steeringFile " + args.SteeringFile + " "
    "--random.seed " + args.Seed + " "
    "--enableGun "
    "--gun.particle " + args.Particle + "- "
    "--gun.energy " + args.Momentum + "*GeV "
    "--gun.distribution uniform "
    "--gun.thetaMin " + args.Theta + "*deg "
    "--gun.thetaMax " + args.Theta + "*deg "
    "--crossingAngleBoost 0 "
    "--numberOfEvents " + args.Nevts
)

print(command)

os.system(command + " > /dev/null")


