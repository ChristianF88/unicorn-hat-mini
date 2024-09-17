#!/bin/bash
apt install python3-pip python3-venv python3-numpy
python -m venv --system-site-packages venv
./venv/bin/pip install -r requirements.txt

# installing service
sudo ln -s ./game.service /etc/systemd/system/game.service
sudo systemctl daemon-reload
sudo systemctl enable your_program.service
sudo systemctl start your_program.service
sudo systemctl status your_program.service