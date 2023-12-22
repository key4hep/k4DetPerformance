#!/usr/bin/env python

import os
import ROOT 
import argparse
import subprocess
import time;
ts = time.time()    # Get current timestamp for unique identifiers

# Lists of parameters for simulation
thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
momentumList_      = ["1", "10", "100"]
particleList_      = [ "mu"]#, "e", "pi"]

DetectorModelList_ = [ "CLD_o2_v05"]
Nevts_             = "10000"

# Directories and files for input and output
runningDirectory = "/afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor"
SteeringFile = "/afs/cern.ch/user/g/gasadows/CLDConfig/CLDConfig/cld_steer.py"
setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/SIM/"

# Enable output checks
check_output = True  # Set to True to enable checks, False to disable
                     # It will check if the ouputs exist and contain correct number of events
                     # if not it will send job to rerun reconstruction

# Create EosDir if it does not exist
if not os.path.exists(EosDir):
    os.makedirs(EosDir)

# Run Simulation on Condor
for dect in DetectorModelList_ :
    for part in  particleList_ :
        for theta in thetaList_ :
            for momentum in momentumList_ :

                output_file = "SIM_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts_edm4hep.root"

                # Check if the output file already exists and has correct Nb of events
                output_file = EosDir +"/"+ output_file
                if check_output and os.path.exists(output_file):
                    root_file = ROOT.TFile(output_file, "READ")
                    events_tree = root_file.Get("events")
                    if events_tree:
                        if events_tree.GetEntries() == int(Nevts_):
                            #print(f"Output file {output_file} already exists and has correct Nb of events. Skipping job.")
                            root_file.Close()
                            continue
                    root_file.Close()
                
                time.sleep(1)
                seed = str(time.time()%1000)
                arguments = "-DetectorModel " + dect + " -Nevts " + Nevts_ + " -Particle " + part + " -Momentum " + momentum + " -Theta " + theta + " -Seed " + seed + " -OutputPath " + output_file + " -SteeringFile " + SteeringFile
                command = "python run_ddsim.py " + arguments
                print(command)

                # Set up job directories and files
                directory_jobs = "CondorJobs/Jobs_DetectorModel_" + dect +  "_Nevts_" + Nevts_ +  "_Particle_" +  part +  "_Momentum_" + momentum +  "_Theta_" +  theta + "_Seed_" + seed
                os.system("mkdir " + directory_jobs)
                print(directory_jobs)
                bash_file = directory_jobs + "/bash_script.sh"

                # Write bash script for job execution
                with open(bash_file, "w") as file:
                    file.write("#!/bin/bash \n")
                    file.write("source " + setup + "\n")
                    file.write("cp /afs/cern.ch/user/g/gasadows/FullSim/TrackingPerformance/Condor/run_ddsim.py . " + "\n")
                    #file.write("ls \n") 
                    #file.write("pwd\n")
                    file.write(command+"\n")
                    file.write("cp " + output_file + " " + EosDir + "\n")
                    file.close()

                # Write condor submission script
                condor_file = directory_jobs + "/condor_script.sub"
                print(condor_file)
                with open(condor_file, "w") as file2:
                    file2.write("executable = bash_script.sh \n")
                    file2.write("arguments = $(ClusterId) $(ProcId) \n")
                    file2.write("output = output.$(ClusterId).$(ProcId).out \n")
                    file2.write("error = error.$(ClusterId).$(ProcId).err \n")
                    file2.write("log = log.$(ClusterId).log \n")
                    #file2.write("+JobFlavour = \"microcentury\" \n") # 1 hour
                    file2.write("+JobFlavour = \"longlunch\" \n")    # 2 hours
                    #file2.write("+JobFlavour = \"workday\" \n")      # 8 hours
                    file2.write("queue \n")
                    file2.close()

                # Submit job to Condor
                os.system("cd "+ directory_jobs + "; condor_submit condor_script.sub")


