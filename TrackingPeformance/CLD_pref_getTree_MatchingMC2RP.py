
testFile="/afs/cern.ch/user/g/gasadows/CLICPerformance/fcceeConfig/TrackingPerformance/rec_output/REC_e_10-GeV_90-deg_edm4hep.root"

#Mandatory: RDFanalysis class where the use defines the operations on the TTreecode
class RDFanalysis():

    #__________________________________________________________
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        df2 = (
            df
               .Alias("ReconstructedParticles", "LooseSelectedPandoraPFOs")
               .Alias("Particle",               "EfficientMCParticles")

               .Alias("MCRecoAssociations0", "RecoMCTruthLink#0.index")
               .Alias("MCRecoAssociations1", "RecoMCTruthLink#1.index")
               .Alias("mcreco0CollID",       "RecoMCTruthLink#0.collectionID")
               .Alias("mcreco1CollID",       "RecoMCTruthLink#1.collectionID")

              # Generated particle
               .Define("MCPart", "FCCAnalyses::MCParticle::sel_genStatus(1)(Particle)") #gen status==1 means final state particle (FS)

               # their index in the LooseSelectedPandoraPFOs collection :
               .Define("index_MCPart",  "MCParticle::get_indices( MCPart, Particle )")

              # indices for Reco - MC matching. Collection #56 = LooseSelectedPandoraPFOs,  collection #41 = EfficientMCParticles
               .Define("indices_RP2MC",   "ReconstructedParticle2MC::getRP2MC_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles )")
               .Define("indices_MC2RP",   "ReconstructedParticle2MC::getMC2RP_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, Particle )")

              # the RP particle matched to the MC particle :
               .Define("RP_matched",  " return LooseSelectedPandoraPFOs.at( indices_MC2RP[ index_MCPart[0] ] ) ;" )

              # Kinematics reco'ed
               .Define("v_RP_matched", " ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> v; v.push_back( RP_matched); return v; ")
               .Define("Reco_p",       "ReconstructedParticle::get_p(v_RP_matched)") 
               .Define("Reco_pt",      "ReconstructedParticle::get_pt(v_RP_matched)") 
               .Define("Reco_eta",     "ReconstructedParticle::get_eta(v_RP_matched)")
               .Define("Reco_theta",   "ReconstructedParticle::get_theta_deg(v_RP_matched)")
               .Define("Reco_phi",     "ReconstructedParticle::get_phi_deg(v_RP_matched)") 

              # Kinematics MC
               .Define("MC_p",           "MCParticle::get_p( MCPart )")
               .Define("MC_pt",          "MCParticle::get_pt( MCPart )")
               .Define("MC_eta",         "MCParticle::get_eta( MCPart )")
               .Define("MC_theta",       "MCParticle::get_theta_deg( MCPart )")
               .Define("MC_phi",         "MCParticle::get_phi_deg( MCPart )")


        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
    # ====== MC Particles
        "MC_p",
        "MC_pt",
        "MC_theta",
        "MC_phi",

    # ====== Reconstructed Particles
        "Reco_p", 
        "Reco_pt",
        "Reco_theta", 
        "Reco_phi",

        ]
        return branchList
