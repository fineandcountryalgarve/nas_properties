import tempfile
from app.utils.drive_folders import get_folder_id
from app.utils.gdrive import list_files_in_folder, download_file_from_drive
from app.utils.mimetypes import MIMETYPES


def fetch_description_file(reference: str, folder_name: str, project_folder: str = None) -> str:
    """
    Fetch description file from Google Drive for a given reference.
    Returns the path to the downloaded file.

    Args:
        reference: Property reference (e.g., FC1075VC or FH_B1_01_P0)
        folder_name: Root folder name in config (e.g., VILLAS_AND_CONTRACTS)
        project_folder: Optional project folder name for agency agreements
                        (e.g., 'Ferragudo Hills'). If not provided, uses reference.
    """
    if not reference:
        raise ValueError("Parameter 'reference' is required.")
    if not folder_name:
        raise ValueError("Parameter 'folder_name' is required.")

    # Get root folder ID from config
    root_folder_id = get_folder_id(folder_name)
    if not root_folder_id:
        raise ValueError(f"Folder '{folder_name}' not found in config.")

    # Use project_folder if provided, otherwise fall back to reference
    search_term = project_folder if project_folder else reference

    print(f"Looking for folder '{search_term}' (reference: '{reference}') in '{folder_name}' (ID: {root_folder_id})")

    # Find the reference subfolder
    subfolders = list_files_in_folder(
        root_folder_id,
        name_contains=search_term,
        mime_type=MIMETYPES["folder"]
    )

    if not subfolders:
        raise FileNotFoundError(f"No subfolder found containing '{reference}' in folder '{folder_name}'.")

    # Use the first matching subfolder
    reference_folder = subfolders[0]
    reference_folder_id = reference_folder["id"]
    print(f"Found reference folder: {reference_folder['name']} (ID: {reference_folder_id})")

    # Look for description file in the subfolder
    # For agency agreements (project_folder provided), search by reference since multiple
    # units share the same folder. For regular properties, search by "description".
    file_search_term = reference if project_folder else "description"

    description_files = list_files_in_folder(
        reference_folder_id,
        name_contains=file_search_term,
        mime_type=MIMETYPES["docx"]
    )

    if not description_files:
        raise FileNotFoundError(f"No description file containing '{file_search_term}' found in folder '{reference_folder['name']}'.")

    description_file = description_files[0]
    print(f"Found description file: {description_file['name']} (ID: {description_file['id']})")

    # Download the file to a temp location
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        temp_path = tmp.name

    download_file_from_drive(description_file["id"], temp_path)
    print(f"Downloaded description file to: {temp_path}")

    return temp_path
