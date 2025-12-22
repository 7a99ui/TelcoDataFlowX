# 🐰 Trino Analytics Setup

This folder contains the configuration and SQL scripts to set up the Analytics layer for the Telco Churn project.

## 🚀 Quick Start (Running Analytics)

### 1. Prerequisites
Ensure the Trino container is running:
```bash
docker-compose up -d trino
```

### 2. Run the Initialization Script
We have consolidated everything (Schema setup, Table registration, and Views) into one file: **`init_analytics.sql`**.

Run it inside the Trino container:

```bash
# Option A: Interactive Shell (Recommended)
docker exec -it trino trino

# Then paste the contents of init_analytics.sql or run specific sections
```

### 3. What `init_analytics.sql` Does
1.  **Creates Schema**: `delta.telco_churn`
2.  **Registers Tables**: `bronze`, `silver`, `gold` (links to MinIO/S3)
    *   *Note: Use `silver` for BI/Analytics. `gold` is for ML training.*
3.  **Creates Views**:
    *   `view_master_dashboard`: The main view for Superset/BI tools with calculated segments.
    *   `view_kpi_summary`: Pre-calculated KPI aggregates.
    *   `view_contract_metrics`: Contract breakdown.

### 4. Connect BI Tool (Superset/Tableau/DBeaver)
*   **Host**: `localhost`
*   **Port**: `8091` (SQL Client port)
*   **Catalog**: `delta`
*   **Schema**: `telco_churn`
*   **User**: `admin`
*   **Password**: (None / Empty)

### 5. Configuration Files
*   `etc/catalog/delta.properties`: Critical config for S3 + Delta Lake + Local Metastore support.
*   `etc/catalog/minio.properties`: (Deprecated/Archive) Legacy Hive/S3 config.
*   `etc/config.properties`: Trino server settings.
