import mwclient
import logging
import re
import os

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

def remove_red_links(page_title, dry_run=False):
    """Removes red-linked articles from a specific page."""
    page = site.pages[page_title]  # Target page

    try:
        # Get the text of the page
        page_text = page.text()
        logging.info(f"Retrieved page content for {page_title}")

        # Regex to find red-linked articles
        red_link_pattern = r"

\[

\[(?:[^|\]

]+\|)?([^\]

]+)\]

\]

"  # Fixed and complete regex pattern
        updated_text = []
        changes_made = False

        lines = page_text.split("\n")
        for line in lines:
            # Check and remove red links
            updated_line = line
            for match in re.finditer(red_link_pattern, line):
                link_target = match.group(1).strip()
                if not site.pages[link_target].exists:  # Check if the page exists
                    logging.info(f"Removing red link: {link_target}")
                    updated_line = updated_line.replace(match.group(0), link_target)  # Replace with plain text
                    changes_made = True
            updated_text.append(updated_line)

        # Save changes if updates are made
        if changes_made:
            if dry_run:
                logging.info("Dry run mode: Changes are not being saved.")
                logging.debug("Updated text content:\n" + "\n".join(updated_text))
            else:
                page.edit("\n".join(updated_text), summary="Removed red-linked articles.")
                logging.info(f"Updated {page_title} successfully.")
        else:
            logging.info(f"No red links found on {page_title}.")

    except Exception as e:
        logging.error(f"Error processing {page_title}: {e}")

# Run the function
if __name__ == "__main__":
    remove_red_links("User talk:Cactusisme/Archive 2", dry_run=False)  # Set to True for testing
