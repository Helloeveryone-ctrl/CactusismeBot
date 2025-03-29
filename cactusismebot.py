import mwclient
import time

# Connect to Test Wikipedia
site = mwclient.Site('test.wikipedia.org')

# Login (replace with your test bot's username and password)
username = 'YourTestBotUsername'
password = 'YourTestBotPassword'
site.login(username, password)

def process_vip_reports():
    # Access a test page instead of WP:VIP
    page = site.pages["Wikipedia:Sandbox"]  # Change this to any test page

    try:
        # Get the text of the page
        vip_text = page.text()

        # Split into sections or lines
        lines = vip_text.split("\n")
        updated_text = []
        for line in lines:
            if "{{done}}" not in line:  # Only process entries not already marked as done
                if "{{vandal|" in line:  # Check for vandal template
                    # Extract the username or IP from the template
                    username_or_ip = extract_vandal_username(line)

                    if username_or_ip and site.users[username_or_ip].get("blockinfo"):
                        # Mark as done
                        line += " {{done}}--~~~~"
            updated_text.append(line)

        # Save changes to the test page
        page.edit("\n".join(updated_text), summary="[TEST] Marking reports as done.")
    except Exception as e:
        print(f"Error processing test page: {e}")

def extract_vandal_username(line):
    # Extract the username from the {{vandal|Username}} template
    if "{{vandal|" in line:
        start = line.index("{{vandal|") + len("{{vandal|")
        end = line.index("}}", start)
        return line[start:end].strip()
    return None

# Run the bot periodically for testing
while True:
    process_vip_reports()
    time.sleep(3)  # Run every 5 minutes

