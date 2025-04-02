import time
import datetime
import re
import mwparserfromhell
import pywikibot  # Ensure Pywikibot is imported

try:
    from webcite import citationdotorg  # Ensure citationdotorg is installed
except ImportError:
    print("ERROR: citationdotorg module not found. Install it or provide an alternative.")

CITE_WEB_TEMPLATE = '{{cite web|url=%s|title=%s|archiveurl=%s|archivedate=%s|deadurl=no}}'

def calculate_date():
    now = datetime.datetime.utcnow()
    return now.strftime('%d %B %Y')

def check_archive_conditions(post_date, last_comment_date):
    now = datetime.datetime.utcnow()
    post_age = (now - post_date).days
    no_comment_duration = (now - last_comment_date).days

    print(f"Post age: {post_age} days, No comments for: {no_comment_duration} days")  # Debug log

    return post_age >= 7 or no_comment_duration >= 2

def archive_page(page):
    orig = page.get()
    text = mwparserfromhell.parse(orig)
    archive_title = "विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)"
    
    print(f"Checking archive conditions for page: {page.title()}")  # Debug log
    if check_archive_conditions(page.creation_date, page.last_comment_date):
        print(f"Archiving {page.title()} to {archive_title}")  # Debug log
        archive_page = pywikibot.Page(pywikibot.Site(), archive_title)
        archive_page.put(str(text), 'बॉट: पोस्ट पुरालेखित किया गया')
        page.delete(reason="बॉट: पोस्ट पुरालेखित किया गया", prompt=False)
    else:
        print(f"Skipping archive: {page.title()} does not meet conditions")  # Debug log

def modify_all_of_page(page):
    links = page.extlinks()
    orig = page.get()
    text = mwparserfromhell.parse(orig)

    print(f"Processing page: {page.title()}")  # Debug log
    print(f"Found {len(links)} external links")  # Debug log
    
    for link in links:
        if 'wiki' in link or not link.startswith(('http', 'ftp', 'https')):
            continue

        try:
            url = citationdotorg.archive_url(link)['webcite_url']
            print(f"Archived link: {url}")  # Debug log
            text = add_template(text, link, url)
        except Exception as e:
            print(f"ERROR archiving {link}: {e}")  # Debug log
        
        time.sleep(5)

    print("Updating page content...")  # Debug log
    page.put(str(text), 'बॉट: मैनुअल परीक्षण द्वारा ऑपरेशन')

def test_edit():
    site = pywikibot.Site()
    page = pywikibot.Page(site, "सदस्य:Cactusisme/Sandbox")  # Uses sandbox for testing edits
    print(f"Attempting to edit {page.title()}...")  # Debug log

    try:
        page.put("Testing bot edit", "Automated edit test")  # Test edit
        print("Test edit completed successfully!")  # Debug log
    except Exception as e:
        print(f"ERROR: Failed to edit page - {e}")  # Debug log

if __name__ == "__main__":
    print("Script is running...")
    
    # Test authentication by making a simple edit
    test_edit()
