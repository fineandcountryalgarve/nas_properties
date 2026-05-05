# Automation Plan: Automated Property Updates to BigQuery (New Files Only)

This plan outlines the automation of the `nas_properties` process by creating **entirely new files**, ensuring no existing code is modified. The target is a new BigQuery table.

## User Review Required

> [!IMPORTANT]
> **No Modifications**: We will NOT modify `np_load.py`, `nas_properties_dag.py`, or `app/utils/gdrive.py`. All logic will reside in new dedicated files.
> [!NOTE]
> **BigQuery Table**: We need to ensure the `bronze.nas_properties` table in BigQuery is ready. While `dlt` can auto-create it, we'll verify the schema manually to include standard `dlt` metadata.

## Proposed Changes

### 1. Extraction & Automation Logic
#### [NEW] [np_automation.py](file:///home/rafaelc/Projects/fc_algarve/nas_properties/np_automation.py)
- Create a `dlt` source that uses `app.utils.gdrive.get_gdrive_service()`.
- Implement a custom `list_modified_files` helper within this file (to avoid modifying `gdrive.py`) that filters by `modifiedTime`.
- Yields records for `dlt`.

### 2. Loading Logic
#### [NEW] [np_load_bq.py](file:///home/rafaelc/Projects/fc_algarve/nas_properties/np_load_bq.py)
- Dedicated loader for BigQuery using `dlt`.
- Configured for `write_disposition="merge"` on the `reference` column.
- Uses `fc-airbyte-sa.json` for credentials.

### 3. Automated Airflow DAG
#### [NEW] [np_dag_bq.py](file:///home/rafaelc/Projects/fc_algarve/airflow-docker/dags/np_bq_dag.py)
- New DAG scheduled at `0 17 * * *`.
- Exclusively handles the incremental load to BigQuery.

## BigQuery Table Setup

You mentioned you can create the table with the `dlt` state columns. For reference, here is the expected schema structure for the `bronze.nas_properties` table:

```sql
CREATE TABLE IF NOT EXISTS `finecountrydatabase.bronze.nas_properties` (
    reference STRING,
    -- ... other property columns (price, location, etc.) ...
    source_modified_at TIMESTAMP,
    _dlt_load_id STRING,
    _dlt_id STRING NOT NULL
)
PARTITION BY DATE(source_modified_at);
```
*(Note: dlt will automatically handle column addition if new fields appear in the Word docs)*

## Implementation Steps

1. **Phase 1: Logic Development**
   - Create `np_automation.py` with the GDrive listing logic.
   - Create `np_load_bq.py` for the dlt-to-BQ pipeline.

2. **Phase 2: DAG Setup**
   - Create `np_bq_dag.py` in the dags folder.

3. **Phase 3: Verification**
   - Run the DAG once to verify it correctly creates/merges data into BigQuery.

## Verification Plan

### Automated Tests
- Verify `np_automation.py` lists only files modified since a given date.
- Dry-run the `dlt` pipeline to ensure credentials and dataset access are correct.

### Manual Verification
- Confirm the new `nas_properties` table appears in BigQuery after the first run.
- Update a price in Drive and verify it syncs to BigQuery via the new DAG.
