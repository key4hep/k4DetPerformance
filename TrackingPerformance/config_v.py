"""
Victors config file for ILD FCCee models
"""

from pathlib import Path

# define environment setup script path
stable = Path("/cvmfs/sw.hsf.org/key4hep/setup.sh")
nightlies = Path("/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh")
setup = nightlies  # choose either stable or nightlies


# ==========================
# define base directories
# ==========================

# those files are available to job
baseAFSDir = Path("/afs/cern.ch/user/") / "v/vschwan/promotion"
# not directly available to job, only for storing purposes
baseEOSDir = Path("/eos/") / "home-v/vschwan/promotion"

# define directory to store output
dataDir = baseEOSDir / "data"
# define dirs
SIMcondorDir = baseAFSDir / "sim" / "condor_jobs"
RECcondorDir = baseAFSDir / "rec" / "condor_jobs"
# detector specific
# FIXME: extract following from dict based on detectorModel var?
detectorDIR = baseAFSDir / "ILDConfig" / "StandardConfig" / "production"
sim_steering_file = detectorDIR / "TPC_debug_muon_steer.py"
rec_steering_file = detectorDIR / "ILDReconstruction.py"


# ==========================
# Job Parameters Initialisation
# ==========================

Nevts_ = 1  # lower limit (rounding might be necessary)
Nevts_per_job = 1  # Set the desired number of events per job
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
detectorModelList = ["ILD_l5_v11"]
detModPaths = {"ILD_l5_v11": Path("ILD/compact/ILD_l5_v11/ILD_l5_v11.xml")}
# Define lists of parameters for reconstruction
thetaList_ = [10]  # , 20 , 30, 40, 50, 60, 70, 80, 89
momentumList_ = [1]  # , 2 , 5, 10, 20, 50, 100, 200
# momentumList_ = [1, 10, 100]
particleList_ = ["mu"]  # ,"e" ,"pi"]
