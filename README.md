
# CactusismeBot
This bot automatically processes vandalism reports on Simple Wikipedia's WP:VIP page, marking `{{vandal|Username}}` reports as resolved with `{{done}}--~~~~` for blocked users/IPs.

## Installation
- Requires Python 3.x
- Install dependencies via `pip install mwclient`.

## Usage
- Replace `YourBotUsername` and `YourBotPassword` in the script.
- Run the bot to process WP:VIP reports periodically.

## Features
- Parses vandalism reports using the `{{vandal|Username}}` template.
- Logs activity locally for transparency.
