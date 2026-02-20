# Airflow Service Dockerfile
FROM apache/airflow:2.8.1-python3.11

USER root

# Install Docker CLI for DockerOperator
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Add airflow user to docker group
RUN groupadd -f docker && usermod -aG docker airflow

USER airflow

# Install additional Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /opt/airflow
