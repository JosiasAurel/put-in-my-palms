FROM ubuntu:22.04

# update apt and install essential packages
RUN apt-get update 
RUN apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev

# install the python runtime and pip
RUN apt-get install -y python3 python3-pip

# END install python runtime

# install node.js - https://nodejs.org/en/download (v22.16.0, Linux, nvm)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
RUN \. "$HOME/.nvm/nvm.sh"
RUN nvm install 22
RUN node -v 

# END install node.js 

# install the rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# END install the rust compiler

# install ruby runtime
RUN sudo apt-get install ruby-full

# END install ruby runtime

WORKDIR /app

COPY . .