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
        # Initialize site with bot credentials
        self.site = Site(
            code='hi',
            fam='wikiversity',
            user='CactusismeBot'  # Your bot username
        )
        self.dry_run = dry_run
        self.section_header_regex = re.compile(r'^(=+)(.+?)\1', re.MULTILINE)
        self.source_page_title = "विकिविश्वविद्यालय:चौपाल"
        self.archive_page_title = "विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)"
        self.archive_days = 60
        self.max_sections = 50

    def parse_date(self, text: str) -> datetime:
        """Improved date parsing for Hindi Wikiversity"""
        patterns = [
            r'(\d{1,2} [जनवरीफरवरीमार्चअप्रैलमईजूनजुलाईअगस्तसितंबरअक्टूबरनवंबरदिसंबर]+ \d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    if any(month in date_str for month in ["जनवरी", "फरवरी"]):
                        day, month, year = date_str.split()
                        month_num = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून",
                                    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"].index(month) + 1
                        return datetime(int(year), month_num, int(day))
                    else:
                        return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
        
        return datetime.now()

    def split_sections(self, text: str) -> list:
        """Split page text into sections"""
        sections = []
        last_end = 0
        
        for match in self.section_header_regex.finditer(text):
            header = match.group(0)
            level = len(match.group(1))
            start = match.end()
            
            next_match = self.section_header_regex.search(text[start:])
            end = start + (next_match.start() if next_match else len(text))
            
            content = text[start:end].strip()
            sections.append((header, content, level))
            last_end = end
        
        return sections[:self.max_sections]

    def should_archive(self, section_content: str) -> bool:
        """Check if section should be archived"""
        section_date = self.parse_date(section_content)
        return (datetime.now() - section_date) > timedelta(days=self.archive_days)

    def send_email(self, archived_count: int, archived_titles: list):
        """Send notification using GitHub Secrets"""
        try:
            # Get credentials from environment variables
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASSWORD')
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = 'hellomary810@gmail.com'
            msg['Subject'] = f"[CactusismeBot] Archived {archived_count} sections"
            
            body = f"""<html>
                <body>
                    <h2>चौपाल आर्काइव रिपोर्ट</h2>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M')} पर आर्काइव किए गए:</p>
                    <ul>
                        {"".join(f"<li>{title}</li>" for title in archived_titles)}
                    </ul>
                </body>
            </html>"""
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(smtp_server, 587) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            logging.info("Notification email sent")
        except Exception as e:
            logging.error(f"Email failed: {str(e)}")

    def run(self):
        """Main archiving workflow"""
        try:
            logging.info("Starting archiving process...")
            source_page = Page(self.site, self.source_page_title)
            archive_page = Page(self.site, self.archive_page_title)
            
            sections = self.split_sections(source_page.text)
            archived_sections = []
            
            for header, content, level in sections:
                if level >= 1 and self.should_archive(content):
                    archived_sections.append((header, content))
                    logging.info(f"Marked for archiving: {header.strip('= ')}")
            
            if not archived_sections:
                logging.info("No sections to archive")
                return
            
            if self.dry_run:
                logging.info(f"Dry run: Would archive {len(archived_sections)} sections")
                return
            
            # Perform archiving
            archive_content = "\n\n".join(f"{h}\n{c}" for h,c in archived_sections)
            archive_page.text += f"\n\n== {datetime.now().strftime('%Y-%m-%d')} ==\n{archive_content}"
            archive_page.save("Bot: Archived old discussions")
            
            # Update source page
            remaining_sections = [s for s in sections if (s[0],s[1]) not in archived_sections]
            source_page.text = "\n\n".join(f"{h}\n{c}" for h,c,_ in remaining_sections)
            source_page.save("Bot: Removed archived sections")
            
            self.send_email(len(archived_sections), [h.strip('= ') for h,_ in archived_sections])
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            self.send_email(0, [f"Archiving failed: {str(e)}"])
            raise

if __name__ == "__main__":
    archiver = ChoupalArchiver(dry_run=os.getenv('DRY_RUN', 'True') == 'True')
    archiver.run()
