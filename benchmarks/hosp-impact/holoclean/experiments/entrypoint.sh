#!/usr/bin/env bash
# Set & move to home directory
source ../set_env.sh

script="run_holoclean.py"
if [ $# -eq 1 ] ; then
  script="$1"
fi

echo "Launching example script $script"
python $script
