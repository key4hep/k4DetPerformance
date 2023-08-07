#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser(description="Script for plotting Detector Performances")
parser.add_argument("-Nevts", help="Number of events", required=True)
parser.add_argument("-OutputPath", help="Output file path", required=True)
parser.add_argument("-InputPath", help="Input file path", required=True)         
parser.add_argument("-SteeringFile", help="Steering file", required=True)       

args = parser.parse_args()

#________________________________________________________________________________

if not os.path.exists(args.InputPath):
    print(f"/!\ Warning: Input file {args.InputPath} does not exist. Skipping it.")
else:
    command = (
        "k4run " + args.SteeringFile +  
        " --LcioEvent.Files " + args.InputPath + 
        " --filename.PodioOutput " + args.OutputPath +
        " -n " + args.Nevts
    )
    print(command)

    os.system(command + " > /dev/null")



