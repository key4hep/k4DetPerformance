
testFile="/eos/user/g/gasadows/Output/Zmumu/REC/Zinclusive_91_100ev_REC.root"

#Mandatory: RDFanalysis class where the use defines the operations on the TTreecode
class RDFanalysis():

    #__________________________________________________________
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        df2 = (
            df

               .Alias("ReconstructedParticles", "LooseSelectedPandoraPFOs")
               .Alias("Particle",               "EfficientMCParticles")

               .Alias("MCRecoAssociations0", "RecoMCTruthLink#0.index")  #recind
               .Alias("MCRecoAssociations1", "RecoMCTruthLink#1.index")  #mcind
               .Alias("mcreco0CollID",       "RecoMCTruthLink#0.collectionID")
               .Alias("mcreco1CollID",       "RecoMCTruthLink#1.collectionID")


              # RP index in the LooseSelectedPandoraPFOs collection :
               .Define("index_Reco",  "ReconstructedParticle::get_indices( ReconstructedParticles, ReconstructedParticles )")
               
              # indices for Reco - MC matching. Collection #56 = LooseSelectedPandoraPFOs,  collection #41 = EfficientMCParticles
               .Define("indices_RP2MC",   "ReconstructedParticle2MC::getRP2MC_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles )")

              # the MC particle matched to the reco'ed particle :
               .Define("MC_matched_to_reco",   "ReconstructedParticle2MC::getRP2MC_index_matched( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle )")

              # Kinematics reco'ed
               .Define("Reco_pdg",       "ReconstructedParticle::get_type(ReconstructedParticles)")
               .Define("Reco_p",         "ReconstructedParticle::get_p(ReconstructedParticles)") 
               .Define("Reco_pt",        "ReconstructedParticle::get_pt(ReconstructedParticles)") 
               .Define("Reco_eta",       "ReconstructedParticle::get_eta(ReconstructedParticles)")
               .Define("Reco_theta",     "ReconstructedParticle::get_theta_deg(ReconstructedParticles)")
               .Define("Reco_phi",       "ReconstructedParticle::get_phi_deg(ReconstructedParticles)") 

              # Kinematics MC
               .Define("MC_pdg",         "MCParticle::get_pdg( MC_matched_to_reco )")
               .Define("MC_p",           "MCParticle::get_p( MC_matched_to_reco )")
               .Define("MC_pt",          "MCParticle::get_pt( MC_matched_to_reco )")
               .Define("MC_eta",         "MCParticle::get_eta( MC_matched_to_reco )")
               .Define("MC_theta",       "MCParticle::get_theta_deg( MC_matched_to_reco )")
               .Define("MC_phi",         "MCParticle::get_phi_deg( MC_matched_to_reco )")

        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
    # ====== MC Particles
        "MC_pdg",
        "MC_p", 
        "MC_pt",
        "MC_theta", 
        "MC_phi",

    # ====== Reconstructed Particles
        "Reco_pdg",
        "Reco_p", 
        "Reco_pt",
        "Reco_theta", 
        "Reco_phi",  

        ]
        return branchList
