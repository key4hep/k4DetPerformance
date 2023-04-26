
#testFile="/eos/user/g/gasadows/Output/Zmumu/REC/Zinclusive_91_100ev_REC.root"

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

              # Kinematics reco'ed
               .Define("Reco_pdg",       "ReconstructedParticle::get_type( ReconstructedParticles )")
               .Define("Reco_pt",        "ReconstructedParticle::get_pt( ReconstructedParticles )") 
               .Define("Reco_theta",     "ReconstructedParticle::get_theta_deg( ReconstructedParticles )")
               .Define("Reco_phi",       "ReconstructedParticle::get_phi_deg( ReconstructedParticles )") 
               .Define("Reco_e",         "ReconstructedParticle::get_e( ReconstructedParticles )") 
               .Define("Reco_tlv",       "ReconstructedParticle::get_tlv( ReconstructedParticles )")

              # Kinematics MC
               .Define("MC_pdg",         "MCParticle::get_pdg( Particle )")
               .Define("MC_pt",          "MCParticle::get_pt( Particle )")
               .Define("MC_theta",       "MCParticle::get_theta_deg( Particle )")
               .Define("MC_phi",         "MCParticle::get_phi_deg( Particle )")
               .Define("MC_e",           "MCParticle::get_e( Particle )")
               .Define("MC_tlv",         "MCParticle::get_tlv( Particle )")

             # RP2MC
              # the MC particle matched to the reco'ed particle :
               .Define("MC_matched_to_reco",   "ReconstructedParticle2MC::getRP2MC_matched( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle )")

              # Kinematics MC 
               .Define("Reco_MC_pdg",         "MCParticle::get_pdg( MC_matched_to_reco )")
               .Define("Reco_MC_pt",          "MCParticle::get_pt( MC_matched_to_reco )")
               .Define("Reco_MC_theta",       "MCParticle::get_theta_deg( MC_matched_to_reco )")
               .Define("Reco_MC_phi",         "MCParticle::get_phi_deg( MC_matched_to_reco )")
               .Define("Reco_MC_e",           "MCParticle::get_e( MC_matched_to_reco )")
               .Define("Reco_MC_tlv",         "MCParticle::get_tlv( MC_matched_to_reco )")

             # MC2RP
              # the reco particle matched to the MC particle :
               .Define("RP_matched_to_mc",   "ReconstructedParticle2MC::getMC2RP_matched( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle )")

              # Kinematics reco'ed
               .Define("MC_Reco_pdg",       "ReconstructedParticle::get_type( RP_matched_to_mc )")
               .Define("MC_Reco_pt",        "ReconstructedParticle::get_pt( RP_matched_to_mc )") 
               .Define("MC_Reco_theta",     "ReconstructedParticle::get_theta_deg( RP_matched_to_mc )")
               .Define("MC_Reco_phi",       "ReconstructedParticle::get_phi_deg( RP_matched_to_mc )") 
               .Define("MC_Reco_e",         "ReconstructedParticle::get_e( RP_matched_to_mc )") 
               .Define("MC_Reco_tlv",       "ReconstructedParticle::get_tlv( RP_matched_to_mc )") 

        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
    # ====== MC Particles
        "MC_pdg", 
        "MC_pt",
        "MC_theta", 
        "MC_phi",
        "MC_e",
        "MC_tlv",

        "Reco_MC_pdg", 
        "Reco_MC_pt",
        "Reco_MC_theta", 
        "Reco_MC_phi",
        "Reco_MC_e",
        "Reco_MC_tlv",

    # ====== Reconstructed Particles
        "Reco_pdg",
        "Reco_pt",
        "Reco_theta", 
        "Reco_phi",  
        "Reco_e",
        "Reco_tlv",  

        "MC_Reco_pdg",
        "MC_Reco_pt",
        "MC_Reco_theta", 
        "MC_Reco_phi",  
        "MC_Reco_e",
        "MC_Reco_tlv",

        ]
        return branchList
