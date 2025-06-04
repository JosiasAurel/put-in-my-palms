#!/bin/bash
apt-get update
apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev
git clone https://github.com/tsl0922/ttyd.git
cd ttyd && mkdir build && cd build
cmake ..
make && make install

# also install python uv for some packages 
# curl -LsSf https://astral.sh/uv/install.sh | sh
pip install uv

# ttyd