#!/usr/bin/env python

import os
import argparse
import subprocess
import time;
ts = time.time()

thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
momentumList_      = [ "1", "2", "5", "10", "20", "50", "100", "200"]
#particleList_      = [ "mu", "e", "pi"]
#thetaList_         = ["10", "20"]
#momentumList_      = [ "1", "2"]
particleList_      = [ "mu"]
DetectorModelList_ = [ "FCCee_o1_v04"]
Nevts_             = "10000"
runningDirectory = "/afs/cern.ch/user/g/gasadows/CondorTests/"
InputDirectory = "/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/FCCee_o1_v04/SIM/"
OutputDirectory = "/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/FCCee_o1_v04/REC/"
runRecoDir = "/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/"
SteeringFile = "/afs/cern.ch/user/g/gasadows/FullSim/fccRec_lcio_input.py"
setup = "/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2023-06-22/x86_64-centos7-gcc12.2.0-opt/key4hep-stack/2023-06-22-4kk5ro/setup.sh"

for dect in DetectorModelList_ :
    for part in  particleList_ :
        for theta in thetaList_ :
            for momentum in momentumList_ :
                time.sleep(1)
                seed = str(time.time()%1000)
                arguments = "-DetectorModel " + dect + " -Nevts " + Nevts_ + " -Particle " + part + " -Momentum " + momentum + " -Theta " + theta + " -OutputPath " + OutputDirectory + " -InputPath " + InputDirectory + " -RunDir " + runRecoDir + " -CondorDir " + runningDirectory + " -SteeringFile " + SteeringFile
                command = "python run_reco.py " + arguments
                print(command)
                directory_jobs = "CondorJobs/Jobs_DetectorModel_" + dect +  "_Nevts_" + Nevts_ +  "_Particle_" +  part +  "_Momentum_" + momentum +  "_Theta_" +  theta
                os.system("mkdir " + directory_jobs)
                print(directory_jobs)
                bash_file = directory_jobs + "/bash_script.sh"
                with open(bash_file, "w") as file:
                    file.write("#!/bin/bash \n")
                    file.write("source "+ setup + "\n")
                    file.write("cd " + runningDirectory + directory_jobs + "\n")
                    file.write("pwd\n") #
                    file.write(command +"\n")
                    file.close()
                condor_file = directory_jobs + "/condor_script.sub"
                print(condor_file)
                with open(condor_file, "w") as file2:
                    file2.write("executable = bash_script.sh \n")
                    file2.write("arguments = $(ClusterId) $(ProcId) \n")
                    file2.write("output = output.$(ClusterId).$(ProcId).out \n")
                    file2.write("error = error.$(ClusterId).$(ProcId).err \n")
                    file2.write("log = log.$(ClusterId).log \n")
                    #file2.write("+JobFlavour = \"espresso\" \n")
                    file2.write("+JobFlavour = \"microcentury\" \n")
                    #file2.write("+JobFlavour = \"longlunch\" \n")
                    #file2.write("+JobFlavour = \"workday\" \n")
                    file2.write("queue \n")
                    file2.close()
                os.system("cp run_reco.py " + directory_jobs + "/.")
                os.system("cd "+ directory_jobs + "; condor_submit condor_script.sub")



