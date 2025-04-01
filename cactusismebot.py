import mwclient
import logging
import re
import os
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Test Wikipedia with a timeout
site = mwclient.Site("test.wikipedia.org", timeout=10)

USERNAME = os.getenv("WIKI_USERNAME")
PASSWORD = os.getenv("WIKI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Environment variables WIKI_USERNAME and WIKI_PASSWORD are not defined.")

try:
    site.login(USERNAME, PASSWORD)
    logging.info("Bot logged in successfully.")
except mwclient.LoginError as e:
    logging.error(f"Login failed: {e}")
    exit(1)

def remove_red_linked_templates_from_page(page):
    """Removes red-linked templates efficiently."""
    try:
        page_text = page.text()
        logging.info(f"Checking page: {page.name}")

        # Find all templates in one pass
        templates = re.findall(r"\{\{([^}|]+)(?:\|[^}]+)?\}\}", page_text)
        red_templates = [t for t in templates if not site.pages[f"Template:{t}"].exists]

        if not red_templates:
            logging.info(f"No red-linked templates on {page.name}.")
            return

        # Remove all red templates in one operation
        for template_name in red_templates:
            page_text = re.sub(rf"\{{\{{{re.escape(template_name)}\}}\}}", "", page_text)

        page.edit(page_text, summary="Removed red-linked templates.")
        logging.info(f"Updated page: {page.name}")

    except Exception as e:
        logging.error(f"Error processing {page.name}: {e}")

def scan_wiki_for_red_linked_templates():
    """Scans up to 100 pages and removes red-linked templates."""
    for i, page in enumerate(site.allpages(namespace=0)):  # Main namespace
        if i >= 100:  # Process only 100 pages per run
            break
        remove_red_linked_templates_from_page(page)
        time.sleep(2)  # Wait 2 seconds between edits

# Run the bot
if __name__ == "__main__":
    scan_wiki_for_red_linked_templates()
