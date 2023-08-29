#ParticleList = ["mu", "e", "pi"]
ParticleList = ["mu"]
ThetaList = ["10", "20", "30", "40", "50", "60", "70", "80", "89"]
MomentumList = ["1", "2", "5", "10", "20", "50", "100", "200"]   
Nevts = "10000"

processList = {f"{particle}_{theta}deg_{momentum}GeV_{Nevts}evts":{} for particle in ParticleList for theta in ThetaList for momentum in MomentumList}
#print(processList)
outputDir = "Output/FCCee_o1_04/stage2_3mic"

inputDir = "Output/FCCee_o1_04/stage1_3mic"

nCPUS = 1

#USER DEFINED CODE
import ROOT
ROOT.gSystem.Load("/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2023-05-30/x86_64-almalinux9-gcc11.3.1-opt/marlinutil/4bba4d10fc1c448213e83251f689370fc2d43c9e=develop-zhkc6e/lib/libMarlinUtil.so")
ROOT.gROOT.ProcessLine(".include /cvmfs/sw-nightlies.hsf.org/key4hep/releases/2023-05-30/x86_64-almalinux9-gcc11.3.1-opt/ced/56f3bc90862e7bd4fa5657e638cceea50b368ed7=develop-lhxqn2/include")
ROOT.gInterpreter.Declare("#include <marlinutil/HelixClass_double.h>")
#END USER DEFINED CODE

varList = ["pt", "d0", "z0", "phi0", "omega", "tanLambda", "p", "phi", "theta"]

class RDFanalysis():

    def analysers(df):
        df2 = (df
               .Define("GunParticleTSIPHelix", "auto h = HelixClass_double(); h.Initialize_Canonical(GunParticleTSIP.phi, GunParticleTSIP.D0, GunParticleTSIP.Z0, GunParticleTSIP.omega, GunParticleTSIP.tanLambda, 2); return h;")
               .Define("reco_pt", "GunParticleTSIPHelix.getPXY()")
               .Define("reco_d0", "GunParticleTSIP.D0")
               .Define("reco_z0", "GunParticleTSIP.Z0")
               .Define("reco_phi0", "GunParticleTSIP.phi")
               .Define("reco_omega", "GunParticleTSIP.omega")
               .Define("reco_tanLambda", "GunParticleTSIP.tanLambda")
               .Define("reco_pvec", "auto p = GunParticleTSIPHelix.getMomentum(); return ROOT::Math::XYZVector(p[0], p[1], p[2]);")
               .Define("reco_p", "reco_pvec.R()") # sorry I didn't choose this method name
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
               .Define("true_p", "true_pvec.R()") # sorry I didn't choose this method name
               .Define("true_phi", "true_pvec.Phi()")
               .Define("true_theta", "true_pvec.Theta()")
        )

        for v in varList:
            df2 = df2.Define(f"delta_{v}", f"reco_{v} - true_{v}")
            df2 = df2.Filter(f"std::isfinite(delta_{v})")
        if "phi0" in varList:
            # correct phi wrap around
            df2 = df2.Redefine("delta_phi0", "delta_phi0 < -ROOT::Math::Pi() ? delta_phi0 + 2 * ROOT::Math::Pi() : delta_phi0")

        return df2

    def output():
        branchList = []
        branchList += [f"reco_{v}" for v in varList]
        branchList += [f"true_{v}" for v in varList]
        branchList += [f"delta_{v}" for v in varList]
        #branchList += [f"delta_{v}_min" for v in varList]
        #branchList += [f"delta_{v}_max" for v in varList]
        return branchList