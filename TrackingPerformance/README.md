Instruction to reproduce this plot:

![TEST](https://github.com/gaswk/FullSim/assets/116810451/b96e29b2-cdb6-4aa3-a203-2a82ee0bd30d)

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
