import os

# Retrieve credentials from environment variables (set via GitHub Secrets)
wiki_username = os.getenv("WIKI_USERNAME")
wiki_password = os.getenv("WIKI_PASSWORD")

if not wiki_username or not wiki_password:
    raise ValueError("ERROR: Wiki credentials not found! Ensure GitHub Secrets are set.")

# Return credentials securely
credentials = (wiki_username, wiki_password)
