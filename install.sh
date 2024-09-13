#!/bin/bash
apt install python3-pip python3-venv python3-numpy
python -m venv --system-site-packages venv
./venv/bin/pip install -r requirements.txt

