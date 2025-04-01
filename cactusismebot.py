import time
import datetime
import re
import ceterach
#import pywikibot
import mwparserfromhell

from webcite import citationdotorg
CITE_WEB = ['cite web', 'web', 'web reference', 'web-reference', 'weblink', 'c web', 'cit web', 'cita web', 'citar web', 'cite blog', 'cite tweet',
            'cite url,', 'cite web.', 'cite webpage', 'cite website', 'cite website article', 'cite-web', 'citeweb', 'cw', 'lien web',
            'web citation', 'web cite',]
CITE_NEWS = ['cite news', 'cit news', 'cite article', 'citenewsauthor', 'cite new', 'cite news-q', 'cite news2', 'cite newspaper', 'cite-news',
              'citenews', 'cute news']
CITE_TEMPLATES = CITE_WEB
CITE_TEMPLATES.extend(CITE_NEWS)
CITE_WEB_TEMPLATE = '{{cite web|url=%s|title=%s|archiveurl=%s|archivedate=%s|deadurl=no}}'

def calculate_date(delay=None):
    #format of 31 June 2012
    now = datetime.datetime.utcnow()
    return now.strftime('%d %B %Y')

def check_archive_conditions(post_date, last_comment_date):
    # Calculate date difference for conditions
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
        if 'wiki' in link:
            continue
        if not link.startswith(('http', 'ftp', 'https')):
            continue
        url = citationdotorg.archive_url(link)['webcite_url']
        print(url)
        text = add_template(text, link, url)
        if not text:
            print('ERROR')
        text = mwparserfromhell.parse(text)
        #pywikibot.showDiff(orig, str(text))
        time.sleep(5)
    print('-----------------------')
    #pywikibot.showDiff(orig, str(text))
    page.put(str(text), 'बॉट: मैनुअल परीक्षण द्वारा ऑपरेशन')

if __name__ == "__main__":
    # Here you can add logic to fetch pages, check conditions, and call archive_page()
    pass
