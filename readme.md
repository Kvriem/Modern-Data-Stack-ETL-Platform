📌 Prompt for Local Agent

You are a senior Data Engineer and DevOps architect.

I want you to help me build a production-grade data engineering project with the following characteristics:

🎯 Project Goal

Build a fully containerized ETL pipeline that:

Extracts data from a source database

Loads it into a target data warehouse

Transforms it using dbt

Orchestrates everything using Airflow

Uses GitHub Actions for CI

Follows production best practices

This project must simulate a real-world modern data stack.

🏗 Architecture Overview

The system must include:

Source Database (Container 1)

PostgreSQL

Acts as OLTP system

Target Database (Container 2)

PostgreSQL

Acts as Data Warehouse

Python ETL Service (Custom Docker Image)

Extracts from source DB

Loads into target DB (raw schema)

Must be idempotent

Must support incremental loads

dbt Layer

Connected to target database

Has staging, intermediate, and mart layers

Includes tests (unique, not_null, relationships)

Uses incremental models where appropriate

Airflow

Orchestrates:
extract_load_task → dbt_run_task → dbt_test_task

Uses DockerOperator

Includes retries and proper logging

GitHub Actions

Runs on push and PR

Builds Docker images

Spins up docker-compose services

Runs ETL

Runs dbt

Runs tests

Fails if any step fails

📁 Required Project Structure

The repository must follow this structure:

project-root/
│
├── airflow/
│   ├── dags/
│   └── Dockerfile
│
├── etl/
│   ├── src/
│   │   ├── extract.py
│   │   ├── load.py
│   │   ├── main.py
│   ├── tests/
│   └── Dockerfile
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── dbt_project.yml
│
├── docker-compose.yml
├── .github/workflows/ci.yml
├── requirements.txt
└── README.md
🐳 Docker Requirements

Each service must run in its own container

Use Docker networks (no localhost)

Use environment variables for credentials

Use .env file locally

Use named volumes for DB persistence

Use multi-stage builds when possible

Add healthchecks to databases

🧠 ETL Design Requirements

The ETL must:

Be modular (extract.py, load.py, main.py)

Use logging

Be idempotent

Use upserts or merge strategy

Support incremental loading via watermark column

Handle failures gracefully

📊 dbt Requirements

Must follow layered architecture:

staging

intermediate

marts

Must include schema.yml tests

Must include at least one incremental model

Must run dbt test after dbt run

Should generate documentation

🌬 Airflow Requirements

Single DAG

Uses DockerOperator

Proper dependency chaining

Includes retries

No hardcoded credentials

Configurable schedule

🔁 CI/CD Requirements

GitHub Actions must:

Run linting (black, flake8, sqlfluff)

Run pytest for ETL

Build Docker images

Run docker-compose

Execute ETL

Execute dbt run

Execute dbt test

Fail on error

Add caching to speed up builds.

📈 Code Quality Standards

Use type hints in Python

Follow PEP8

Use logging instead of print

Use environment variables

Avoid hardcoding values

Write meaningful commit messages

Add a professional README with architecture diagram

🚀 Additional Production-Level Enhancements

If possible, also include:

Makefile with developer commands

Pre-commit hooks

Health checks

Structured logging

Retry mechanisms

Clear separation between dev and prod configs

🔎 How You Should Help Me

When generating code:

Provide production-quality code

Add comments explaining decisions

Explain best practices briefly

Avoid shortcuts

Think like a senior engineer reviewing a PR

If something is ambiguous, propose the most production-ready approach.

The goal is to build a portfolio-level, real-world, modern data engineering project that demonstrates:

Containerization

Orchestration

Data modeling

CI/CD

DevOps best practices