FROM ubuntu:22.04

# update apt and install essential packages
RUN apt-get update
RUN apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev libncurses-dev tar ffmpeg

# install the python runtime and pip
RUN apt-get install -y python3 python3-pip

# END install python runtime

# install node.js - https://nodejs.org/en/download (v22.16.0, Linux, nvm)
RUN apt-get install -y nodejs
RUN apt-get install -y npm
# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# RUN \. "$HOME/.nvm/nvm.sh"
# RUN nvm install 22
# RUN node -v 

# END install node.js 

# install bun
RUN curl -fsSL https://bun.sh/install | bash
# END install bun

# install the rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# END install the rust compiler

# install ruby runtime
RUN apt-get -y install ruby-full

# END install ruby runtime

# install golang
RUN apt install -y golang-go

# END install golang

COPY run-app.sh /run-app.sh
WORKDIR /app

COPY . .

RUN groupadd -r hackclubber && useradd -r -g hackclubber --no-create-home --shell /bin/bash hackclubber
RUN mkdir -p /etc/sudoers.d && \
    echo "myuser ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get" >> /etc/sudoers.d/myuser && \
    chmod 0440 /etc/sudoers.d/myuser
RUN chown -R hackclubber:hackclubber /app

# install jq command tool
RUN apt-get install -y jq
# END install jq command tool

# install ttyd - this will help us eventually expose the terminal via a web interface
# RUN git clone https://github.com/tsl0922/ttyd.git
# RUN cd ttyd && mkdir build && cd build
# RUN cmake ..
# RUN make && make install

# END install ttyd

RUN chmod +x add-ttyd.sh
RUN ./add-ttyd.sh 

# remove ttyd to avoid people tampering with the installation
RUN rm add-ttyd.sh
RUN rm -rf ttyd

# this is where we will be cloning the repository to work with

# clone the repository
RUN git clone https://github.com/hackclub/terminalcraft.git
RUN cd terminalcraft

# give executable permission to this script
RUN chmod +x /run-app.sh

EXPOSE 8989

USER hackclubber

ENTRYPOINT [ "/run-app.sh" ]
# CMD ./run-app.sh
