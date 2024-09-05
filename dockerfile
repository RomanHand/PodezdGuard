FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

COPY cam.py .
COPY config.yml .

RUN pip install --no-cache-dir opencv-python ultralytics

CMD ["python", "cam.py"]
