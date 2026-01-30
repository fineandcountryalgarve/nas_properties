from nas_properties.np_extract import fetch_description_file
from nas_properties.np_transform import parse_description_file
from nas_properties.np_load import upload_to_postgres, cleanup_temp_file


def np_extract(reference: str, folder_name: str) -> str:
    """Extract: Download description file from Google Drive."""
    file_path = fetch_description_file(reference, folder_name)
    print("Extract stage completed.")
    return file_path


def np_transform(file_path: str) -> dict:
    """Transform: Parse the description file into a DataFrame."""
    df = parse_description_file(file_path)
    print("Transform stage completed.")
    return {"file_path": file_path, "df": df}


def np_load(transform_result: dict) -> None:
    """Load: Upload DataFrame to PostgreSQL and cleanup."""
    df = transform_result["df"]
    file_path = transform_result["file_path"]

    upload_to_postgres(df)
    cleanup_temp_file(file_path)
    print("Load stage completed.")


if __name__ == "__main__":
    # Example usage for testing
    reference = "FC1075VC"
    folder_name = "VILLAS_AND_CONTRACTS"

    file_path = np_extract(reference, folder_name)
    transform_result = np_transform(file_path)
    np_load(transform_result)
