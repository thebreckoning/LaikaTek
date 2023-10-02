#!/usr/bin/python3
# keymaster.py

# For future handling of Azure key vault keys and/or secrets using the Azure SDK for Python
# Not yet in use

import os
from azure.identity import ClientSecretCredential
from azure.keyvault.keys import KeyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read credentials from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
db_root_passkey = os.getenv("DB_ROOT_KEY")
db_special_passkey = os.getenv("DB_SPECIAL_KEY")
vault_name=os.getenv("VAULT_NAME")

# Set up the Key Vault client using ClientSecretCredential
vault_url = "https://{vault_name}.vault.azure.net/"
credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)
client = KeyClient(vault_url=vault_url, credential=credential)

# db pass
retrieve_special_passkey = client.get_key(name=db_special_passkey)
retrieve_root_passkey = client.get_key(name=db_root_passkey)

# Get the key's value
db_root_passkey = retrieve_root_passkey.key
db_special_passkey = retrieve_special_passkey.key


