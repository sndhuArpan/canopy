#!/bin/bash



runProcess() {
  process=$1
  while true ; do
      echo "Starting process"
      /usr/local/bin/python3.9 $process
      echo "Process Finished"
    done
}


cmd="runProcess /Users/Sandhu/canopy/canopy/src/DB/market_data/RunMarketDataWebSocketFallback.py"
$cmd &
runProcess /Users/Sandhu/canopy/canopy/src/DB/market_data/RunMarketDataLoader.py