#!/usr/bin/env python

import os
import ROOT  
import argparse
import subprocess
import time;
ts = time.time()    # Get current timestamp for unique identifiers

# Lists of parameters for reconstruction
thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
momentumList_      = [ "1", "2", "5", "10", "20", "50", "100", "200"]
particleList_      = [ "mu"]#, "e", "pi"]

DetectorModelList_ = [ "CLD_o2_v05"] 
Nevts_             = "10000"
ResVDX_UV_ = ['0.001']    #default ['0.003']

# Directories and files for input and output
InputDirectory = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/SIM/"
SteeringFile = "/afs/cern.ch/user/g/gasadows/CLDConfig/CLDConfig/CLDReconstruction_VXDargs.py"
#SteeringFile = "/afs/cern.ch/user/g/gasadows/CLDConfig/CLDConfig/CLDReconstruction.py"
setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh"
CLDdir = "/afs/cern.ch/user/g/gasadows/CLDConfig"
EosDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModelList_[0]}/REC/VXD_1mic"
EosDir_aida = EosDir+"/aida_outputs"

# Enable output checks
check_output = True  # Set to True to enable checks, False to disable
                     # It will check if the ouputs exist and contain correct number of events
                     # if not it will send job to rerun reconstruction

# Create output directories if they don't exist
for directory in [EosDir, EosDir_aida]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Run Reconstruction on Condor    
for dect in DetectorModelList_ :
    for part in  particleList_ :
        for theta in thetaList_ :
            for momentum in momentumList_ :

                outputFileName = "REC_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts"

                inputFile= os.path.join(InputDirectory, "SIM_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts_edm4hep.root")   
                #input_file= os.path.join(InputDirectory, "SIMTest_" + dect + "_" + part + "_" + theta + "_deg_" + momentum + "_GeV_" + Nevts_ + "_evts.slcio")

                # Check if the input file exists
                if not os.path.exists(inputFile):
                    print(f"Error: Input file {inputFile} does not exist. Skipping job.")
                    continue 
                # Check if the output file already exists and has correct Nb of events
                output_file = EosDir +"/"+ outputFileName + "_edm4hep.root"
                if check_output and os.path.exists(output_file):
                    root_file = ROOT.TFile(output_file, "READ")
                    events_tree = root_file.Get("events")
                    if events_tree:
                        if events_tree.GetEntries() == int(Nevts_):
                            root_file.Close()
                            continue
                    root_file.Close()

                time.sleep(1)
                seed = str(time.time()%1000)
                arguments = f" --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/{DetectorModelList_[0]}/{DetectorModelList_[0]}.xml --inputFiles " + inputFile + " --outputBasename  " + outputFileName+ f" --VXDDigitiserResUV={ResVDX_UV_[0]}" + " --trackingOnly" + " -n " + Nevts_
                command = f"k4run {SteeringFile} " + arguments + " > /dev/null"
                print(command)

                # Set up job directories and files
                directory_jobs = "CondorJobs/Jobs_DetectorModel_" + dect +  "_Nevts_" + Nevts_ +  "_Particle_" +  part +  "_Momentum_" + momentum +  "_Theta_" +  theta
                os.system("mkdir " + directory_jobs)
                print(directory_jobs)
                bash_file = directory_jobs + "/bash_script.sh"

                # Write bash script for job execution
                with open(bash_file, "w") as file:
                    file.write("#!/bin/bash \n")
                    file.write("source "+ setup + "\n")
                    file.write("cp -rf " + CLDdir + " ." + "\n")
                    file.write("cd " + "CLDConfig/CLDConfig" + "\n")
                    file.write("pwd \n") 
                    #file.write("ls \n") 
                    file.write(command +"\n")
                    file.write("cp "+ outputFileName + "_edm4hep.root" + "  " + EosDir +"\n")
                    file.write("cp "+ outputFileName + "_aida.root" + "  " + EosDir_aida +"\n")

                    # Copy output file with retry logic
                    output_file = outputFileName + "_edm4hep.root"
                    eos_output_path = os.path.join(EosDir, output_file)
                    file.write(f"copy_success=0\n")
                    file.write(f"for attempt in 1 2 3 4 5\n")
                    file.write("do\n")
                    file.write(f"    cp {output_file} {EosDir}\n")
                    file.write(f"    if [ -s {eos_output_path} ]; then\n")
                    file.write("        echo 'Copy successful'\n")
                    file.write("        copy_success=1\n")
                    file.write("        break\n")
                    file.write("    else\n")
                    file.write("        echo 'Copy failed, retrying...'\n")
                    file.write("        sleep 10\n")
                    file.write("    fi\n")
                    file.write("done\n")
                    file.write("if [ $copy_success -ne 1 ]; then\n")
                    file.write("    echo 'Max copy attempts reached. Task failed.'\n")
                    file.write("    exit 1\n")
                    file.write("fi\n")
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
                    #file2.write("+JobFlavour = \"longlunch\" \n")    # 2 hours
                    file2.write("+JobFlavour = \"workday\" \n")      # 8 hours
                    file2.write("queue \n")
                    file2.close()

                # Submit job to Condor
                os.system("cd "+ directory_jobs + "; condor_submit condor_script.sub")



