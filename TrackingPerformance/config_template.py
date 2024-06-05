"""
copy this template of a config file and adapt it to your needs
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
baseAFSDir = Path("/afs/cern.ch/user/") / "U/USER/CHANGE/PATH"  # FIXME
# not directly available to job, only for storing purposes
baseEOSDir = Path("/eos/") / "HOME-U/USER/CHANGE/PATH"  # FIXME

# define directory to store output
dataDir = baseEOSDir / "data"
# define dirs
SIMcondorDir = baseAFSDir / "sim" / "condor_jobs"
RECcondorDir = baseAFSDir / "rec" / "condor_jobs"
# detector specific
# FIXME: extract following from dict based on detectorModel var?
detectorDIR = baseAFSDir / "CHANGE" / "PATH"  # FIXME
sim_steering_file = detectorDIR / "CHANGE" / "PATH"  # FIXME
rec_steering_file = detectorDIR / "CHANGE" / "PATH"  # FIXME


# ==========================
# Job Parameters Initialisation
# ==========================

Nevts_ = 30  # lower limit (rounding might be necessary)
Nevts_per_job = 10  # Set the desired number of events per job
JOB_FLAVOR = "longlunch"
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
detectorModelList = ["detector_model_1"]
detModPaths = {"detector_model_1": Path("CHANGE/PATH")}  # FIXME
# Define lists of parameters for reconstruction
thetaList_ = [10, 20]  # , 30, 40, 50, 60, 70, 80, 89
momentumList_ = [1, 2]  # , 5, 10, 20, 50, 100, 200
# momentumList_ = [1, 10, 100]
particleList_ = ["mu"]  # ,"e" ,"pi"]
