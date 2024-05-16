import sys
from os.path import dirname, abspath, join

# Add the project root directory to the sys.path
project_root = dirname(dirname(abspath(__file__)))
# Append the project root to sys.path if not already present
if project_root not in sys.path:
    sys.path.append(project_root)

# import config
import config

# ==========================
# Parameters Initialisation
# ==========================
# Define lists of parameters for reconstruction
thetaList_ = config.thetaList_
momentumList_ = config.momentumList_
particleList_ = config.particleList_

DetectorModel = config.detectorModel
Nevts_ = config.Nevts_
Nevt_per_job = config.Nevt_per_job  # Set the desired number of events per job

# Output and input directories
outputDir = join(config.dataDir, f"TrackingPerformance/{DetectorModel[0]}/analysis/")
inputDir = join(config.dataDir, f"TrackingPerformance/{DetectorModel[0]}/REC/")


processList = {
    f"REC_{DetectorModel[0]}_{particle}_{theta}_deg_{momentum}_GeV_{Nevts_per_job}_evts_{i}_edm4hep": {
        "output": f"{particle}_{theta}deg_{momentum}GeV_{Nevts_per_job}evts_{i}"
    }
    for particle in ParticleList
    for theta in ThetaList
    for momentum in MomentumList
    for i in range(int(Nevts) // int(Nevts_per_job))
}

# Optional: ncpus, default is 4, -1 uses all cores available
nCPUS = -1

# USER DEFINED CODE
import ROOT

ROOT.gInterpreter.Declare(
    """
ROOT::VecOps::RVec<int> MCTruthTrackIndex(ROOT::VecOps::RVec<int> trackIndex,
                                          ROOT::VecOps::RVec<int> mcIndex,
                                          ROOT::VecOps::RVec<edm4hep::MCParticleData> mc)
{
    ROOT::VecOps::RVec<int> res;
    res.resize(mc.size(), -1);

    for (size_t i = 0; i < mcIndex.size(); i++) {
        res[trackIndex[i]] = mcIndex[i];
    }
    return res;
}
"""
)
ROOT.gInterpreter.Declare("#include <marlinutil/HelixClass_double.h>")
# END USER DEFINED CODE

# List of variables to analyse
varList = ["pt", "d0", "z0", "phi0", "omega", "tanLambda", "p", "phi", "theta"]


class RDFanalysis:

    def analysers(df):
        df2 = (
            df.Alias("MCTrackAssociations0", "_SiTracksMCTruthLink_rec.index")
            .Alias("MCTrackAssociations1", "_SiTracksMCTruthLink_sim.index")
            .Alias("SiTracks_Refitted_1", "_SiTracks_Refitted_trackStates")
            .Define("GunParticle_index", "MCParticles.generatorStatus == 1")
            .Define("GunParticle", "MCParticles[GunParticle_index][0]")
            .Define(
                "trackStates_IP",
                "SiTracks_Refitted_1[SiTracks_Refitted_1.location == 1]",
            )
            .Define(
                "MC2TrackIndex",
                "MCTruthTrackIndex(MCTrackAssociations0, MCTrackAssociations1, MCParticles)",
            )
            .Define("GunParticleTrackIndex", "MC2TrackIndex[GunParticle_index][0]")
            .Define("GunParticleTSIP", "trackStates_IP[GunParticleTrackIndex]")
            .Define("MatchedGunParticle_1", "MCParticles[MC2TrackIndex != -1]")
            .Define(
                "MatchedGunParticle",
                "FCCAnalyses::MCParticle::sel_genStatus(1) (MatchedGunParticle_1)",
            )
            .Define("trackData", "SiTracks_Refitted[GunParticleTrackIndex]")
            # Helix calculations and definitions
            .Define(
                "GunParticleTSIPHelix",
                "auto h = HelixClass_double(); h.Initialize_Canonical(GunParticleTSIP.phi, GunParticleTSIP.D0, GunParticleTSIP.Z0, GunParticleTSIP.omega, GunParticleTSIP.tanLambda, 2); return h;",
            )
            .Define("reco_pt", "GunParticleTSIPHelix.getPXY()")
            .Define("reco_d0", "GunParticleTSIP.D0")
            .Define("reco_z0", "GunParticleTSIP.Z0")
            .Define("reco_phi0", "GunParticleTSIP.phi")
            .Define("reco_omega", "GunParticleTSIP.omega")
            .Define("reco_tanLambda", "GunParticleTSIP.tanLambda")
            .Define(
                "reco_pvec",
                "auto p = GunParticleTSIPHelix.getMomentum(); return ROOT::Math::XYZVector(p[0], p[1], p[2]);",
            )
            .Define("reco_p", "reco_pvec.R()")
            .Define("reco_phi", "reco_pvec.Phi()")
            .Define("reco_theta", "reco_pvec.Theta()")
            .Define(
                "GunParticleMCMom",
                "std::vector<double> v = {GunParticle.momentum.x, GunParticle.momentum.y, GunParticle.momentum.z}; return v;",
            )
            .Define(
                "GunParticleMCPos",
                "std::vector<double> v = {GunParticle.vertex.x, GunParticle.vertex.y, GunParticle.vertex.z}; return v;",
            )
            .Define(
                "GunParticleMCHelix",
                "auto h = HelixClass_double(); h.Initialize_VP(GunParticleMCPos.data(), GunParticleMCMom.data(), -1, 2); return h;",
            )
            .Define("true_pt", "GunParticleMCHelix.getPXY()")
            .Define("true_d0", "GunParticleMCHelix.getD0()")
            .Define("true_z0", "GunParticleMCHelix.getZ0()")
            .Define("true_phi0", "GunParticleMCHelix.getPhi0()")
            .Define("true_omega", "GunParticleMCHelix.getOmega()")
            .Define("true_tanLambda", "GunParticleMCHelix.getTanLambda()")
            .Define(
                "true_pvec",
                "ROOT::Math::XYZVector(GunParticleMCMom[0], GunParticleMCMom[1], GunParticleMCMom[2])",
            )
            .Define("true_p", "true_pvec.R()")
            .Define("true_phi", "true_pvec.Phi()")
            .Define("true_theta", "true_pvec.Theta()")
            .Define("chi2_trk", "trackData.chi2")
            .Define("ndf_trk", "trackData.ndf")
            .Define("chi2_over_ndf", "chi2_trk / ndf_trk")
            .Filter("chi2_over_ndf < 10 ")
            # Remove fake tracks
            .Filter("abs( (reco_pt - true_pt) / true_pt) <= 0.20")
            .Filter("abs( (reco_phi - true_phi) / true_phi) <= 0.20 ")
            .Filter("abs( (reco_theta - true_theta) / true_theta) <= 0.20 ")
            .Define("num_reconstructed_tracks", "trackStates_IP.size() > 0 ? 1 : 0")
        )

        for v in varList:
            df2 = df2.Define(f"delta_{v}", f"reco_{v} - true_{v}")
            df2 = df2.Filter(f"std::isfinite(delta_{v})")
        if "phi0" in varList:
            # Correct phi wrap around
            df2 = df2.Redefine(
                "delta_phi0",
                "delta_phi0 < -ROOT::Math::Pi() ? delta_phi0 + 2 * ROOT::Math::Pi() : delta_phi0",
            )

        return df2

    def output():
        branchList = []
        branchList += [f"reco_{v}" for v in varList]
        branchList += [f"true_{v}" for v in varList]
        branchList += [f"delta_{v}" for v in varList]
        branchList += ["chi2_over_ndf"]
        branchList += ["num_reconstructed_tracks"]
        return branchList
