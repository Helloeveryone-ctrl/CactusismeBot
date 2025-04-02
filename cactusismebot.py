import time
import datetime
import re
import mwparserfromhell

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
    return post_age >= 7 or no_comment_duration >= 2

def archive_page(page):
    orig = page.get()
    text = mwparserfromhell.parse(orig)
    archive_title = "विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)"
    
    if check_archive_conditions(page.creation_date, page.last_comment_date):
        archive_page = pywikibot.Page(pywikibot.Site(), archive_title)
        archive_page.put(str(text), 'बॉट: पोस्ट पुरालेखित किया गया')
        page.delete(reason="बॉट: पोस्ट पुरालेखित किया गया", prompt=False)

def modify_all_of_page(page):
    links = page.extlinks()
    orig = page.get()
    text = mwparserfromhell.parse(orig)
    
    for link in links:
        if 'wiki' in link or not link.startswith(('http', 'ftp', 'https')):
            continue
        try:
            url = citationdotorg.archive_url(link)['webcite_url']
            text = add_template(text, link, url)
        except Exception as e:
            print(f"ERROR archiving {link}: {e}")
        
        time.sleep(5)

    page.put(str(text), 'बॉट: मैनुअल परीक्षण द्वारा ऑपरेशन')

if __name__ == "__main__":
    print("Script is running...")
