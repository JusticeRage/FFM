#operating system
FROM ubuntu:22.04 as base

#base update upgrade 
RUN apt update -y 
RUN apt upgrade -y 

#system utils 
RUN apt install -y curl \
    gpg \
    openssh-server \
    openssh-client \
    git \
    python3-dev \
    python3-pip \
    sudo \
    vim 
 
RUN useradd -rm -d /home/neo -s /bin/bash -G sudo -u 1000 neo
RUN chown -R neo: /opt
USER neo
WORKDIR /home/neo/.ssh
RUN ssh-keygen -q -t rsa -N '' -f id_rsa
WORKDIR /opt
RUN git clone https://github.com/JusticeRage/FFM.git
WORKDIR /opt/FFM/
RUN pip3 install tqdm
RUN export PATH=$PATH:/home/neo/.local/bin
