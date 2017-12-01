#!/bin/bash

virtualenv --help
if [ $? != 0 ]; then
    echo "Virtualenv not detected! Attempting install..."
    sudo -H pip install virtualenv --no-cache  # Needs sudo password auth from user?
fi

# Create env, change to it
virtualenv BeerBuddy/static/env
. BeerBuddy/static/env/bin/activate

for LINE in $(cat dependencies.txt); do
    pip install $LINE --no-cache-dir
done
