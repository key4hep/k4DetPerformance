
### Setup
```
source /cvmfs/sw.hsf.org/key4hep/setup.sh

git clone https://github.com/iLCSoft/CLICPerformance.git
```

### Simulation
```
python ./FullSim/TrackingPerformance/Simulation.py
```
Simulation of single particle (e-, pi-, mu-) with fixed energy and theta, steps for 10, 30, 50, 70 and 89 deg in theta and 1, 2, 5, 10, 20, 50, 100, 200 GeV in energy.

### Reconstruction
fccRec_e4h_input.py file [here](https://github.com/gaswk/FullSim/blob/main/fccRec_e4h_input.py)
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
python FullSim/TrackingPerformance/CLDprefPlot_track.py
```
