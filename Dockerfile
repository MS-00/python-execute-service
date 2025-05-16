# Stage 1: Build NSJail
FROM debian:bookworm-slim AS nsjail-build
RUN apt-get update && \
    apt-get install -y git build-essential bison flex libcap-dev libnl-3-dev libnl-route-3-dev libprotobuf-dev protobuf-compiler pkg-config clang && \
    git clone https://github.com/google/nsjail.git /opt/nsjail && \
    cd /opt/nsjail && make

# Stage 2: Final image
FROM python:3.12-slim

# Install libprotobuf and libnl-route-3 runtime for NSJail
RUN apt-get update && \
    apt-get install -y libprotobuf32 libnl-route-3-200 && \
    rm -rf /var/lib/apt/lists/*

# Copy NSJail binary from builder
COPY --from=nsjail-build /opt/nsjail/nsjail /usr/local/bin/nsjail

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8080
CMD ["python", "main.py"]
