import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pywikibot
from datetime import datetime, timedelta
import re
import logging
from config.settings import EMAIL_CONFIG, WIKI_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ChoupalArchiver:
    def __init__(self, dry_run=True):
        self.site = pywikibot.Site(
            WIKI_CONFIG['lang'], 
            WIKI_CONFIG['family'],
            user=WIKI_CONFIG['user']
        )
        self.dry_run = dry_run
        self.section_header_regex = re.compile(r'^(=+)(.+?)\1', re.MULTILINE)

    # [Previous methods: parse_date, split_sections, should_archive]

    def send_email(self, archived_count, archived_titles):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender']
            msg['To'] = EMAIL_CONFIG['recipient']
            msg['Subject'] = f"{EMAIL_CONFIG['subject_prefix']} Archived {archived_count} sections"
            
            body = f"""<html>
                <body>
                    <h2>चौपाल आर्काइविंग रिपोर्ट</h2>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} पर {archived_count} अनुभाग आर्काइव किए गए:</p>
                    <ul>
                        {"".join(f"<li>{title[:50]}...</li>" for title in archived_titles)}
                    </ul>
                </body>
            </html>"""
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(EMAIL_CONFIG['server'], EMAIL_CONFIG['port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
                server.send_message(msg)
            
            logging.info("Email notification sent")
        except Exception as e:
            logging.error(f"Email failed: {str(e)}")

    def run(self):
        try:
            # [Previous archiving logic]
            if not self.dry_run and archived_sections:
                self.send_email(len(archived_sections), archived_titles)
                
        except Exception as e:
            logging.error(f"Archiving failed: {str(e)}")
            self.send_email(0, [f"Archiving failed: {str(e)}"])

if __name__ == "__main__":
    archiver = ChoupalArchiver(dry_run=os.getenv('DRY_RUN', 'True') == 'True')
    archiver.run()
