PROJECT_BASE_PATH='/home/ec2-user/canopy/canopy'
source $PROJECT_BASE_PATH/env/bin/activate

export PYTHONPATH=$PROJECT_BASE_PATH

python3 $PROJECT_BASE_PATH/src/core/alert_checker.py