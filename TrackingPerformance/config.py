from pathlib import Path

# define environment setup script path
stable = Path("/cvmfs/sw.hsf.org/key4hep/setup.sh")
nightlies = Path("/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh")
setup = nightlies  # choose either stable or nightlies

# define base directory
baseDir = Path("/eos/home-v/vschwan/promotion/")

# define directory to store output and subdirs
dataDir = baseDir / "data"
SIMcondorDir = dataDir / "sim" / "condor_jobs"
RECcondorDir = dataDir / "rec" / "condor_jobs"
ILDDir = baseDir / "ILDConfig" / "StandardConfig" / "production"
sim_steering_file = ILDDir / "TPC_debug_muon_steer.py"
rec_steering_file = ILDDir / "ILDReconstruction.py"

# ==========================
# Job Parameters Initialisation
# ==========================

Nevts_ = "300"
Nevt_per_job = "100"  # Set the desired number of events per job

# ==========================
# Parameters Initialisation
# ==========================
detectorModel = ["ILD_l5_v11"]
detModPaths = {"ILD_l5_v11": Path("ILD/compact/ILD_l5_v11/ILD_l5_v11.xml")}
# Define lists of parameters for reconstruction
thetaList_ = ["10", "20"]  # , "30", "40", "50", "60", "70", "80", "89"
momentumList_ = ["1", "2"]  # , "5", "10", "20", "50", "100", "200"
# momentumList_ = ["1", "10", "100"]
particleList_ = ["mu"]  # ,"e" ,"pi"]
