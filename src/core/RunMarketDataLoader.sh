#!/bin/bash

PROJECT_BASE_PATH='/home/ec2-user/canopy/canopy'
source $PROJECT_BASE_PATH/env/bin/activate


runProcess() {
  process=$1
  while true ; do
      echo "Starting process"
      python3 $process
      echo "Process Finished"
    done
}


cmd="python3 /home/ec2-user/canopy/canopy/src/DB/market_data/RunMarketDataWebSocketFallback.py"
$cmd &
runProcess /home/ec2-user/canopy/canopy/src/DB/market_data/RunMarketDataLoader.py