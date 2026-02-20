# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd docker-actions
cp .env.example .env
```

### 2. Start Services
```bash
make setup
# Or: docker-compose build && docker-compose up -d
```

### 3. Wait for Initialization (30 seconds)
```bash
# Watch the logs
make logs
```

### 4. Access Airflow
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### 5. Run Your First Pipeline
```bash
# Option 1: Via Makefile
make pipeline

# Option 2: Via individual commands
make etl       # Extract & Load
make dbt-run   # Transform
make dbt-test  # Validate

# Option 3: Via Airflow UI
# Navigate to DAGs → etl_pipeline → Trigger DAG
```

## 📊 What You'll See

After running the pipeline:

1. **Source Database** (port 5433)
   - Sample data: customers, orders, products, order_items

2. **Target Database** (port 5434)
   - `raw` schema: Loaded from source
   - `staging` schema: Cleaned views
   - `intermediate` schema: Enriched views
   - `marts` schema: Analytics tables

## 🔍 Verify Results

### Check Database Content
```bash
# Connect to target database
make db-target

# In psql, run:
\dt raw.*          # Show raw tables
\dt staging.*      # Show staging views
\dt marts.*        # Show mart tables

SELECT * FROM marts.fct_sales LIMIT 10;
SELECT * FROM marts.dim_customers LIMIT 10;
```

### Check Airflow
1. Open http://localhost:8080
2. Navigate to "DAGs"
3. Click on "etl_pipeline"
4. View task execution status

## 🎯 Common Tasks

### Run ETL Only
```bash
make etl
# Or: docker-compose --profile etl run --rm etl
```

### Run dbt Only
```bash
make dbt-run
# Or: docker-compose --profile dbt run --rm dbt dbt run --profiles-dir .
```

### Test Everything
```bash
make test      # Python tests
make dbt-test  # dbt tests
make lint      # Code quality
```

### View Logs
```bash
make logs                                    # All services
docker-compose logs airflow-scheduler        # Airflow scheduler
docker-compose logs -f etl                   # ETL service (follow)
```

### Restart Services
```bash
make restart
# Or: make down && make up
```

### Clean Everything
```bash
make clean  # Stops containers, removes volumes
```

## 🛠️ Development Workflow

1. **Make Code Changes**
   ```bash
   # Edit Python files in etl/src/
   # Edit dbt models in dbt/models/
   ```

2. **Format Code**
   ```bash
   make format  # Black formatter
   make lint    # Check code quality
   ```

3. **Test Changes**
   ```bash
   make test    # Run pytest
   ```

4. **Rebuild and Test**
   ```bash
   docker-compose build etl  # Rebuild ETL image
   make etl                   # Test ETL
   make dbt-run               # Test dbt
   ```

5. **Run Full Pipeline**
   ```bash
   make pipeline  # Complete end-to-end test
   ```

## 📚 Resources

- **Airflow UI**: http://localhost:8080
- **Source DB**: `psql -h localhost -p 5433 -U source_user -d source_oltp`
- **Target DB**: `psql -h localhost -p 5434 -U target_user -d target_warehouse`

## 🐛 Troubleshooting

### Services Won't Start
```bash
docker-compose ps        # Check service status
docker-compose logs      # View error logs
make clean && make setup # Fresh start
```

### Can't Connect to Database
```bash
# Wait for health checks
docker-compose ps

# Check if containers are running
docker ps

# Test connection
docker exec -it target_db psql -U target_user -d target_warehouse
```

### Airflow Tasks Failing
1. Check logs in Airflow UI
2. Verify environment variables in `.env`
3. Check task logs: `docker-compose logs airflow-scheduler`

### dbt Errors
```bash
# Check dbt debug
docker-compose --profile dbt run --rm dbt dbt debug --profiles-dir .

# Check connection
docker-compose --profile dbt run --rm dbt dbt run-operation test_connection --profiles-dir .
```

## 💡 Tips

- **First Run**: Takes ~60 seconds for Airflow to fully initialize
- **Database Reset**: Use `make db-reset` (WARNING: deletes all data)
- **Check Health**: `docker-compose ps` shows health status
- **Save Changes**: Commit your .env file changes (except passwords!)
- **Pre-commit Hooks**: Run `pre-commit install` for automatic checks

## 🎓 Learning Path

1. ✅ Get pipeline running (you are here!)
2. 📊 Explore the data in target database
3. 🔍 Review dbt models in `dbt/models/`
4. 🐍 Check ETL code in `etl/src/`
5. 🌊 Study Airflow DAG in `airflow/dags/`
6. 🧪 Run and review tests
7. 📝 Read ARCHITECTURE.md for deep dive
8. 🔨 Make your own changes!

## 🆘 Need Help?

- Check ARCHITECTURE.md for detailed explanations
- Review logs with `make logs`
- Check README.md for comprehensive documentation
- Review test files for usage examples
