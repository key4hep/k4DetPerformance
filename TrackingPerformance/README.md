Instruction to reproduce this [plot](https://github.com/gaswk/FullSim/blob/main/TrackingPerformance/plots/TEST.png)

### Setup
```
source /cvmfs/sw.hsf.org/key4hep/setup.sh

git clone https://github.com/iLCSoft/CLICPerformance.git
```

### Simulation
```
. ./FullSim/TrackingPerformance/Simulation.sh
```

### Reconstruction
```
. ./FullSim/TrackingPerformance/Reconstruction.sh
```

### Analysis
Clone this fork of [FCCAnalyses](https://github.com/gaswk/FCCAnalyses) and follow instructions here:

```
git clone https://github.com/gaswk/FCCAnalyses.git

cd FCCAnalyses

source ./setup.sh
mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j4
cd ..
```

Then run the following script:
```
. ./FullSim/TrackingPerformance/Analysis.sh
```

### Plotting
```
python FullSim/TrackingPerformance/CLDprefPlot.py
```
