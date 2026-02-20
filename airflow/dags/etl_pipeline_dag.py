"""
ETL Pipeline DAG

Orchestrates the full data pipeline:
1. Extract and Load data from source to target database
2. Run dbt transformations
3. Run dbt tests

Author: Data Engineering Team
"""

import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}

# Define the DAG
dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline with dbt transformations',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['etl', 'dbt', 'production'],
)

# Task 1: Extract and Load
extract_load_task = DockerOperator(
    task_id='extract_load',
    image='docker-actions-etl:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main',
    docker_url='unix://var/run/docker.sock',
    network_mode='etl_network',
    environment={
        'SOURCE_DB_HOST': os.getenv('SOURCE_DB_HOST', 'source_db'),
        'SOURCE_DB_PORT': os.getenv('SOURCE_DB_PORT', '5432'),
        'SOURCE_DB_NAME': os.getenv('SOURCE_DB_NAME', 'source_db'),
        'SOURCE_DB_USER': os.getenv('SOURCE_DB_USER', 'source_user'),
        'SOURCE_DB_PASSWORD': os.getenv('SOURCE_DB_PASSWORD', 'source_password'),
        'TARGET_DB_HOST': os.getenv('TARGET_DB_HOST', 'target_db'),
        'TARGET_DB_PORT': os.getenv('TARGET_DB_PORT', '5432'),
        'TARGET_DB_NAME': os.getenv('TARGET_DB_NAME', 'target_db'),
        'TARGET_DB_USER': os.getenv('TARGET_DB_USER', 'target_user'),
        'TARGET_DB_PASSWORD': os.getenv('TARGET_DB_PASSWORD', 'target_password'),
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 2: dbt run (execute transformations)
dbt_run_task = DockerOperator(
    task_id='dbt_run',
    image='docker-actions-dbt:latest',
    api_version='auto',
    auto_remove=True,
    command='dbt run --profiles-dir .',
    docker_url='unix://var/run/docker.sock',
    network_mode='etl_network',
    environment={
        'TARGET_DB_HOST': os.getenv('TARGET_DB_HOST', 'target_db'),
        'TARGET_DB_PORT': os.getenv('TARGET_DB_PORT', '5432'),
        'TARGET_DB_NAME': os.getenv('TARGET_DB_NAME', 'target_db'),
        'TARGET_DB_USER': os.getenv('TARGET_DB_USER', 'target_user'),
        'TARGET_DB_PASSWORD': os.getenv('TARGET_DB_PASSWORD', 'target_password'),
    },
    mounts=[
        Mount(
            source='/home/kariem/projects/docker-actions/dbt',
            target='/usr/app/dbt',
            type='bind'
        ),
    ],
    working_dir='/usr/app/dbt',
    mount_tmp_dir=False,
    dag=dag,
)

# Task 3: dbt test (validate data quality)
dbt_test_task = DockerOperator(
    task_id='dbt_test',
    image='docker-actions-dbt:latest',
    api_version='auto',
    auto_remove=True,
    command='dbt test --profiles-dir .',
    docker_url='unix://var/run/docker.sock',
    network_mode='etl_network',
    environment={
        'TARGET_DB_HOST': os.getenv('TARGET_DB_HOST', 'target_db'),
        'TARGET_DB_PORT': os.getenv('TARGET_DB_PORT', '5432'),
        'TARGET_DB_NAME': os.getenv('TARGET_DB_NAME', 'target_db'),
        'TARGET_DB_USER': os.getenv('TARGET_DB_USER', 'target_user'),
        'TARGET_DB_PASSWORD': os.getenv('TARGET_DB_PASSWORD', 'target_password'),
    },
    mounts=[
        Mount(
            source='/home/kariem/projects/docker-actions/dbt',
            target='/usr/app/dbt',
            type='bind'
        ),
    ],
    working_dir='/usr/app/dbt',
    mount_tmp_dir=False,
    dag=dag,
)

# Define task dependencies
extract_load_task >> dbt_run_task >> dbt_test_task
