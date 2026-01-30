import pandas as pd
from docx import Document


def parse_description_file(file_path: str) -> pd.DataFrame:
    """
    Parse the description .docx file and return a DataFrame.
    """
    doc = Document(file_path)

    if not doc.tables:
        raise ValueError("No tables found in the description document.")

    table = doc.tables[0]
    data = {}
    for row in table.rows:
        key = row.cells[0].text.strip()
        value = row.cells[1].text.strip()
        if key.lower() == "property features":
            value = "; ".join(
                line.strip().lstrip("•·●■-– ").strip() for line in value.splitlines() if line.strip()
            )
        data[key] = value

    publishing_properties = pd.DataFrame(list(data.items()), columns=["Key", "Value"])
    publishing_properties = publishing_properties.set_index("Key").T.reset_index(drop=True)
    publishing_properties.columns = publishing_properties.columns.map(str.lower)

    print(f"Parsed properties:\n{publishing_properties.to_string()}")

    return publishing_properties
