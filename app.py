from flask import Flask, request, render_template, redirect, url_for, flash
import requests
import threading
import time
import json
import os
import subprocess
import logging
from urllib import parse  # Import the parse module from urllib

app = Flask(__name__)
app.secret_key = '123123'  # Change this to a random secret key
monitored_urls = []

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1300161172963725433/hMfUBN6DIvVbvPELhxMXXg-Lmokz4ylzFCjqdTZVcfHHCB7FdRxJyaEIItxorgRwDDsP'  # Replace with your Discord webhook URL

# Configure logging
logging.basicConfig(filename='monitor.log', level=logging.INFO)

# Load URLs from file at startup
def load_urls():
    if os.path.exists('monitored_urls.json'):
        with open('monitored_urls.json', 'r') as f:
            return json.load(f)
    return []

# Save URLs to file
def save_urls():
    with open('monitored_urls.json', 'w') as f:
        json.dump(monitored_urls, f)

def send_discord_notification(message):
    data = {
        'content': message
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def log_status(url, status):
    logging.info(f"{time.ctime()}: {url} - Status: {status}")

def check_website_with_ping(url):
    try:
        hostname = url.split("//")[-1].split("/")[0]
        response = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode != 0:
            send_discord_notification(f"Website Down Alert: {url} is down (ping failed).")
            log_status(url, "Down (ping failed)")
            return False
        return True
    except Exception as e:
        send_discord_notification(f"Error checking {url} with ping: {str(e)}")
        log_status(url, f"Error (ping): {str(e)}")
        return False

def check_website_with_curl(url):
    try:
        response = subprocess.run(['curl', '-o', '/dev/null', '-s', '-w', '%{http_code}', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_code = response.stdout.decode('utf-8').strip()
        if status_code != "200":
            send_discord_notification(f"Website Down Alert: {url} returned status code {status_code}.")
            log_status(url, f"Down (status code: {status_code})")
    except Exception as e:
        send_discord_notification(f"Error checking {url} with curl: {str(e)}")
        log_status(url, f"Error (curl): {str(e)}")

def check_website(url):
    if not check_website_with_ping(url):
        return  # If ping fails, no need to check further
    check_website_with_curl(url)

def monitor_websites():
    while True:
        for url in monitored_urls:
            check_website(url)
        time.sleep(5)  # Check every minute

@app.route('/', methods=['GET', 'POST'])
def index():
    global monitored_urls
    if request.method == 'POST':
        url = request.form['url']
        if url and url not in monitored_urls:
            monitored_urls.append(url)
            save_urls()  # Save to file
            flash(f'Added {url} to monitored URLs.', 'success')
        else:
            flash('Invalid URL or already monitored.', 'danger')
        return redirect(url_for('index'))

    return render_template('index.html', monitored_urls=monitored_urls, parse=parse)  # Pass parse to template

@app.route('/remove/<path:url>')
def remove_url(url):
    global monitored_urls
    if url in monitored_urls:
        monitored_urls.remove(url)
        save_urls()  # Save changes to file
        flash(f'Removed {url} from monitored URLs.', 'success')
    else:
        flash(f'URL {url} not found.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    monitored_urls = load_urls()  # Load monitored URLs from file
    threading.Thread(target=monitor_websites, daemon=True).start()
    app.run(debug=True)
