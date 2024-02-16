# FullSim

## Setup

source key4hep stable
```
source /cvmfs/sw.hsf.org/key4hep/setup.sh
```
source key4hep nightlies
```
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh
```

```
git clone https://github.com/key4hep/CLDConfig.git

cd CLDConfig/CLDConfig/
```

## Simulation

```
ddsim --compactFile $K4GEO/FCCee/CLD/compact/FCCee_o1_v04/FCCee_o1_v04.xml \
            --inputFiles ee_Zmumu_91.hepmc \
            --numberOfEvents 10000 --steeringFile fcc_steer.py \
            --outputFile Zmumu_91_10000ev_SIM_edm4hep.root
```

### Simulation with ParticleGun

```
ddsim --compactFile $K4GEO/FCCee/CLD/compact/FCCee_o1_v04/FCCee_o1_v04.xml \
      --outputFile outputSIM_edm4hep.root \
      --steeringFile cld_steer.py \
      --random.seed 0123456789 \
      --enableGun \
      --gun.particle mu- \
      --gun.energy "1*GeV" \
      --gun.distribution uniform \
      --gun.thetaMin "89*deg" \
      --gun.thetaMax "89*deg" \
      --crossingAngleBoost 0 \
      --numberOfEvents 10000
```


> **Note**
> 
> simulation output file format must be **_edm4hep.root** or **.slcio**

## Reconstruction

```
k4run CLDReconstruction.py --inputFiles outputSIM_edm4hep.root \
            --outputBasename outputREC \
            --VXDDigitiserResUV=0.001 \
            --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/CLD_o2_v05/CLD_o2_v05.xml \
            --trackingOnly \
            -n 100
```

