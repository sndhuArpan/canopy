#!/bin/bash



runProcess() {
  process=$1
  while true ; do
      echo "Starting process"
      /usr/local/bin/python3.9 $process
      echo "Process Finished"
    done
}


#cmd="/usr/local/bin/python3.9 /Users/Sandhu/canopy/canopy/src/DB/market_data/RunMarketDataWebSocketFallback.py"
#$cmd &
/usr/local/bin/python3.9 /Users/Sandhu/canopy/canopy/src/DB/market_data/RunMarketDataWebSocketFallback.py
#runProcess /Users/Sandhu/canopy/canopy/src/DB/market_data/RunMarketDataLoader.py