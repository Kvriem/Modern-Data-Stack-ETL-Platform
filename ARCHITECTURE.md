# ETL Pipeline Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         APACHE AIRFLOW ORCHESTRATOR                       │
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ Extract/Load │ -> │   dbt Run    │ -> │   dbt Test   │               │
│  │    Task      │    │     Task     │    │     Task     │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                            │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                         │
         ▼                                                         ▼
┌─────────────────┐                                     ┌─────────────────┐
│   SOURCE DB     │                                     │   TARGET DB     │
│  (PostgreSQL)   │                                     │  (PostgreSQL)   │
│                 │                                     │                 │
│  ┌───────────┐  │                                     │  ┌───────────┐  │
│  │ customers │  │──── Python ETL Extract ─────────────>│ │raw.       │  │
│  │ orders    │  │                                     │  │customers  │  │
│  │ products  │  │                                     │  │orders     │  │
│  │order_items│  │                                     │  │products   │  │
│  └───────────┘  │                                     │  │order_items│  │
│                 │                                     │  └───────────┘  │
│  Port: 5433     │                                     │                 │
└─────────────────┘                                     │  Port: 5434     │
                                                        │                 │
                                                        │  dbt Transform  │
                                                        │       ↓         │
                                                        │  ┌───────────┐  │
                                                        │  │staging.   │  │
                                                        │  │stg_*      │  │
                                                        │  └─────┬─────┘  │
                                                        │        ↓         │
                                                        │  ┌───────────┐  │
                                                        │  │inter-     │  │
                                                        │  │mediate.   │  │
                                                        │  │int_*      │  │
                                                        │  └─────┬─────┘  │
                                                        │        ↓         │
                                                        │  ┌───────────┐  │
                                                        │  │marts.     │  │
                                                        │  │dim_*      │  │
                                                        │  │fct_*      │  │
                                                        │  └───────────┘  │
                                                        └─────────────────┘
```

## Data Flow

### Phase 1: Extract & Load (Python ETL)

**Input**: Source OLTP database
**Output**: Target database `raw` schema
**Features**:
- Incremental loading with watermarks
- Upsert strategy (INSERT ... ON CONFLICT)
- Batch processing
- Error handling and retries
- Structured logging

### Phase 2: Staging Layer (dbt)

**Input**: `raw` schema
**Output**: `staging` schema
**Purpose**: Clean and standardize
**Materialization**: VIEW

Models:
- `stg_customers` - Standardized customer data
- `stg_orders` - Cleaned order data
- `stg_products` - Standardized product catalog
- `stg_order_items` - Line item details

### Phase 3: Intermediate Layer (dbt)

**Input**: `staging` schema
**Output**: `intermediate` schema
**Purpose**: Business logic and enrichment
**Materialization**: VIEW

Models:
- `int_orders_enriched` - Orders + customer information
- `int_order_items_enriched` - Items + product details

### Phase 4: Marts Layer (dbt)

**Input**: `intermediate` schema
**Output**: `marts` schema
**Purpose**: Analytics-ready star schema
**Materialization**: TABLE (with incremental for facts)

Dimensions:
- `dim_customers` - Customer attributes
- `dim_products` - Product attributes

Facts:
- `fct_sales` - Sales transactions (incremental)
- `fct_orders` - Order summaries with metrics

## Network Architecture

```
┌─────────────────────────────────────────────────────┐
│              etl_network (Docker Bridge)             │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │source_db │  │target_db │  │airflow_db│          │
│  │:5432     │  │:5432     │  │:5432     │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   ETL    │  │   dbt    │  │ Airflow  │          │
│  │ Service  │  │ Service  │  │Web/Sched │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                       │
└─────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    Port 5433      Port 5434      Port 8080
    (external)     (external)     (external)
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | Apache Airflow | Workflow management |
| ETL | Python 3.11 | Extract and Load |
| Transformation | dbt Core | Data modeling |
| Storage | PostgreSQL 15 | Databases |
| Containerization | Docker Compose | Service management |
| CI/CD | GitHub Actions | Automation |
| Testing | pytest, dbt test | Quality assurance |

## Data Quality

### Source Tests
- Primary key uniqueness
- Foreign key relationships
- Not null constraints

### Staging Tests
- Unique identifiers
- Required fields
- Accepted values
- Referential integrity

### Marts Tests
- Dimension key uniqueness
- Fact-dimension relationships
- Non-null measures
- Data freshness

## Deployment

### Local Development
```bash
make setup    # Initialize
make pipeline # Run full pipeline
make test     # Run tests
```

### CI/CD Pipeline
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Lint   │ -> │   Test   │ -> │  Build   │ -> │Integration│
│          │    │   ETL    │    │  Docker  │    │   Test    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Production Considerations
- Use Docker secrets for credentials
- Set up monitoring (Prometheus/Grafana)
- Configure log aggregation (ELK stack)
- Enable Airflow alerting
- Set up database backups
- Use connection pooling
- Configure autoscaling

## Performance Optimization

1. **Database**
   - Indexed watermark columns
   - Partitioned fact tables
   - Materialized views for marts

2. **ETL**
   - Batch processing (configurable size)
   - Parallel table processing
   - Connection pooling

3. **dbt**
   - Incremental models for large facts
   - View materialization for staging
   - Table materialization for marts

## Security

- Environment-based configuration
- No hardcoded credentials
- Network isolation
- Database user permissions
- Container security best practices
