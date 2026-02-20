# Production-Grade ETL Pipeline Project Plan

## 📋 Overview

Build a fully containerized ETL pipeline with:
- Source & Target PostgreSQL databases
- Python ETL service
- dbt transformations
- Airflow orchestration
- GitHub Actions CI/CD

---

## 🗂 Phase 1: Project Scaffolding

**Goal:** Create the full directory structure

```
docker-actions/
├── airflow/
│   ├── dags/
│   │   └── etl_pipeline_dag.py
│   ├── Dockerfile
│   └── requirements.txt
├── etl/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── extract.py
│   │   ├── load.py
│   │   ├── main.py
│   │   └── config.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_extract.py
│   │   └── test_load.py
│   ├── Dockerfile
│   └── requirements.txt
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   └── schema.yml
│   │   ├── intermediate/
│   │   │   ├── int_orders_enriched.sql
│   │   │   └── schema.yml
│   │   └── marts/
│   │       ├── fct_sales.sql
│   │       ├── dim_customers.sql
│   │       └── schema.yml
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── Dockerfile
├── db/
│   └── init/
│       └── init_source.sql
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── Makefile
├── requirements.txt
├── .pre-commit-config.yaml
└── README.md
```

**Tasks:**
- [ ] Create all directories
- [ ] Create placeholder files
- [ ] Set up .gitignore

---

## 🐳 Phase 2: Docker Infrastructure

**Goal:** Set up all containers with proper networking

### Containers:
1. **source_db** - PostgreSQL (OLTP source)
2. **target_db** - PostgreSQL (Data Warehouse)
3. **etl** - Python ETL service
4. **dbt** - dbt container
5. **airflow** - Airflow scheduler + webserver

### Requirements:
- [ ] Create docker-compose.yml with all services
- [ ] Configure Docker network (`etl_network`)
- [ ] Set up named volumes for DB persistence
- [ ] Add healthchecks for databases
- [ ] Create .env file for credentials
- [ ] Use multi-stage builds for Python images

---

## 🔄 Phase 3: ETL Service Development

**Goal:** Build modular, production-ready ETL scripts

### Files:
- `config.py` - Environment variables, DB connections
- `extract.py` - Extract data from source DB
- `load.py` - Load data to target DB (raw schema)
- `main.py` - Orchestrate ETL process

### Features:
- [ ] Structured logging
- [ ] Type hints throughout
- [ ] Idempotent operations (upserts)
- [ ] Incremental loading via watermark column
- [ ] Error handling with retries
- [ ] Unit tests with pytest

### Sample Tables:
- `customers` (id, name, email, created_at, updated_at)
- `orders` (id, customer_id, amount, status, created_at, updated_at)
- `products` (id, name, price, category, created_at, updated_at)

---

## 📊 Phase 4: dbt Layer

**Goal:** Transform raw data into analytics-ready models

### Layers:
1. **Staging** (`stg_`)
   - Clean and rename columns
   - Cast data types
   - 1:1 mapping from source

2. **Intermediate** (`int_`)
   - Business logic joins
   - Calculations
   - Enrichments

3. **Marts** (`fct_`, `dim_`)
   - Final analytics tables
   - Star schema design

### Requirements:
- [ ] Create dbt_project.yml
- [ ] Create profiles.yml (for target DB connection)
- [ ] Build staging models with schema.yml tests
- [ ] Build intermediate models
- [ ] Build mart models (at least one incremental)
- [ ] Add tests: unique, not_null, relationships
- [ ] Configure documentation generation

---

## 🌬 Phase 5: Airflow Orchestration

**Goal:** Automate pipeline execution

### DAG Structure:
```
extract_load_task → dbt_run_task → dbt_test_task
```

### Requirements:
- [ ] Create Airflow Dockerfile
- [ ] Configure DockerOperator for each task
- [ ] Set up proper dependency chaining
- [ ] Add retries (3 attempts, 5 min delay)
- [ ] Use environment variables (no hardcoded creds)
- [ ] Configure daily schedule
- [ ] Add proper logging

---

## 🔁 Phase 6: CI/CD Pipeline

**Goal:** Automate testing and deployment with GitHub Actions

### Workflow Steps:
1. **Lint**
   - [ ] black (Python formatting)
   - [ ] flake8 (Python linting)
   - [ ] sqlfluff (SQL linting)

2. **Test**
   - [ ] Run pytest for ETL

3. **Build**
   - [ ] Build Docker images
   - [ ] Use caching for faster builds

4. **Integration**
   - [ ] Spin up docker-compose
   - [ ] Wait for healthchecks
   - [ ] Run ETL
   - [ ] Run dbt run
   - [ ] Run dbt test

5. **Cleanup**
   - [ ] Tear down containers
   - [ ] Fail pipeline on any error

---

## 📝 Phase 7: Documentation & Quality

**Goal:** Professional-grade documentation and tooling

### Tasks:
- [ ] Write comprehensive README.md
- [ ] Add architecture diagram
- [ ] Create Makefile with commands:
  - `make build` - Build all images
  - `make up` - Start services
  - `make down` - Stop services
  - `make etl` - Run ETL manually
  - `make dbt-run` - Run dbt
  - `make test` - Run all tests
  - `make lint` - Run linters
- [ ] Set up pre-commit hooks
- [ ] Create .env.example with sample values

---

## ✅ Checklist Summary

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Project Structure | ✅ |
| 2 | Docker Infrastructure | ✅ |
| 3 | ETL Service | ✅ |
| 4 | dbt Layer | ⬜ |
| 5 | Airflow DAG | ⬜ |
| 6 | CI/CD Pipeline | ⬜ |
| 7 | Documentation | ⬜ |

---

## 🚀 Execution Order

1. **Phase 1** → Scaffold structure
2. **Phase 2** → Docker setup (databases first)
3. **Phase 3** → ETL development + testing
4. **Phase 4** → dbt models + tests
5. **Phase 5** → Airflow DAG
6. **Phase 6** → GitHub Actions CI
7. **Phase 7** → Polish docs and tooling

---

## 📌 Notes

- Each phase should be committed separately with meaningful messages
- Test locally before pushing to CI
- Use feature branches for each phase
- Document any deviations from the plan
