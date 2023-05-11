#! /usr/bin/bash

# Define a string variable with a value
ParticleList="mu"  ##"mu e pi"
MomentumList="1 2 5 10 20 50 100 200"
ThetaList="10 30 50 70 89"

# Iterate the string variable using for loop
for Particle in $ParticleList; do
    for momentum in $MomentumList; do
        for theta in $ThetaList     ##{STRAT..END.STEP}
        do
            echo "running FCCAnalyis with Particle $Particle-, Theta = $theta deg, Momentum = $momentum Gev"

        fccanalysis run FullSim/TrackingPerformance/CLD_pref_getTree.py \
        --output /eos/user/g/gasadows/Output/TrackingPerformance/Analysis/test/$Particle-$theta-deg_$momentum-GeV_1000evt.root \
        --files-list /eos/user/g/gasadows/Output/TrackingPerformance/REC/REC_$Particle-$theta-deg_$momentum-GeV_1000evt_edm4hep.root  \
            #> /dev/null
        done    ##loop over theta
    done    ##loop over momentum
done  ##loop over particle
