"""
Victors config file for ILD FCCee models
"""

from pathlib import Path

# define environment setup script path
stable = Path("/cvmfs/sw.hsf.org/key4hep/setup.sh")
nightlies = Path("/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh")
setup = nightlies  # choose either stable or nightlies

# False: filepath_edm4hep.root; False: filepath.edm4hep.root
EDM4HEP_SUFFIX_WITH_UNDERSCORE = False

# ==========================
# define base directories
# ==========================

# those files are available to job
base_afs_dir = Path("/afs/cern.ch/user") / "v/vschwan/promotion"
# not directly available to job, only for storing purposes
base_eos_dir = Path("/eos/user") / "v/vschwan/promotion"

# define directory to store output
data_dir = base_eos_dir / "data"
# define dirs
sim_condor_dir = base_afs_dir / "sim" / "condor_jobs"
rec_condor_dir = base_afs_dir / "rec" / "condor_jobs"
# detector specific
# FIXME: extract following from dict based on detectorModel var?
detector_dir = base_afs_dir / "ILDConfig" / "StandardConfig" / "production"
sim_steering_file = detector_dir / "TPC_debug_muon_steer.py"
rec_steering_file = detector_dir / "ILDReconstruction.py"


# ==========================
# Job Parameters Initialisation
# ==========================

N_EVTS = 1  # lower limit (rounding might be necessary)
N_EVTS_PER_JOB = 1  # Set the desired number of events per job
JOB_FLAVOR = "espresso"
# Job flavours:
#   espresso     = 20 minutes
#   microcentury = 1 hour
#   longlunch    = 2 hours
#   workday      = 8 hours
#   tomorrow     = 1 day
#   testmatch    = 3 days
#   nextweek     = 1 week


# ==========================
# Parameters Initialisation
# ==========================
# FIXME: Should this be a list? Often only element 0 accessed
detector_model_list = ["ILD_l5_v11"]
det_mod_paths = {"ILD_l5_v11": Path("ILD/compact/ILD_l5_v11/ILD_l5_v11.xml")}
# Define lists of parameters for reconstruction
theta_list = [10]  # , 20 , 30, 40, 50, 60, 70, 80, 89
momentum_list = [1]  # , 2 , 5, 10, 20, 50, 100, 200
# momentumList_ = [1, 10, 100]
particle_list = ["mu"]  # ,"e" ,"pi"]
