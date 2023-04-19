# FullSim

## Simulation

```
source /cvmfs/sw.hsf.org/key4hep/setup.sh

git clone https://github.com/iLCSoft/CLICPerformance.git

cd CLICPerformance/fcceeConfig/
```

```
ddsim --compactFile $LCGEO/FCCee/compact/FCCee_o2_v02/FCCee_o2_v02.xml --inputFiles /eos/home-g/gasadows/genFiles/ee_Zmumu_91.hepmc --numberOfEvents 10000 --steeringFile fcc_steer.py --outputFile /eos/home-g/gasadows/Output/Zmumu/SIM/Zmumu_91_10000ev_SIM_edm4hep.root
```

## Reconstruction

fccRec_e4h_input.py file [here](https://github.com/gaswk/FullSim/blob/main/fccRec_e4h_input.py)

```
k4run fccRec_e4h_input.py  --EventDataSvc.input /eos/home-g/gasadows/Output/Zmumu/SIM/Zmumu_91_10000ev_SIM_edm4hep.root  -n 10000

```

## Analysis
Follow instructions here [FCCAnalyses](https://github.com/HEP-FCC/FCCAnalyses)

```

```
fccanalysis run Zmumu/analysis_Zmumu.py  --test --nevents 10000 --output /eos/home-g/gasadows/Output/Zmumu/Analysis/Zmumu.root
```
