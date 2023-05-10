FROM ubuntu:22.04 as base

#base update upgrade 
RUN apt update -y 
RUN apt upgrade -y 

#system utils 
RUN apt install -y curl \
    gpg \
    openssh-server \
    git \
    python3-dev \
    python3-pip \
    sudo \
    vim 
 
#client ssh stuffs
RUN apt-get -y install openssh-client
RUN ssh-keygen -q -t rsa -N '' -f /id_rsa

RUN useradd -rm -d /home/neo -s /bin/bash -G sudo -u 1000 neo
RUN chown -R neo: /opt
USER neo
WORKDIR /opt
RUN https://github.com/JusticeRage/FFM.git
RUN cd FFM/
RUN pip3 install tqdm
RUN export PATH=$PATH:/home/neo/.local/bin
