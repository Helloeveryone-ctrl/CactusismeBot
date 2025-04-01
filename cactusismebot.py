import mwclient
import logging
import os
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Test Wikipedia
site = mwclient.Site("test.wikipedia.org")

# Get credentials from environment variables
USERNAME = os.getenv("WIKI_USERNAME")
PASSWORD = os.getenv("WIKI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Environment variables WIKI_USERNAME and WIKI_PASSWORD are not defined.")

# Login to the site
try:
    site.login(USERNAME, PASSWORD)
    logging.info("Bot logged in successfully.")
except mwclient.LoginError as e:
    logging.error(f"Login failed: {e}")
    exit(1)

def add_no_sources_template(page_title, dry_run=False):
    """Adds {{No sources}} template to articles with no references."""
    page = site.pages[page_title]  # Target page

    try:
        # Get the text of the page
        page_text = page.text()
        logging.info(f"Retrieved page content for {page_title}")

        # Check if the page contains references or <ref> tags
        if "<ref>" not in page_text:  # If no <ref> tags exist, the page likely has no sources
            # Check if the template is already added
            if "{{No sources}}" not in page_text:
                # Add the {{No sources}} template at the top of the page
                new_page_text = "{{No sources}}\n" + page_text
                logging.info(f"Adding {{No sources}} template to {page_title}")

                # Only update if not in dry-run mode
                if not dry_run:
                    page.edit(new_page_text, summary="Adding {{No sources}} template")
                    logging.info(f"Successfully added {{No sources}} template to {page_title}.")
                else:
                    logging.info(f"Dry run mode: Not saving changes to {page_title}.")
            else:
                logging.info(f"Page {page_title} already has the {{No sources}} template.")
        else:
            logging.info(f"Page {page_title} has references, skipping...")

    except Exception as e:
        logging.error(f"Error processing {page_title}: {e}")

def run_bot():
    """Fetches pages and adds {{No sources}} to those without references."""
    # Set up a list of pages to check
    pages_to_check = [
        "ExamplePage1",  # Add your target pages here
        "ExamplePage2",
        # You can also use a page list from an API or another source
    ]

    for page_title in pages_to_check:
        add_no_sources_template(page_title, dry_run=True)  # Set dry_run to False when you're ready to update

if __name__ == "__main__":
    run_bot()
