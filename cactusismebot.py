import time
import datetime
import re
import mwparserfromhell
import pywikibot

try:
    from webcite import citationdotorg
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

    print(f"Post age: {post_age} days, No comments for: {no_comment_duration} days")

    return post_age >= 7 or no_comment_duration >= 2

def archive_page(page):
    orig = page.get()
    text = mwparserfromhell.parse(orig)
    archive_title = "विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)"
    
    print(f"Checking archive conditions for page: {page.title()}")
    if check_archive_conditions(page.creation_date, page.last_comment_date):
        print(f"Archiving {page.title()} to {archive_title}")
        archive_page = pywikibot.Page(pywikibot.Site(), archive_title)
        archive_page.put(str(text), 'बॉट: पोस्ट पुरालेखित किया गया')
        page.delete(reason="बॉट: पोस्ट पुरालेखित किया गया", prompt=False)
    else:
        print(f"Skipping archive: {page.title()} does not meet conditions")

def modify_all_of_page(page):
    links = page.extlinks()
    orig = page.get()
    text = mwparserfromhell.parse(orig)

    print(f"Processing page: {page.title()}")
    print(f"Found {len(links)} external links")
    
    for link in links:
        if 'wiki' in link or not link.startswith(('http', 'ftp', 'https')):
            continue

        try:
            url = citationdotorg.archive_url(link)['webcite_url']
            print(f"Archived link: {url}")
            text = add_template(text, link, url)
        except Exception as e:
            print(f"ERROR archiving {link}: {e}")
        
        time.sleep(5)

    print("Updating page content...")
    page.put(str(text), 'बॉट: मैनुअल परीक्षण द्वारा ऑपरेशन')

def test_edit():
    site = pywikibot.Site()
    
    # Authenticate bot using recommended method
    try:
        print("Logging in with Pywikibot...")
        site.login()  # Ensure authentication before proceeding
        print("Bot logged in successfully!")
    except Exception as e:
        print(f"ERROR: Bot login failed - {e}")
        return

    page = pywikibot.Page(site, "सदस्य:Cactusisme/Sandbox")
    print(f"Attempting to edit {page.title()}...")

    try:
        page.put("Testing bot edit", "Automated edit test")
        print("Test edit completed successfully!")
    except Exception as e:
        print(f"ERROR: Failed to edit page - {e}")

if __name__ == "__main__":
    print("Script is running...")

    # Ensure login before modifying pages
    try:
        import subprocess
        subprocess.run(["python", "pwb.py", "login"], check=True)
    except Exception as e:
        print(f"ERROR executing Pywikibot login: {e}")

    # Test authentication and edit the sandbox
    test_edit()
