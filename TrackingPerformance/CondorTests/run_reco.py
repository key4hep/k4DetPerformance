#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser(description="Script for plotting Detector Performances")
parser.add_argument("-DetectorModel", help="Detector model: FCCee_o1_v04 \n FCCee_o2_v02", required=True)
parser.add_argument("-Nevts", help="Number of events", required=True)
parser.add_argument("-Particle", help="particles : [mu, e, pi]", required=True)
parser.add_argument("-Momentum", help="momentum ", required=True)
parser.add_argument("-Theta", help="theta ", required=True)
parser.add_argument("-OutputPath", help="Output file path", required=True)
parser.add_argument("-InputPath", help="Input file path", required=True)        
parser.add_argument("-RunDir", help="running directory", required=True)         
parser.add_argument("-CondorDir", help="condor directory", required=True)       
parser.add_argument("-SteeringFile", help="Steering file", required=True)       

args = parser.parse_args()

#________________________________________________________________________________
os.chdir(args.RunDir)  

output_file = os.path.join(args.OutputPath, "RECTest_" + args.DetectorModel + "_" + args.Particle + "_" + args.Theta + "_deg_" + args.Momentum + "_GeV_" + args.Nevts + "_evts_edm4hep.root")

input_file= os.path.join(args.InputPath, "SIMTest_" + args.DetectorModel + "_" + args.Particle + "_" + args.Theta + "_deg_" + args.Momentum + "_GeV_" + args.Nevts + "_evts.slcio")

if not os.path.exists(input_file):
    print(f"/!\ Warning: Input file {input_file} does not exist. Skipping it.")
else:
    command = (
        "k4run " + args.SteeringFile +  
        " --LcioEvent.Files " + input_file + 
        " --filename.PodioOutput " + output_file +
        " -n " + args.Nevts
    )
    print(command)

    os.system(command + " > /dev/null")

os.chdir(args.CondorDir)  


