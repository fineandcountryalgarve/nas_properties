import os
import pandas as pd
from app.utils.db_engine import get_engine


def upload_to_postgres(df: pd.DataFrame) -> None:
    """
    Upload DataFrame to PostgreSQL, replacing existing data.
    """
    if df.empty or df.shape[1] == 0:
        raise ValueError(f"DataFrame is empty or has no columns — nothing to upload. Shape: {df.shape}")

    engine = get_engine()
    df.to_sql(
        "nas_properties",
        engine,
        schema="bronze",
        if_exists="append",
        index=False
    )
    print("Property information sent to PostgreSQL.")


def cleanup_temp_file(file_path: str) -> None:
    """
    Remove temporary file.
    """
    if file_path and os.path.exists(file_path):
        os.unlink(file_path)
        print(f"Cleaned up temp file: {file_path}")
