### Running CLD Full Simulation and Reconstruction on Condor

To execute simulation and reconstruction processes for CLD Full Simulation on Condor, follow these steps. Before running the scripts, ensure to set the desired variables within them according to your requirements.

**Important Note:** The values for **Nevts** (Total Number of Events) and **Nevt_per_job** (Number of Events per Job) should be identical for both Simulation and Reconstruction processes.

##### Run Simulation
Start by running the simulation process. Set the necessary variables within the **condorJobs_sim.py** script.
```
python condorJobs_sim.py
```

##### Run Reconstruction
After completing the simulation, proceed with the reconstruction process. Similar to the simulation step, ensure that the variables in the **condorJobs_reco.py** script are correctly set.
```
python condorJobs_reco.py
```

Make sure to verify the consistency of **Nevts** and **Nevt_per_job* between both scripts. Also, check that each step is completed successfully before moving to the next. If any issues arise, recheck the variable settings in the scripts to ensure they match your simulation and reconstruction needs.