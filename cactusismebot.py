import mwclient
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Simple Wikipedia
site = mwclient.Site("simple.wikipedia.org")

# Bot login
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

# Function to get section titles and original posters
def get_sections_and_posters(page_title):
    page = site.pages[page_title]
    if not page.exists:
        logging.error("Page does not exist.")
        return {}
    
    page_text = page.text()
    section_posters = {}
    
    # Regex to find == Section Headers == and extract the first signature after them
    section_pattern = re.compile(r'==\s*(.*?)\s*==.*?(\[\[User:[^|]+\|([^]]+)\]\])', re.DOTALL)
    
    for match in section_pattern.finditer(page_text):
        section_title = match.group(1).strip()
        poster_username = match.group(3).strip()
        section_posters[section_title] = poster_username
    
    return section_posters

# Function to notify users if their section is removed
def notify_users(original_sections, new_sections, talk_page):
    for section, user in original_sections.items():
        if section not in new_sections:
            logging.info(f"Notifying {user} about missing section: {section}")
            message = f"Hello [[User:{user}|{user}]],\n\nYour discussion section titled '{section}' on [[Wikipedia:Simple talk]] has been archived or removed. Please check the archives or re-add the discussion if necessary.\n\n-- ~~~~"
            
            user_talk_page = site.pages[f"User talk:{user}"]
            user_talk_page.text()  # Ensure we fetch the latest version
            user_talk_page.save(user_talk_page.text() + '\n\n' + message, summary="Notifying user about archived/deleted section.")

# Main execution
if __name__ == "__main__":
    TALK_PAGE = "Wikipedia:Simple talk"
    
    logging.info("Fetching original sections...")
    original_sections = get_sections_and_posters(TALK_PAGE)
    
    logging.info("Checking for updates...")
    new_sections = get_sections_and_posters(TALK_PAGE)
    
    notify_users(original_sections, new_sections, TALK_PAGE)
    
    logging.info("Script completed.")
