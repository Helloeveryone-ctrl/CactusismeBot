import mwclient
import time

# Connect to Test Wikipedia
site = mwclient.Site('test.wikipedia.org')

# Login (replace with your test bot's username and password)
USERNAME = CactusismeBot
PASSWORD = Temporarybotpassword

try:
    site.login(USERNAME, PASSWORD)
    print("Logged in successfully.")
except mwclient.LoginError as e:
    print(f"Login failed: {e}")
    exit(1)

def extract_vandal_username(line):
    """Extract the username or IP from the {{vandal|Username}} template."""
    if "{{vandal|" in line and "}}" in line:
        start = line.index("{{vandal|") + len("{{vandal|")
        end = line.index("}}", start)
        return line[start:end].strip()
    return None

def process_vip_reports():
    """Processes reports on User:Cactusisme/WP:VIP and marks blocked vandals as done."""
    page = site.pages["User:Cactusisme/WP:VIP"]  # Target page for testing

    try:
        # Get the text of the page
        vip_text = page.text()

        # Split into sections or lines
        lines = vip_text.split("\n")
        updated_text = []
        changes_made = False

        for line in lines:
            if "{{done}}" not in line and "{{vandal|" in line:
                vandal_username = extract_vandal_username(line)

                if vandal_username:
                    user_info = site.users[vandal_username]

                    if user_info.get("blockinfo"):  # Locally blocked
                        line += " {{done}}--~~~~"
                        changes_made = True
                        print(f"Marked {vandal_username} as done (Blocked).")

            updated_text.append(line)

        # Save changes to the target page if there are updates
        if changes_made:
            page.edit("\n".join(updated_text), summary="[TEST] Marking reports as done.")
            print("Updated User:Cactusisme/WP:VIP successfully.")
        else:
            print("No changes needed on User:Cactusisme/WP:VIP.")

    except Exception as e:
        print(f"Error processing User:Cactusisme/WP:VIP: {e}")

# Run the bot periodically for testing
while True:
    process_vip_reports()
    time.sleep(3)  # Run every 3 seconds for testing purposes

