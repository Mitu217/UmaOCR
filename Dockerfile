FROM ubuntu:20.04 AS base

# add repository
RUN \
    apt update \
    && apt install -y software-properties-common \
    && add-apt-repository -y ppa:alex-p/tesseract-ocr

# install packages
RUN \
    apt update \
    && apt install -y tesseract-ocr libtesseract-dev tesseract-ocr-jpn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base

# install package
RUN \
    apt update \
    && apt install -y python3.8 python3-distutils libgl1-mesa-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# pip install: https://pip.pypa.io/en/stable/installing/
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.8 get-pip.py

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["sh", "entrypoint.sh"]
