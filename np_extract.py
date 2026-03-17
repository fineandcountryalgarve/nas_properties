import io
import tempfile
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.utils.drive_folders import get_folder_id
from app.utils.mimetypes import MIMETYPES

_KEY_DOCKER = Path("/keys/fc-pipeline-reader.json")
_KEY_LOCAL = Path(__file__).parent.parent.parent / "keys" / "fc-pipeline-reader.json"


def _get_drive_service():
    key_path = _KEY_DOCKER if _KEY_DOCKER.exists() else _KEY_LOCAL
    creds = service_account.Credentials.from_service_account_file(
        str(key_path),
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=creds)


def _list_files(service, folder_id, name_contains=None, mime_type=None):
    query = f"'{folder_id}' in parents and trashed = false"
    if name_contains:
        query += f" and name contains '{name_contains}'"
    if mime_type:
        query += f" and mimeType = '{mime_type}'"
    results = service.files().list(
        q=query, fields="files(id, name, createdTime)", pageSize=100
    ).execute()
    return results.get("files", [])


def _download_file(service, file_id, destination_path):
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(destination_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return destination_path


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

    root_folder_id = get_folder_id(folder_name)
    if not root_folder_id:
        raise ValueError(f"Folder '{folder_name}' not found in config.")

    service = _get_drive_service()

    search_term = project_folder if project_folder else reference
    print(f"Looking for folder '{search_term}' (reference: '{reference}') in '{folder_name}' (ID: {root_folder_id})")

    subfolders = _list_files(service, root_folder_id, name_contains=search_term, mime_type=MIMETYPES["folder"])
    if not subfolders:
        raise FileNotFoundError(f"No subfolder found containing '{reference}' in folder '{folder_name}'.")

    reference_folder = subfolders[0]
    reference_folder_id = reference_folder["id"]
    print(f"Found reference folder: {reference_folder['name']} (ID: {reference_folder_id})")

    file_search_term = reference if project_folder else "description"
    description_files = _list_files(
        service, reference_folder_id, name_contains=file_search_term, mime_type=MIMETYPES["docx"]
    )
    if not description_files:
        raise FileNotFoundError(
            f"No description file containing '{file_search_term}' found in folder '{reference_folder['name']}'."
        )

    description_file = description_files[0]
    print(f"Found description file: {description_file['name']} (ID: {description_file['id']})")

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        temp_path = tmp.name

    _download_file(service, description_file["id"], temp_path)
    print(f"Downloaded description file to: {temp_path}")

    return temp_path
