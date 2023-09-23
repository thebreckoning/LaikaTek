#!/usr/bin/python3
import os
from azure.identity import ClientSecretCredential
from azure.keyvault.keys import KeyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read credentials from environment variables
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
tenant_id = os.getenv("tenant_id")

# Set up the Key Vault client using ClientSecretCredential
vault_url = "https://laikatek.vault.azure.net/"
credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)
client = KeyClient(vault_url=vault_url, credential=credential)

# db pass
key_name = "ltdb"
retrieved_key = client.get_key(name=key_name)

# Get the key's value
db_password = retrieved_key.key