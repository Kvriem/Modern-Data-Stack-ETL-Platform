# Production-Grade ETL Pipeline

A fully containerized, production-ready data engineering pipeline demonstrating modern data stack best practices.

## 🏗️ Architecture

```
┌─────────────────┐
│  Source DB      │
│  (PostgreSQL)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python ETL     │
│  Extract & Load │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Target DB      │
│  (PostgreSQL)   │
│  Raw Schema     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  dbt Transform  │
│  Staging → Mart │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Warehouse │
│  Analytics-Ready│
└─────────────────┘

     Orchestrated by Apache Airflow
     Automated via GitHub Actions CI/CD
```

## 🎯 Features

- **Containerized Architecture**: All components run in Docker containers
- **Production ETL**: Incremental loading with watermarks, error handling, retries
- **dbt Transformations**: Layered architecture (staging → intermediate → marts)
- **Apache Airflow**: Orchestration with dependency management
- **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions
- **Data Quality**: Comprehensive dbt tests (unique, not_null, relationships)
- **Developer Tools**: Makefile for common tasks, pre-commit hooks
- **Comprehensive Testing**: Unit tests with pytest

## 📦 Tech Stack

- **Orchestration**: Apache Airflow
- **ETL**: Python 3.11, psycopg2, structlog
- **Transformations**: dbt Core
- **Databases**: PostgreSQL 15
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, black, flake8, sqlfluff

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional but recommended)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd docker-actions
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**
   ```bash
   make setup
   # Or manually:
   # docker-compose build
   # docker-compose up -d
   ```

4. **Wait for initialization** (30 seconds)
   - Airflow will initialize the database and create admin user

5. **Access Airflow UI**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

## 🔧 Common Commands

```bash
# Start all services
make up

# Stop all services
make down

# Run ETL manually
make etl

# Run dbt transformations
make dbt-run

# Run dbt tests
make dbt-test

# Run complete pipeline
make pipeline

# View logs
make logs

# Run Python tests
make test

# Run linters
make lint

# Format code
make format

# Connect to databases
make db-source  # Source database
make db-target  # Target database

# Clean up everything
make clean
```

## 📊 Data Flow

### 1. Source Database (OLTP)
- **Tables**: customers, orders, products, order_items
- **Port**: 5433
- Simulates operational database

### 2. ETL Process
- **Extract**: Read data from source with incremental loading
- **Load**: Upsert data to target `raw` schema
- **Watermarks**: Track last extraction timestamp

### 3. dbt Transformations

#### Staging Layer (`raw` → `staging`)
- Clean and standardize column names
- Type casting
- 1:1 mapping from source

**Models:**
- `stg_customers`
- `stg_products`
- `stg_orders`
- `stg_order_items`

#### Intermediate Layer (`staging` → `intermediate`)
- Business logic joins
- Calculated fields
- Data enrichment

**Models:**
- `int_orders_enriched` - Orders with customer info
- `int_order_items_enriched` - Items with product details

#### Marts Layer (`intermediate` → `marts`)
- Analytics-ready tables
- Star schema design
- Aggregations

**Models:**
- `dim_customers` - Customer dimension
- `dim_products` - Product dimension
- `fct_sales` - Sales fact (incremental)
- `fct_orders` - Order summary fact

### 4. Airflow Orchestration

**DAG**: `etl_pipeline`
- **Schedule**: Daily at 2 AM UTC
- **Tasks**:
  1. `extract_load` - Run Python ETL
  2. `dbt_run` - Execute dbt models
  3. `dbt_test` - Run data quality tests

## 🧪 Testing

### Python Unit Tests
```bash
cd etl
pytest tests/ -v --cov=src --cov-report=term-missing
```

### dbt Tests
```bash
make dbt-test
# Or manually:
docker-compose --profile dbt run --rm dbt dbt test --profiles-dir .
```

### CI/CD Pipeline
- Runs automatically on push/PR
- **Stages**:
  1. Lint (black, flake8, sqlfluff)
  2. Test ETL (pytest)
  3. Build Docker images
  4. Integration test (full pipeline)

## 📁 Project Structure

```
docker-actions/
├── airflow/              # Airflow configuration
│   ├── dags/            # DAG definitions
│   ├── Dockerfile       # Airflow image
│   └── requirements.txt
├── dbt/                 # dbt project
│   ├── models/
│   │   ├── staging/     # Staging models
│   │   ├── intermediate/# Intermediate models
│   │   └── marts/       # Mart models
│   ├── dbt_project.yml
│   └── profiles.yml
├── etl/                 # Python ETL service
│   ├── src/
│   │   ├── extract.py   # Data extraction
│   │   ├── load.py      # Data loading
│   │   ├── main.py      # Orchestration
│   │   └── config.py    # Configuration
│   ├── tests/           # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   └── init/            # Database initialization
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
├── docker-compose.yml   # Service definitions
├── Makefile            # Developer commands
├── .env.example        # Environment template
└── README.md
```

## 🔒 Security

- Database credentials via environment variables
- No hardcoded secrets
- `.env` file excluded from version control
- Docker secrets for production deployment

## 📈 Monitoring & Logging

- **Structured Logging**: JSON logs with structlog
- **Airflow UI**: Task monitoring and logs
- **dbt Logs**: Transformation execution details
- **Health Checks**: Database availability monitoring

## 🛠️ Development

### Adding a New Table

1. **Add to ETL config** (`etl/src/config.py`)
2. **Create staging model** (`dbt/models/staging/`)
3. **Add tests** (`schema.yml`)
4. **Create marts** as needed
5. **Run pipeline**: `make pipeline`

### Pre-commit Hooks

```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Reset everything
make clean
make setup
```

### Database connection errors
```bash
# Check database health
docker-compose ps

# Restart databases
docker-compose restart source_db target_db
```

### Airflow tasks failing
```bash
# View Airflow logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver

# Check task logs in Airflow UI
```

## 📚 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test && make lint`
5. Submit a pull request

## 📝 License

This project is for educational and portfolio purposes.

## 👤 Author

**Data Engineering Team**

---

**⭐ If you found this project helpful, please give it a star!**
