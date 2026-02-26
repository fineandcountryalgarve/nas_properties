from nas_properties.np_extract import fetch_description_file
from nas_properties.np_transform import parse_description_file
from nas_properties.np_load import upload_to_postgres, cleanup_temp_file
from publications.sa_extract import extract_socialmedia_data
from publications.sa_transform import transform_socialmedia_data
from publications.ps_load import load_to_google_sheets
from app.utils.gsheets_worksheets import get_gsheets_id


# Social media publishing configuration (mirrors sa_controller)
SHEET_ID = get_gsheets_id("publications")
WORKSHEET_NAME = "social_media"


def np_extract(reference: str, folder_name: str, project_folder: str = None) -> str:
    """Extract: Download description file from Google Drive."""
    file_path = fetch_description_file(reference, folder_name, project_folder)
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


def np_socialmedia(full_reference: str) -> bool:
    """Publish: Extract social media data from warehouse and send to Google Sheets."""
    print("\n" + "="*60)
    print("📱 SOCIAL MEDIA PUBLISH STEP")
    print("="*60)

    raw_df = extract_socialmedia_data([full_reference])
    if raw_df is None:
        print("⚠️ No social media data extracted.")
        return False

    transformed_df = transform_socialmedia_data(raw_df)
    if transformed_df is None:
        print("⚠️ Social media transform failed.")
        return False

    success = load_to_google_sheets(
        df=transformed_df,
        sheet_id=SHEET_ID,
        worksheet_name=WORKSHEET_NAME,
        include_headers=False,
        add_date_column=True,
        start_row=2
    )
    print("Social media publish stage completed." if success else "Social media publish stage failed.")
    return success


if __name__ == "__main__":
    # Example usage for testing
    # Regular property:
    reference = "FC1075VC"
    folder_name = "VILLAS_AND_CONTRACTS"
    file_path = np_extract(reference, folder_name)

    # Agency agreement (with project_folder):
    # reference = "FH_B1_01_P0"
    # folder_name = "AGENCY_AGREEMENTS"
    # file_path = np_extract(reference, folder_name, project_folder="Ferragudo Hills")

    transform_result = np_transform(file_path)
    np_load(transform_result)
