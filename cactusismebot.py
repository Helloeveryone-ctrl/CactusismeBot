import mwclient
import logging
import re
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Test Wikipedia
site = mwclient.Site("test.wikipedia.org", scheme="https")

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

def extract_vandal_username(line):
    """Extracts the username or IP from {{vandal}} or {{ipvandal}} templates."""
    match = re.search(r"{{(?:vandal|ipvandal)\|([^}]+)}}", line)
    if match:
        vandal_username = match.group(1).strip()
        logging.debug(f"Extracted vandal username: {vandal_username} from line: {line}")
        return vandal_username
    return None

def process_vip_reports(clear_old=False, dry_run=False):
    """Processes reports on WP:VIP, marks blocked vandals as done, and optionally clears old reports."""
    page = site.pages["Wikipedia:VIP"]  # VIP page

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
                        # Retrieve user information correctly
                        user_info = site.users([vandal_username]).get(vandal_username, {})

                        if user_info and user_info.get("blockedby"):
                            # Mark as done
                            line += " {{done}} --~~~~"
                            changes_made = True
                            blocking_admin = user_info.get("blockedby")
                            logging.info(f"Marked {vandal_username} as done (Blocked by {blocking_admin}).")
                        else:
                            logging.info(f"User {vandal_username} is not blocked or missing data.")

                    except Exception as user_error:
                        logging.error(f"Error processing user {vandal_username}: {user_error}")

            updated_text.append(line)

        # Optionally clear the VIP page if all reports are marked as done
        if clear_old and all("{{done}}" in l for l in updated_text if extract_vandal_username(l)):
            logging.info("All reports are resolved, clearing VIP page.")
            updated_text = ["== Current reports =="]

        # Save changes if updates were made
        if changes_made or clear_old:
            if dry_run:
                logging.info("Dry run mode: Changes are not being saved.")
                logging.debug("Updated text content:\n" + "\n".join(updated_text))
            else:
                page.edit("\n".join(updated_text), summary="Marking reports as done and/or clearing VIP.")
                logging.info("Updated Wikipedia:VIP successfully.")
        else:
            logging.info("No changes needed on Wikipedia:VIP.")

    except Exception as e:
        logging.error(f"Error processing Wikipedia:VIP: {e}")

# Run the bot
if __name__ == "__main__":
    process_vip_reports(clear_old=True, dry_run=False)  # Set dry_run=True to test without saving changes
