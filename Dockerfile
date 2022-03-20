FROM nvidia/cuda:11.1-cudnn8-devel-ubuntu18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
      apt-get install -y software-properties-common \
      && apt-get install --no-install-recommends --no-install-suggests -y gnupg2 ca-certificates \
            git build-essential libopencv-dev \
      && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y git \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install python3.8 -y && \
    apt install python3-distutils -y && \
    apt install python3.8-dev -y && \
    apt install build-essential -y && \
    apt-get install python3-pip -y && \
    apt update && apt install -y libsm6 libxext6 ffmpeg && \
    apt-get install -y libxrender-dev

COPY . /uit_car_racing

RUN git clone https://github.com/AlexeyAB/darknet.git

RUN cp /uit_car_racing/Makefile /darknet/ && \
      cd darknet/ && \
      make

RUN cp darknet/libdarknet.so uit_car_racing/ && \
      cp darknet/uselib uit_car_racing/ && \
      cp darknet/darknet uit_car_racing/

RUN cd uit_car_racing/ && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --pre torch torchvision -f https://download.pytorch.org/whl/nightly/cu111/torch_nightly.html -U && \
    python3 -m pip install -r requirements.txt

WORKDIR /uit_car_racing/
