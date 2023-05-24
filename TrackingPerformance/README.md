Instruction to reproduce this plot:

![momentum_resolution_mu](https://github.com/gaswk/FullSim/assets/116810451/a3029300-0857-45fb-bcb5-6478d8f341d7)

### Setup
```
source /cvmfs/sw.hsf.org/key4hep/setup.sh

git clone https://github.com/iLCSoft/CLICPerformance.git
```

### Simulation
```
python ./FullSim/TrackingPerformance/Simulation.py
```
Simulation of single particle with fixed energy and theta, steps for 10, 30, 50, 70 and 89 deg in theta and 1, 2, 5, 10, 20, 50, 100, 200 GeV in energy.

### Reconstruction
```
python ./FullSim/TrackingPerformance/Reconstruction.py
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
python ./FullSim/TrackingPerformance/Analysis.py
```

### Plotting
```
python FullSim/TrackingPerformance/CLDprefPlot.py
```
