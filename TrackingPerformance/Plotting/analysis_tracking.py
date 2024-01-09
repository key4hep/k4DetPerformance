# Lists of parameters
ParticleList = ["mu"]#, "e", "pi"]
#ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
ThetaList = ["89"]
MomentumList = ["1", "10", "100"]
#MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]
DetectorModel = ["CLD_o2_v05"]  #["FCCee_o1_v04"]  ["CLD_o2_v05"]  ["CLD_o3_v01"]
Nevts = "10000"

# Dictionary to generate process names and output filenames for different parameters combinations
processList = {
    f"REC_{DetectorModel[0]}_{particle}_{theta}_deg_{momentum}_GeV_{Nevts}_evts_edm4hep":{"output":f"{particle}_{theta}deg_{momentum}GeV_{Nevts}evts"}
     for particle in ParticleList for theta in ThetaList for momentum in MomentumList}

# Output and input directories
outputDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel[0]}/analysis/"
inputDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/{DetectorModel[0]}/REC/mu"

# Optional: ncpus, default is 4, -1 uses all cores available
nCPUS = -1

#USER DEFINED CODE
import ROOT
ROOT.gInterpreter.Declare("""
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
""")
ROOT.gInterpreter.Declare("#include <marlinutil/HelixClass_double.h>")
#END USER DEFINED CODE

# List of variables to analyse
varList = ["pt", "d0", "z0", "phi0", "omega", "tanLambda", "p", "phi", "theta"]
varList2 = ["pt", "p"]

class RDFanalysis():

    def analysers(df):
        df2 = (df

               .Alias("MCTrackAssociations0", "_SiTracksMCTruthLink_rec.index")
               .Alias("MCTrackAssociations1", "_SiTracksMCTruthLink_sim.index")
               .Alias("SiTracks_Refitted_1", "_SiTracks_Refitted_trackStates")

               .Define("GunParticle_index", "MCParticles.generatorStatus == 1")
               .Define("GunParticle", "MCParticles[GunParticle_index][0]")

               .Define("trackStates_IP", "SiTracks_Refitted_1[SiTracks_Refitted_1.location == 1]") 
               .Define("MC2TrackIndex", "MCTruthTrackIndex(MCTrackAssociations0, MCTrackAssociations1, MCParticles)")
               .Define("GunParticleTrackIndex", "MC2TrackIndex[GunParticle_index][0]")
               .Define("GunParticleTSIP", "trackStates_IP[GunParticleTrackIndex]") 

               .Define("MatchedGunParticle_1", "MCParticles[MC2TrackIndex != -1]")
               .Define("MatchedGunParticle", "FCCAnalyses::MCParticle::sel_genStatus(1) (MatchedGunParticle_1)")

               .Define("trackData", "SiTracks_Refitted[GunParticleTrackIndex]")

              # Helix calculations and definitions
               .Define("GunParticleTSIPHelix", "auto h = HelixClass_double(); h.Initialize_Canonical(GunParticleTSIP.phi, GunParticleTSIP.D0, GunParticleTSIP.Z0, GunParticleTSIP.omega, GunParticleTSIP.tanLambda, 2); return h;")
               .Define("reco_pt", "GunParticleTSIPHelix.getPXY()")
               .Define("reco_d0", "GunParticleTSIP.D0")
               .Define("reco_z0", "GunParticleTSIP.Z0")
               .Define("reco_phi0", "GunParticleTSIP.phi")
               .Define("reco_omega", "GunParticleTSIP.omega")
               .Define("reco_tanLambda", "GunParticleTSIP.tanLambda")
               .Define("reco_pvec", "auto p = GunParticleTSIPHelix.getMomentum(); return ROOT::Math::XYZVector(p[0], p[1], p[2]);")
               .Define("reco_p", "reco_pvec.R()") 
               .Define("reco_phi", "reco_pvec.Phi()")
               .Define("reco_theta", "reco_pvec.Theta()")

               .Define("GunParticleMCMom", "std::vector<double> v = {GunParticle.momentum.x, GunParticle.momentum.y, GunParticle.momentum.z}; return v;")
               .Define("GunParticleMCPos", "std::vector<double> v = {GunParticle.vertex.x, GunParticle.vertex.y, GunParticle.vertex.z}; return v;")
               .Define("GunParticleMCHelix", "auto h = HelixClass_double(); h.Initialize_VP(GunParticleMCPos.data(), GunParticleMCMom.data(), -1, 2); return h;")
               .Define("true_pt", "GunParticleMCHelix.getPXY()")
               .Define("true_d0", "GunParticleMCHelix.getD0()")
               .Define("true_z0", "GunParticleMCHelix.getZ0()")
               .Define("true_phi0", "GunParticleMCHelix.getPhi0()")
               .Define("true_omega", "GunParticleMCHelix.getOmega()")
               .Define("true_tanLambda", "GunParticleMCHelix.getTanLambda()")
               .Define("true_pvec", "ROOT::Math::XYZVector(GunParticleMCMom[0], GunParticleMCMom[1], GunParticleMCMom[2])")
               .Define("true_p", "true_pvec.R()") 
               .Define("true_phi", "true_pvec.Phi()")
               .Define("true_theta", "true_pvec.Theta()")

              ## MatchedGunParticle
               #.Define("MatchedGunParticleMCMom", "std::vector<double> v = {MatchedGunParticle.momentum.x[0], MatchedGunParticle.momentum.y[0], MatchedGunParticle.momentum.z[0]}; return v;")
               #.Define("MatchedGunParticleMCPos", "std::vector<double> v = {MatchedGunParticle.vertex.x[0], MatchedGunParticle.vertex.y[0], MatchedGunParticle.vertex.z[0]}; return v;")
               #.Define("MatchedGunParticleMCHelix", "auto h = HelixClass_double(); h.Initialize_VP(MatchedGunParticleMCPos.data(), MatchedGunParticleMCMom.data(), -1, 2); return h;")
               #.Define("true_pt_matched", "MatchedGunParticleMCHelix.getPXY()")
               #.Define("true_pvec_matched", "ROOT::Math::XYZVector(MatchedGunParticleMCMom[0], MatchedGunParticleMCMom[1], MatchedGunParticleMCMom[2])")
               #.Define("true_p_matched", "true_pvec_matched.R()") 

               .Define("chi2_trk", "trackData.chi2")
               .Define("ndf_trk", "trackData.ndf")
               .Define("chi2_over_ndf", "chi2_trk / ndf_trk")
               .Filter("chi2_over_ndf < 10 ")
        )

        for v in varList:
            df2 = df2.Define(f"delta_{v}", f"reco_{v} - true_{v}")
            df2 = df2.Filter(f"std::isfinite(delta_{v})")
           # Remove fake tracks
            df2 = df2.Filter(f"abs( (reco_pt - true_pt) / true_pt) <= 0.20")
            df2 = df2.Filter(f"abs( (reco_phi - true_phi) / true_phi) <= 0.20 ")
            df2 = df2.Filter(f"abs( (reco_theta - true_theta) / true_theta) <= 0.20 ")
        if "phi0" in varList:
           # Correct phi wrap around
            df2 = df2.Redefine("delta_phi0", "delta_phi0 < -ROOT::Math::Pi() ? delta_phi0 + 2 * ROOT::Math::Pi() : delta_phi0")

        return df2

    def output():
        branchList = []
        branchList += [f"reco_{v}" for v in varList]
        branchList += [f"true_{v}" for v in varList]
        branchList += [f"delta_{v}" for v in varList]
        #branchList += [f"true_{v}_matched" for v in varList2]
        branchList += ["chi2_over_ndf"]
        return branchList
