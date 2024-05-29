# FullSim

The main documentation is in the subdirectories.

## Setup

source either key4hep stable

```sh
source /cvmfs/sw.hsf.org/key4hep/setup.sh
```

or source key4hep nightlies

```sh
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh
```

```sh
git clone https://github.com/key4hep/CLDConfig.git

cd CLDConfig/CLDConfig/
```

## Simulation

```sh
ddsim --compactFile $K4GEO/FCCee/CLD/compact/CLD_o2_v06/CLD_o2_v06.xml \
            --inputFiles ee_Zmumu_91.hepmc \
            --numberOfEvents 10000 --steeringFile fcc_steer.py \
            --outputFile Zmumu_91_10000ev_SIM_edm4hep.root
```

### Simulation with ParticleGun

```sh
ddsim --compactFile $K4GEO/FCCee/CLD/compact/CLD_o2_v06/CLD_o2_v06.xml \
      --outputFile outputSIM.edm4hep.root \
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
> simulation output file format must be **.edm4hep.root** or **.slcio**

## Reconstruction

```sh
k4run CLDReconstruction.py --inputFiles outputSIM_edm4hep.root \
            --outputBasename outputREC \
            --VXDDigitiserResUV=0.001 \
            --GeoSvc.detectors=$K4GEO/FCCee/CLD/compact/CLD_o2_v06/CLD_o2_v06.xml \
            --trackingOnly \
            -n 100
```
