#operating system
FROM ubuntu:22.04 as base

#base update upgrade 
RUN apt update -y 
RUN apt upgrade -y 

#system utils 
RUN apt install -y apt-utils locales-all fonts-noto \
    fontconfig --reinstall \
    curl \
    gpg \
    openssh-server \
    openssh-client \
    git \
    python3-dev \
    python3-pip \
    sudo \
    vim \
    net-tools \
    rdesktop \
    freerdp2-x11 \ 
    tor \
    proxychains-ng 

RUN useradd -rm -d /home/neo -s /bin/bash -G sudo -u 1000 neo
RUN touch /home/neo/.vimrc 
RUN echo "colorscheme elflord" >> /home/neo/.vimrc
RUN echo "set ts=4 sw=4" >> /home/neo/.vimrc
RUN echo "set number" >> /home/neo/.vimrc

RUN chown -R neo: /opt
#creating this dir prevents misc/tab_completion.py from breaking ffm.py
RUN mkdir -p /snap/bin
USER neo
WORKDIR /home/neo/.ssh
WORKDIR /opt
RUN git clone https://github.com/JusticeRage/FFM.git
WORKDIR /opt/FFM/
RUN pip3 install tqdm
RUN export PATH=$PATH:/home/neo/.local/bin
