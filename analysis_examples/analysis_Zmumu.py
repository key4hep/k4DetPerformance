
testFile="/eos/user/g/gasadows/Output/Zmumu/REC/Zmumu_91_10000ev_REC.root"
#testFile="/eos/user/g/gasadows/Output/Zmumu/REC/Zmumu_240_10000ev_REC.root"

#Mandatory: RDFanalysis class where the use defines the operations on the TTreecode
class RDFanalysis():

    #__________________________________________________________
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        df2 = (
            df
               #.Define("start", ' std::cout << std::endl << " === New events " << std::endl;  return 1; ' )

               .Alias("ReconstructedParticles", "LooseSelectedPandoraPFOs")
               .Alias("Particle",               "EfficientMCParticles")

               .Alias("MCRecoAssociations0", "RecoMCTruthLink#0.index")
               .Alias("MCRecoAssociations1", "RecoMCTruthLink#1.index")
               .Alias("mcreco0CollID",       "RecoMCTruthLink#0.collectionID")
               .Alias("mcreco1CollID",       "RecoMCTruthLink#1.collectionID")

              # Reconstructed Muons
               .Define("RecoMuons",    "ReconstructedParticle::sel_type(13, true) ( ReconstructedParticles )")
               .Define("RecoMuMinus",  "ReconstructedParticle::sel_type(13, false) ( ReconstructedParticles )")
               .Define("RecoMuPlus",   "ReconstructedParticle::sel_type(-13, false) ( ReconstructedParticles )")

              # their index in the LooseSelectedPandoraPFOs collection :
               .Define("index_RecoMuMinus",  "ReconstructedParticle::get_indices( RecoMuMinus, ReconstructedParticles )")
               .Define("index_RecoMuPlus",   "ReconstructedParticle::get_indices( RecoMuPlus, ReconstructedParticles )")
               
              # indices for Reco - MC matching. Collection #56 = LooseSelectedPandoraPFOs,  collection #41 = EfficientMCParticles
               .Define("indices_RP2MC",   "ReconstructedParticle2MC::getRP2MC_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles )")
               .Define("indices_MC2RP",   "ReconstructedParticle2MC::getMC2RP_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, Particle )")

              # remove pathological events
               .Define("indexminus0" ,  "return index_RecoMuMinus[0] ;")
               .Define("indexplus0" ,   "return index_RecoMuPlus[0] ;")
               .Define("idxsize",       "return indices_RP2MC.size(); ")

               .Define("im",        "return indices_RP2MC[ index_RecoMuMinus[0] ];")
               .Define("ip",        "return indices_RP2MC[ index_RecoMuPlus[0] ];")
               .Define("emcsize",   "return EfficientMCParticles.size(); ")

               .Filter(" im >= 0 && ip >= 0 ")
               
              # demand a reco'ed mu+ and mu-
               .Filter( " index_RecoMuMinus.size() == 1 && index_RecoMuPlus.size() == 1 " ) 

              # the MC particle matched to the reco'ed mu- :
               .Define("MC_matched_to_minus",  " return EfficientMCParticles.at( indices_RP2MC[ index_RecoMuMinus[0] ] ) ;" )
               .Define("MC_matched_to_plus",   " return EfficientMCParticles.at( indices_RP2MC[ index_RecoMuPlus[0] ] ) ;" )

              # Kinematics reco'ed
               .Define("RecoMuMinus_p",       "ReconstructedParticle::get_p(RecoMuMinus)") 
               .Define("RecoMuMinus_pt",      "ReconstructedParticle::get_pt(RecoMuMinus)") 
               .Define("RecoMuMinus_eta",     "ReconstructedParticle::get_eta(RecoMuMinus)")
               .Define("RecoMuMinus_theta",   "ReconstructedParticle::get_theta(RecoMuMinus)")
               .Define("RecoMuMinus_phi",     "ReconstructedParticle::get_phi(RecoMuMinus)") #polar angle in the transverse plane phi
               .Define("RecoMuPlus_p",        "ReconstructedParticle::get_p(RecoMuPlus)")
               .Define("RecoMuPlus_pt",       "ReconstructedParticle::get_pt(RecoMuPlus)")
               .Define("RecoMuPlus_eta",      "ReconstructedParticle::get_eta(RecoMuPlus)")
               .Define("RecoMuPlus_theta",    "ReconstructedParticle::get_theta(RecoMuPlus)")
               .Define("RecoMuPlus_phi",      "ReconstructedParticle::get_phi(RecoMuPlus)") #polar angle in the transverse plane phi

             # Kinematics MC. I use an intermediate vector in order to make use of the methods from MCParticle :-(
               .Define("v_MC_matched_to_minus", " ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( MC_matched_to_minus ); return v; ")
               .Define("v_MC_matched_to_plus",  " ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( MC_matched_to_plus ); return v; ")
               .Define("MCMuMinus_p",           "MCParticle::get_p( v_MC_matched_to_minus )")
               .Define("MCMuMinus_pt",          "MCParticle::get_pt( v_MC_matched_to_minus )")
               .Define("MCMuMinus_eta",         "MCParticle::get_eta( v_MC_matched_to_minus )")
               .Define("MCMuMinus_theta",       "MCParticle::get_theta( v_MC_matched_to_minus )")
               .Define("MCMuMinus_phi",         "MCParticle::get_phi( v_MC_matched_to_minus )")
               .Define("MCMuPlus_p",            "MCParticle::get_p( v_MC_matched_to_plus )")
               .Define("MCMuPlus_pt",           "MCParticle::get_pt( v_MC_matched_to_plus )")
               .Define("MCMuPlus_eta",          "MCParticle::get_eta( v_MC_matched_to_plus )")
               .Define("MCMuPlus_theta",        "MCParticle::get_theta( v_MC_matched_to_plus )")
               .Define("MCMuPlus_phi",          "MCParticle::get_phi( v_MC_matched_to_plus )")

               ##########
               # DeltaR #
               ##########      
              # mu minus         
               .Define("DeltaR_muMinus",  "ReconstructedParticle2MC::get_DeltaR_pdg( 56, 41, 13 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle)" )  
              # mu plus
               .Define("DeltaR_muPlus",   "ReconstructedParticle2MC::get_DeltaR_pdg( 56, 41, -13 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles, Particle)" )  

               ##############
               # Z inv Mass #
               ##############
               .Define("Zmass",  "ReconstructedParticle::get_masstlv(RecoMuons)")

               #######################
               # Tracking Efficiency #
               ####################### 
             ## Pt
              # \DeltaPt = (Pt_reco - Pt_Gen)
               .Define("DeltaPt_muPlus",      " return ( (RecoMuPlus_pt.at(0) - MCMuPlus_pt.at(0)) ); ")
               .Define("DeltaPt_muMinus",     " return ( (RecoMuMinus_pt.at(0) - MCMuMinus_pt.at(0)) ); ")
              # \DeltaPt_p = (Pt_reco - Pt_Gen)/Pt_gen
               .Define("DeltaPt_pt_muPlus",   " return ( DeltaPt_muPlus/(MCMuPlus_pt.at(0)) ); ")
               .Define("DeltaPt_pt_muMinus",  " return ( DeltaPt_muMinus/(MCMuMinus_pt.at(0)) ); ")
              # \DeltaPt_p2 = (Pt_reco - Pt_Gen)/Pt^2_gen
               .Define("DeltaPt_pt2_muPlus",  " return ( DeltaPt_muPlus/(MCMuPlus_pt.at(0)*MCMuPlus_pt.at(0)) ); ")
               .Define("DeltaPt_pt2_muMinus", " return ( DeltaPt_muMinus/(MCMuMinus_pt.at(0)*MCMuMinus_pt.at(0)) ); ")

             ## P
              # \DeltaP = (P_reco - P_Gen)
               .Define("DeltaP_muPlus",     " return ( (RecoMuPlus_p.at(0) - MCMuPlus_p.at(0)) ); ")
               .Define("DeltaP_muMinus",    " return ( (RecoMuMinus_p.at(0) - MCMuMinus_p.at(0)) ); ")
              # \DeltaP_p = (P_reco - P_Gen)/P_gen
               .Define("DeltaP_p_muPlus",   " return ( DeltaP_muPlus/(MCMuPlus_p.at(0)) ); ")
               .Define("DeltaP_p_muMinus",  " return ( DeltaP_muMinus/(MCMuMinus_p.at(0)) ); ")
              # \DeltaP_p2 = (P_reco - P_Gen)/P^2_gen
               .Define("DeltaP_p2_muPlus",  " return ( DeltaP_muPlus/(MCMuPlus_p.at(0)*MCMuPlus_p.at(0)) ); ")
               .Define("DeltaP_p2_muMinus", " return ( DeltaP_muMinus/(MCMuMinus_p.at(0)*MCMuMinus_p.at(0)) ); ")

             ## theta
              # \Delta_theta = (theta_reco - theta_gen)
               .Define("DeltaTheta_muPlus",  " return ( (RecoMuPlus_theta.at(0) - MCMuPlus_theta.at(0)) ); ")
               .Define("DeltaTheta_muMinus", " return ( (RecoMuMinus_theta.at(0) - MCMuMinus_theta.at(0)) ); ")

             ## phi
              # \Delta_phi = (phi_reco - phi_gen)
               .Define("DeltaPhi_muPlus",   " return ( (RecoMuPlus_phi.at(0) - MCMuPlus_phi.at(0)) ); ")
               .Define("DeltaPhi_muMinus",  " return ( (RecoMuMinus_phi.at(0) - MCMuMinus_phi.at(0)) ); ")


        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
            #"start",
    # ====== MC Particles
      # mu minus
        "MCMuMinus_p",
        "MCMuMinus_pt",
        "MCMuMinus_theta",
        "MCMuMinus_phi",

      # mu plus
        "MCMuPlus_p",
        "MCMuPlus_pt",
        "MCMuPlus_theta",
        "MCMuPlus_phi",

    # ====== Reconstructed Particles
      # mu minus
        "RecoMuMinus_p", 
        "RecoMuMinus_pt",
        "RecoMuMinus_theta", 
        "RecoMuMinus_phi",
      
      # mu plus 
        "RecoMuPlus_p",
        "RecoMuPlus_pt",
        "RecoMuPlus_theta", 
        "RecoMuPlus_phi", 

    # ====== Z inv Mass
        "Zmass",

    # ====== Tracking Efficiency
        "DeltaPt_muPlus",
        "DeltaPt_muMinus",
        "DeltaPt_pt_muPlus",
        "DeltaPt_pt_muMinus",
        "DeltaPt_pt2_muPlus",
        "DeltaPt_pt2_muMinus",

        "DeltaP_muPlus",
        "DeltaP_muMinus",
        "DeltaP_p_muPlus",
        "DeltaP_p_muMinus",
        "DeltaP_p2_muPlus",
        "DeltaP_p2_muMinus",

        "DeltaTheta_muPlus",
        "DeltaTheta_muMinus",

        "DeltaPhi_muPlus",
        "DeltaPhi_muMinus",

    # ====== Matching
        "DeltaR_muMinus",
        "DeltaR_muPlus", 

    # ===== test indices
        "indices_RP2MC",
        "indices_MC2RP",

        ]
        return branchList
