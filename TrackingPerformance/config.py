from os.path import join

# define base directory
baseDir = "/eos/home-v/vschwan/promotion/"
# define directory to store output
dataDir = join(baseDir, "data/")
SIMcondorDir = join(dataDir, "sim/condor_jobs/")
sim_steering_file = "/eos/home-v/vschwan/promotion/ILDConfig/StandardConfig/production/TPC_debug_muon_steer.py"

# ==========================
# Job Parameters Initialisation
# ==========================

Nevts_ = "300"
Nevt_per_job = "100"  # Set the desired number of events per job

# ==========================
# Parameters Initialisation
# ==========================
detectorModel = ["ILD_l5_v11"]
detModPaths = {"ILD_l5_v11": "ILD/compact/ILD_l5_v11/ILD_l5_v11.xml"}
# Define lists of parameters for reconstruction
thetaList_ = ["10", "20"]  # , "30", "40", "50", "60", "70", "80", "89"
momentumList_ = ["1", "2"]  # , "5", "10", "20", "50", "100", "200"
# momentumList_ = ["1", "10", "100"]
particleList_ = ["mu"]  # ,"e" ,"pi"]
