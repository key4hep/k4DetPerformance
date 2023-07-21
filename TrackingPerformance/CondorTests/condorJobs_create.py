#!/usr/bin/env python

import os
import argparse
import subprocess
import time;
ts = time.time()

#thetaList_         = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
#momentumList_      = [ "1", "2", "5", "10", "20", "50", "100", "200"]
#particleList_      = [ "mu", "e", "pi"]
thetaList_         = ["10", "20"]
momentumList_      = [ "1"]#, "2"]
particleList_      = [ "mu"]
DetectorModelList_ = [ "FCCee_o1_v04"]
Nevts_             = "10"
runningDirectory = "/afs/cern.ch/user/g/gasadows/CondorTests/"
OutputDirectory = "/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/FCCee_o1_v04/SIM/"
SteeringFile = "/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/fcc_steer.py"
setup = "/cvmfs/sw.hsf.org/key4hep/setup.sh"

for dect in DetectorModelList_ :
    for part in  particleList_ :
        for theta in thetaList_ :
            for momentum in momentumList_ :
                time.sleep(1)
                seed = str(time.time()%1000)
                arguments = "-DetectorModel " + dect + " -Nevts " + Nevts_ + " -Particle " + part + " -Momentum " + momentum + " -Theta " + theta + " -Seed " + seed + " -OutputPath " + OutputDirectory + " -SteeringFile " + SteeringFile
                command = "python run_ddsim.py " + arguments
                print(command)
                #subprocess.run(["python", "run_ddsim.py"])
                directory_jobs = "CondorJobs/Jobs_DetectorModel_" + dect +  "_Nevts_" + Nevts_ +  "_Particle_" +  part +  "_Momentum_" + momentum +  "_Theta_" +  theta + "_Seed_" + seed
                os.system("mkdir " + directory_jobs)
                print(directory_jobs)
                bash_file = directory_jobs + "/bash_script.sh"
                with open(bash_file, "w") as file:
                    file.write("#!/bin/bash \n")
                    file.write("source " + setup + "\n")
                    file.write("cd " + runningDirectory + directory_jobs + "\n")
                    #file.write("pwd\n")
                    file.write(command+"\n")
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
                    #file2.write("+JobFlavour = \"microcentury\" \n")
                    #file2.write("+JobFlavour = \"longlunch\" \n")
                    file2.write("queue \n")
                    file2.close()
                os.system("cp run_ddsim.py " + directory_jobs + "/.")
                os.system("cd "+ directory_jobs + "; condor_submit condor_script.sub")


