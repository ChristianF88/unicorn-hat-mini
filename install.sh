#!/bin/bash
apt install python3-pip python3-venv python3-numpy
python -m venv --system-site-packages venv
./venv/bin/pip install -r requirements.txt

# installing service
sudo cp game.service /etc/systemd/system/game.service
sudo systemctl daemon-reload
sudo systemctl enable game.service
sudo systemctl start game.service
sudo systemctl status game.service