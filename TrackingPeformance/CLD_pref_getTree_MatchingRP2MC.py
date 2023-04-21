
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

              # Reconstructed particle (e-)
               .Define("RecoPart",  "ReconstructedParticle::sel_type(11, false) ( ReconstructedParticles )")

               # their index in the LooseSelectedPandoraPFOs collection :
               .Define("index_RecoPart",  "ReconstructedParticle::get_indices( RecoPart, ReconstructedParticles )")

              # indices for Reco - MC matching. Collection #56 = LooseSelectedPandoraPFOs,  collection #41 = EfficientMCParticles
               .Define("indices_RP2MC",   "ReconstructedParticle2MC::getRP2MC_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, ReconstructedParticles )")
               .Define("indices_MC2RP",   "ReconstructedParticle2MC::getMC2RP_index_bycollID( 56, 41 ) ( MCRecoAssociations0, MCRecoAssociations1, mcreco0CollID, mcreco1CollID, Particle )")

              # remove pathological events
               .Define("index0" ,  "return index_RecoPart[0] ;")
               .Define("idxsize",       "return indices_RP2MC.size(); ")

               .Define("ind",        "return indices_RP2MC[ index_RecoPart[0] ];")
               .Define("emcsize",   "return EfficientMCParticles.size(); ")

               .Filter(" ind >= 0 ")

              # the MC particle matched to the reco'ed particle :
               .Define("MC_matched",  " return EfficientMCParticles.at( indices_RP2MC[ index_RecoPart[0] ] ) ;" )

              # Kinematics reco'ed
               .Define("Reco_p",       "ReconstructedParticle::get_p(RecoPart)") 
               .Define("Reco_pt",      "ReconstructedParticle::get_pt(RecoPart)") 
               .Define("Reco_eta",     "ReconstructedParticle::get_eta(RecoPart)")
               .Define("Reco_theta",   "ReconstructedParticle::get_theta_deg(RecoPart)")
               .Define("Reco_phi",     "ReconstructedParticle::get_phi_deg(RecoPart)") 

              # Kinematics MC. I use an intermediate vector in order to make use of the methods from MCParticle :-(
               .Define("v_MC_matched", " ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( MC_matched); return v; ")
               .Define("MC_p",           "MCParticle::get_p( v_MC_matched )")
               .Define("MC_pt",          "MCParticle::get_pt( v_MC_matched )")
               .Define("MC_eta",         "MCParticle::get_eta( v_MC_matched )")
               .Define("MC_theta",       "MCParticle::get_theta_deg( v_MC_matched )")
               .Define("MC_phi",         "MCParticle::get_phi_deg( v_MC_matched )")


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
