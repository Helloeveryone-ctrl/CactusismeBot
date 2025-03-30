import mwclient
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Simple English Wikipedia
site = mwclient.Site("simple.wikipedia.org")  # Change this if WP:VIP is on another project

import os

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
    """Extract the username or IP from the {{vandal|Username}} or {{ipvandal|Username}} template."""
    if "{{vandal|" in line or "{{ipvandal|" in line:
        template_start = "{{vandal|" if "{{vandal|" in line else "{{ipvandal|"
        start = line.index(template_start) + len(template_start)
        end = line.index("}}", start)
        return line[start:end].strip()
    return None

def process_vip_reports():
    """Processes reports on WP:VIP and marks blocked vandals as done."""
    page = site.pages["Wikipedia:Vandalism in progress"]  # WP:VIP page

    try:
        # Get the text of the page
        vip_text = page.text()

        # Split into sections or lines
        lines = vip_text.split("\n")
        updated_text = []
        changes_made = False

        for line in lines:
            if "{{done}}" not in line and ("{{vandal|" in line or "{{ipvandal|" in line):
                vandal_username = extract_vandal_username(line)

                if vandal_username:
                    # Retrieve user information
                    user_info_list = site.users([vandal_username])
                    user_info = user_info_list[0] if user_info_list else None

                    if user_info and "blockedby" in user_info:
                        # Mark as done
                        line += " {{done}}--~~~~"
                        changes_made = True
                        blocking_admin = user_info.get("blockedby")
                        logging.info(f"Marked {vandal_username} as done (Blocked by {blocking_admin}).")

            updated_text.append(line)

        # Save changes to WP:VIP if there are updates
        if changes_made:
            page.edit("\n".join(updated_text), summary="Marking reports as done.")
            logging.info("Updated Wikipedia:VIP successfully.")
        else:
            logging.info("No changes needed on Wikipedia:VIP.")

    except Exception as e:
        logging.error(f"Error processing Wikipedia:VIP: {e}")

# Run the bot once (to be scheduled via cron job or GitHub Actions)
if __name__ == "__main__":
    process_vip_reports()

