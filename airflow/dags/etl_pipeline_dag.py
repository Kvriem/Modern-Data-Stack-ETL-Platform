"""
ETL Pipeline DAG

Orchestrates the full data pipeline:
1. Extract and Load data from source to target database
2. Run dbt transformations
3. Run dbt tests

Author: Data Engineering Team
"""

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
        'SOURCE_DB_HOST': '{{ var.value.SOURCE_DB_HOST }}',
        'SOURCE_DB_PORT': '{{ var.value.SOURCE_DB_PORT }}',
        'SOURCE_DB_NAME': '{{ var.value.SOURCE_DB_NAME }}',
        'SOURCE_DB_USER': '{{ var.value.SOURCE_DB_USER }}',
        'SOURCE_DB_PASSWORD': '{{ var.value.SOURCE_DB_PASSWORD }}',
        'TARGET_DB_HOST': '{{ var.value.TARGET_DB_HOST }}',
        'TARGET_DB_PORT': '{{ var.value.TARGET_DB_PORT }}',
        'TARGET_DB_NAME': '{{ var.value.TARGET_DB_NAME }}',
        'TARGET_DB_USER': '{{ var.value.TARGET_DB_USER }}',
        'TARGET_DB_PASSWORD': '{{ var.value.TARGET_DB_PASSWORD }}',
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
        'TARGET_DB_HOST': '{{ var.value.TARGET_DB_HOST }}',
        'TARGET_DB_PORT': '{{ var.value.TARGET_DB_PORT }}',
        'TARGET_DB_NAME': '{{ var.value.TARGET_DB_NAME }}',
        'TARGET_DB_USER': '{{ var.value.TARGET_DB_USER }}',
        'TARGET_DB_PASSWORD': '{{ var.value.TARGET_DB_PASSWORD }}',
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
        'TARGET_DB_HOST': '{{ var.value.TARGET_DB_HOST }}',
        'TARGET_DB_PORT': '{{ var.value.TARGET_DB_PORT }}',
        'TARGET_DB_NAME': '{{ var.value.TARGET_DB_NAME }}',
        'TARGET_DB_USER': '{{ var.value.TARGET_DB_USER }}',
        'TARGET_DB_PASSWORD': '{{ var.value.TARGET_DB_PASSWORD }}',
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
