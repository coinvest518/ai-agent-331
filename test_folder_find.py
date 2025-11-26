"""Test finding AI Video folder."""

from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    entity_id=os.getenv("GOOGLEDRIVE_ENTITY_ID")
)

result = composio_client.tools.execute(
    "GOOGLEDRIVE_FIND_FOLDER",
    {"name_exact": "AI Video"},
    connected_account_id=os.getenv("GOOGLEDRIVE_CONNECTION_ID")
)

print(f"Folder search result: {result}")
