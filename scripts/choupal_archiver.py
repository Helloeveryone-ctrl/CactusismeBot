import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import re
import logging
from pywikibot import Site, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ChoupalArchiver:
    def __init__(self, dry_run=True):
        # Initialize site with explicit credentials
        self.site = Site(
            code='hi',
            fam='wikiversity',
            user='CactusismeBot'  #Replace with your actual bot username
        )
        self.dry_run = dry_run
        self.section_header_regex = re.compile(r'^(=+)(.+?)\1', re.MULTILINE)
        self.source_page_title = "विकिविश्वविद्यालय:चौपाल"
        self.archive_page_title = "विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)"
        self.archive_days = 30

    def parse_date(self, text: str) -> datetime:
        """Extract date from section text"""
        # Simplified date parsing - customize as needed
        try:
            date_str = re.search(r'\d{4}-\d{2}-\d{2}', text).group()
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (AttributeError, ValueError):
            return datetime.now()

    def split_sections(self, text: str) -> list:
        """Split page text into sections"""
        return [(m.group(0), m.group(2), len(m.group(1))) 
               for m in self.section_header_regex.finditer(text)]

    def should_archive(self, section_content: str) -> bool:
        """Determine if section should be archived"""
        section_date = self.parse_date(section_content)
        return (datetime.now() - section_date) > timedelta(days=self.archive_days)

    def send_email(self, archived_count: int, archived_titles: list):
        """Send notification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = 'your_email@gmail.com'
            msg['To'] = 'hellomary810@gmail.com'
            msg['Subject'] = f"Archived {archived_count} sections"
            
            body = f"Archived sections:\n" + "\n".join(archived_titles)
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('your_email@gmail.com', 'your_app_password')
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Email failed: {str(e)}")

    def run(self):
        """Main execution method"""
        try:
            logging.info("Starting archive process...")
            
            # Load pages
            source_page = Page(self.site, self.source_page_title)
            archive_page = Page(self.site, self.archive_page_title)
            
            # Process sections
            sections = self.split_sections(source_page.text)
            archived_sections = []
            
            for header, content, level in sections:
                if level >= 2 and self.should_archive(content):
                    archived_sections.append((header, content))
                    logging.info(f"Marked for archiving: {header[:50]}...")
            
            if not archived_sections:
                logging.info("No sections to archive.")
                return
            
            # Dry run check
            if self.dry_run:
                logging.info(f"Dry run: Would archive {len(archived_sections)} sections")
                return
            
            # Perform actual archiving
            # ... (add your archiving logic here)
            
            logging.info(f"Successfully archived {len(archived_sections)} sections")
            self.send_email(len(archived_sections), [h for h, _ in archived_sections])
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise

if __name__ == "__main__":
    archiver = ChoupalArchiver(dry_run=os.getenv('DRY_RUN', 'True') == 'True')
    archiver.run()
