
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


             # RP2MC
              # the MC particle matched to the reco'ed particle :
               .Define("MC_matched_to_reco",   "ReconstructedParticle2MC::getRP2MC_matched( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle )")

              # Kinematics reco'ed
               .Define("Reco_pdg_RP2MC",       "ReconstructedParticle::get_type( ReconstructedParticles )")
               .Define("Reco_pt_RP2MC",        "ReconstructedParticle::get_pt( ReconstructedParticles )") 
               .Define("Reco_theta_RP2MC",     "ReconstructedParticle::get_theta_deg( ReconstructedParticles )")
               .Define("Reco_phi_RP2MC",       "ReconstructedParticle::get_phi_deg( ReconstructedParticles )") 
               .Define("Reco_e_RP2MC",         "ReconstructedParticle::get_e( ReconstructedParticles )") 
               .Define("Reco_tlv_RP2MC",       "ReconstructedParticle::get_tlv( ReconstructedParticles )")

              # Kinematics MC
               .Define("MC_pdg_RP2MC",         "MCParticle::get_pdg( MC_matched_to_reco )")
               .Define("MC_pt_RP2MC",          "MCParticle::get_pt( MC_matched_to_reco )")
               .Define("MC_theta_RP2MC",       "MCParticle::get_theta_deg( MC_matched_to_reco )")
               .Define("MC_phi_RP2MC",         "MCParticle::get_phi_deg( MC_matched_to_reco )")
               .Define("MC_e_RP2MC",           "MCParticle::get_e( MC_matched_to_reco )")
               .Define("MC_tlv_RP2MC",         "MCParticle::get_tlv( MC_matched_to_reco )")

             # MC2RP
              # the MC particle matched to the reco'ed particle :
               .Define("RP_matched_to_mc",   "ReconstructedParticle2MC::getMC2RP_matched( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle )")

              # Kinematics reco'ed
               .Define("Reco_pdg_MC2RP",       "ReconstructedParticle::get_type( RP_matched_to_mc )")
               .Define("Reco_pt_MC2RP",        "ReconstructedParticle::get_pt( RP_matched_to_mc )") 
               .Define("Reco_theta_MC2RP",     "ReconstructedParticle::get_theta_deg( RP_matched_to_mc )")
               .Define("Reco_phi_MC2RP",       "ReconstructedParticle::get_phi_deg( RP_matched_to_mc )") 
               .Define("Reco_e_MC2RP",         "ReconstructedParticle::get_e( RP_matched_to_mc )") 
               .Define("Reco_tlv_MC2RP",       "ReconstructedParticle::get_tlv( RP_matched_to_mc )") 

              # Kinematics MC
               .Define("MC_pdg_MC2RP",         "MCParticle::get_pdg( Particle )")
               .Define("MC_pt_MC2RP",          "MCParticle::get_pt( Particle )")
               .Define("MC_theta_MC2RP",       "MCParticle::get_theta_deg( Particle )")
               .Define("MC_phi_MC2RP",         "MCParticle::get_phi_deg( Particle )")
               .Define("MC_e_MC2RP",           "MCParticle::get_e( Particle )")
               .Define("MC_tlv_MC2RP",         "MCParticle::get_tlv( Particle )")

        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
    # ====== MC Particles
        "MC_pdg_RP2MC", 
        "MC_pt_RP2MC",
        "MC_theta_RP2MC", 
        "MC_phi_RP2MC",
        "MC_e_RP2MC",
        "MC_tlv_RP2MC",

        "MC_pdg_MC2RP", 
        "MC_pt_MC2RP",
        "MC_theta_MC2RP", 
        "MC_phi_MC2RP",
        "MC_e_MC2RP",
        "MC_tlv_MC2RP",

    # ====== Reconstructed Particles
        "Reco_pdg_RP2MC",
        "Reco_pt_RP2MC",
        "Reco_theta_RP2MC", 
        "Reco_phi_RP2MC",  
        "Reco_e_RP2MC",
        "Reco_tlv_RP2MC",  

        "Reco_pdg_MC2RP",
        "Reco_pt_MC2RP",
        "Reco_theta_MC2RP", 
        "Reco_phi_MC2RP",  
        "Reco_e_MC2RP",
        "Reco_tlv_MC2RP",

        ]
        return branchList
