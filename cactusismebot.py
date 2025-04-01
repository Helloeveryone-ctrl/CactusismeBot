import mwclient
import logging
import re
import os
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Test Wikipedia
site = mwclient.Site("test.wikipedia.org")

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
    """Removes red-linked templates from a single Wikipedia page."""
    try:
        # Get the text of the page
        page_text = page.text()
        logging.info(f"Checking page: {page.name}")

        # Regex pattern to find template transclusions {{TemplateName}}
        template_pattern = r"\{\{([^}|]+)(?:\|[^}]+)?\}\}"

        updated_text = []
        changes_made = False

        lines = page_text.split("\n")
        for line in lines:
            updated_line = line
            for match in re.finditer(template_pattern, line):
                template_name = match.group(1).strip()

                # Check if the template exists
                if not site.pages[f"Template:{template_name}"].exists:
                    logging.info(f"Removing red-linked template: {{ {template_name} }} from {page.name}")
                    updated_line = updated_line.replace(match.group(0), "")  # Remove the template
                    changes_made = True

            updated_text.append(updated_line)

        # Save changes if updates were made
        if changes_made:
            page.edit("\n".join(updated_text), summary="Removed red-linked templates.")
            logging.info(f"Updated page: {page.name}")
        else:
            logging.info(f"No red-linked templates found on {page.name}.")

    except Exception as e:
        logging.error(f"Error processing {page.name}: {e}")

def scan_wiki_for_red_linked_templates():
    """Scans every page on the wiki and removes red-linked templates."""
    for page in site.allpages(namespace=0):  # Scans all main namespace pages
        remove_red_linked_templates_from_page(page)
        time.sleep(1)  # Delay to avoid API spam

# Run the bot
if __name__ == "__main__":
    scan_wiki_for_red_linked_templates()
