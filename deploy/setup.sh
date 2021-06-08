#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/sndhuArpan/canopy.git'

PROJECT_BASE_PATH='/home/ec2-user/canopy/canopy'

echo "Installing dependencies..."
sudo yum update
sudo yum install -y python3
sudo yum install -y sqlite git

# Create project directory
mkdir -p $PROJECT_BASE_PATH
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH

# Create virtual environment
mkdir -p $PROJECT_BASE_PATH/env
python3 -m venv $PROJECT_BASE_PATH/env

# Install python packages
$PROJECT_BASE_PATH/env/bin/pip install -r $PROJECT_BASE_PATH/requirement.txt

source $PROJECT_BASE_PATH/env/bin activate

echo "DONE! :)"