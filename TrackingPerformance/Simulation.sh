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
            echo "running ddsim with Particle $Particle-, Theta = $theta deg, Momentum = $momentum Gev"

            ddsim --compactFile $LCGEO/FCCee/compact/FCCee_o2_v02/FCCee_o2_v02.xml \
                        --outputFile /eos/user/g/gasadows/Output/TrackingPerformance/SIM/SIM_$Particle-$theta-deg_$momentum-GeV_1000evt_edm4hep.root \
                        --steeringFile CLICPerformance/fcceeConfig/fcc_steer.py \
                        --random.seed 0123456789 \
                        --enableGun \
                        --gun.particle $Particle- \
                        --gun.energy "$momentum*GeV" \
                        --gun.distribution uniform \
                        --gun.thetaMin "$theta*deg" \
                        --gun.thetaMax "$theta*deg" \
                        --crossingAngleBoost 0 \
                        --numberOfEvents 1000  \
                        > /dev/null
            done    ##loop over theta
    done    ##loop over momentum
done  ##loop over particle
