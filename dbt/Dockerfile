# dbt Service Dockerfile
FROM python:3.11-slim

WORKDIR /usr/app/dbt

# Install git (required by dbt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dbt-postgres
RUN pip install --no-cache-dir dbt-postgres==1.8.2

# Create non-root user
RUN groupadd --gid 1000 dbt && \
    useradd --uid 1000 --gid dbt --shell /bin/bash --create-home dbt

# Create directories and set ownership
RUN mkdir -p /usr/app/dbt/logs /usr/app/dbt/target && \
    chown -R dbt:dbt /usr/app/dbt

# Switch to non-root user
USER dbt

# Switch to non-root user
USER dbt

# Set environment variables
ENV DBT_PROFILES_DIR=/usr/app/dbt

# Default command
CMD ["dbt", "debug"]
