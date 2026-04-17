FROM python:3.11-slim

# Build tools + network tools the LLM probe scripts will try to use
RUN apt-get update && apt-get install -y \
    strace \
    procps \
    gcc \
    g++ \
    cmake \
    make \
    iputils-ping \
    iproute2 \
    netcat-openbsd \
    && apt-get remove -y wget curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root prisoner user
RUN useradd -ms /bin/bash prisoner

# Internal directories — all owned by prisoner
WORKDIR /home/prisoner
RUN mkdir -p /home/prisoner/tools \
    && mkdir -p /home/prisoner/workspace \
    && mkdir -p /home/prisoner/memory \
    && chown -R prisoner:prisoner /home/prisoner

# /logs — created here with open permissions so mounted volume is writable
RUN mkdir -p /logs && chmod 777 /logs

# Model directory - will be mounted read-only at runtime
RUN mkdir -p /models

# Syscall logger
COPY agent/syscall_logger.sh /usr/local/bin/syscall_logger.sh
RUN chmod +x /usr/local/bin/syscall_logger.sh

# Agent runtime
COPY agent/agent.py /home/prisoner/agent.py
RUN chown prisoner:prisoner /home/prisoner/agent.py

# Install Python deps
COPY agent/requirements.txt /tmp/requirements.txt
ENV CMAKE_ARGS="-DLLAMA_BLAS=OFF -DLLAMA_CUBLAS=OFF"
ENV FORCE_CMAKE=1
RUN pip install --no-cache-dir llama-cpp-python==0.3.4 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
RUN pip install --no-cache-dir psutil requests

# Entrypoint runs as root briefly to start logger, then agent runs as prisoner
COPY agent/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER prisoner

ENTRYPOINT ["/entrypoint.sh"]