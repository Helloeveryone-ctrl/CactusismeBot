import os

WIKI_CONFIG = {
    'lang': 'hi',
    'family': 'wikiversity',
    'source_page': 'विकिविश्वविद्यालय:चौपाल',
    'archive_page': 'विकिविश्वविद्यालय:चौपाल आर्काइव्स (निर्माण-2025)',
    'user': os.getenv('WIKI_USERNAME'),
    'archive_days': 30
}

EMAIL_CONFIG = {
    'server': os.getenv('SMTP_SERVER'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'sender': os.getenv('SMTP_USER'),
    'password': os.getenv('SMTP_PASSWORD'),
    'recipient': 'galvin_gromit@students.edu.org',
    'subject_prefix': '[WikiBot]'
}
