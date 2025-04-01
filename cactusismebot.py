import mwclient
import logging
import re
import os
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Test Wikipedia
site = mwclient.Site("test.wikipedia.org")

USERNAME = os.getenv("WIKI_USERNAME")
PASSWORD = os.getenv("WIKI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Environment variables WIKI_USERNAME and WIKI_PASSWORD are not defined.")

try:
    site.login(USERNAME, PASSWORD)
    logging.info(f"Bot logged in successfully as {site.username}")
except mwclient.LoginError as e:
    logging.error(f"Login failed: {e}")
    exit(1)

def extract_vandal_username(line):
    """Extract the username or IP from vandal templates using regex."""
    match = re.search(r"{{(?:vandal|ipvandal)\|([^}]+)}}", line)
    vandal_username = match.group(1).strip() if match else None
    logging.debug(f"Extracted vandal username: {vandal_username} from line: {line}")
    return vandal_username

def process_vip_reports(dry_run=False):
    """Processes reports on WP:VIP and marks blocked vandals as done."""
    page = site.pages["Wikipedia:VIP"]  # WP:VIP page

    try:
        # Get the text of the page
        vip_text = page.text()
        logging.debug(f"Retrieved page content:\n{vip_text}")

        lines = vip_text.split("\n")
        updated_text = []
        changes_made = False

        for line in lines:
            if "{{done}}" not in line:
                vandal_username = extract_vandal_username(line)

                if vandal_username:
                    try:
                        # Retrieve user information
                        user_info_list = site.users([vandal_username])
                        user_info = next(iter(user_info_list), None)  # Get first user info from iterator
                        logging.debug(f"User info for {vandal_username}: {user_info}")

                        if user_info and user_info.get("blockedby"):
                            # Mark as done
                            line += " {{done}} --~~~~"
                            changes_made = True
                            blocking_admin = user_info.get("blockedby")
                            logging.info(f"Marked {vandal_username} as done (Blocked by {blocking_admin}).")
                        else:
                            logging.info(f"User {vandal_username} is not blocked or information is missing.")

                    except Exception as user_error:
                        logging.error(f"Error processing user {vandal_username}: {user_error}")

            updated_text.append(line)

        # Save changes to WP:VIP if there are updates
        if changes_made:
            if dry_run:
                logging.info("Dry run mode: Changes are not being saved.")
                logging.debug("Updated text content:\n" + "\n".join(updated_text))
            else:
                page.edit("\n".join(updated_text), summary="Marking reports as done.")
                logging.info("Updated Wikipedia:VIP successfully.")
        else:
            logging.info("No changes needed on Wikipedia:VIP.")

    except Exception as e:
        logging.error(f"Error processing Wikipedia:VIP: {e}")

# Run the bot every minute
if __name__ == "__main__":
    while True:
        process_vip_reports(dry_run=False)  # Set to True for testing without saving changes
        logging.info("Sleeping for 1 minute...")
        time.sleep(60)
