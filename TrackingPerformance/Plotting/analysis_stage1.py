#ParticleList = ["mu", "e", "pi"]
ParticleList = ["mu"]
ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]
DetectorModel = ["FCCee_o1_v04"]
Nevts = "10000"

processList = {f"REC_{DetectorModel[0]}_resVXD_15mic_{particle}_{theta}_deg_{momentum}_GeV_{Nevts}_evts_edm4hep":{"output":f"{particle}_{theta}deg_{momentum}GeV_{Nevts}evts"} for particle in ParticleList for theta in ThetaList for momentum in MomentumList}
#print(processList)
outputDir = f"Output/{DetectorModel[0]}/stage1_15mic"

inputDir = f"/eos/user/g/gasadows/Output/TrackingPerformance/LCIO/{DetectorModel[0]}/REC/resVXD_15mic"

#nCPUS = 6
nCPUS = 1

#USER DEFINED CODE
import ROOT
ROOT.gInterpreter.Declare("""
ROOT::VecOps::RVec<int> MCTruthTrackIndex(ROOT::VecOps::RVec<int> trackIndex,
                                          ROOT::VecOps::RVec<int> mcIndex,
                                          ROOT::VecOps::RVec<edm4hep::MCParticleData> mc)
{
    ROOT::VecOps::RVec<int> res;
    res.resize(mc.size(), -1);

    for (size_t i = 0; i < trackIndex.size(); i++) {
        res[mcIndex[i]] = trackIndex[i];
    }
    return res;
}
""")
#END USER DEFINED CODE

class RDFanalysis():

    def analysers(df):
        df2 = (df
            .Alias("MCTrackAssociations0", "SiTracksMCTruthLink#0.index")
            .Alias("MCTrackAssociations1", "SiTracksMCTruthLink#1.index")
            .Define("GunParticle_index", "MCParticles.generatorStatus == 1")
            .Define("GunParticle", "MCParticles[GunParticle_index][0]")
            .Define("trackStates_IP", "SiTracks_Refitted_1[SiTracks_Refitted_1.location == 1]")
            .Define("MC2TrackIndex", "MCTruthTrackIndex(MCTrackAssociations0, MCTrackAssociations1, MCParticles)")
            .Define("GunParticleTrackIndex", "MC2TrackIndex[GunParticle_index][0]")
            .Define("GunParticleTSIP", "trackStates_IP[GunParticleTrackIndex]")
        )
        return df2

    def output():
        branchList = [
                "GunParticle",
                "GunParticleTSIP"
        ]
        return branchList