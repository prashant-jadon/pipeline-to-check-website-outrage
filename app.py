from flask import Flask, request, render_template, redirect, url_for, flash
import requests
import threading
import time
import json
import os
import subprocess
import logging
from datetime import datetime
from urllib import parse


app = Flask(__name__)
app.secret_key = '123123'  # Change this to a secure secret key

# Globals
monitored_urls = []
url_status = {}  # Track the current status of each URL
monitoring_logs = []  # Store log of monitoring checks

# Helper functions
def load_urls():
    """Load URLs from a file at startup."""
    if os.path.exists('monitored_urls.json'):
        with open('monitored_urls.json', 'r') as f:
            return json.load(f)
    return []

def save_urls():
    """Save URLs to a file."""
    with open('monitored_urls.json', 'w') as f:
        json.dump(monitored_urls, f)

def send_discord_notification(message):
    """Send a notification to Discord webhook."""
    data = {'content': message}
    requests.post('https://discord.com/api/webhooks/1300161172963725433/hMfUBN6DIvVbvPELhxMXXg-Lmokz4ylzFCjqdTZVcfHHCB7FdRxJyaEIItxorgRwDDsP', json=data)

def log_status(url, status, response_time=None):
    """Log the status of a URL and store it for displaying in the dashboard."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "url": url,
        "status": status,
        "response_time": response_time if response_time else "N/A"
    }
    monitoring_logs.append(log_entry)
    logging.info(f"{timestamp}: {url} - Status: {status}, Response Time: {response_time} ms")

def check_website(url):
    """Check the website using ping and curl, log, and notify on failure."""
    # Check with ping
    hostname = url.split("//")[-1].split("/")[0]
    ping_response = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if ping_response.returncode != 0:
        send_discord_notification(f"Website Down Alert: {url} (Ping failed)")
        log_status(url, "Down (ping failed)")
        url_status[url] = False
        return

    # Check with curl
    curl_response = subprocess.run(['curl', '-o', '/dev/null', '-s', '-w', '%{time_total}', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if curl_response.returncode == 0:
        response_time = float(curl_response.stdout.decode('utf-8').strip()) * 1000
        log_status(url, "Up", response_time)
        url_status[url] = True
    else:
        send_discord_notification(f"Website Down Alert: {url} (Curl error)")
        log_status(url, "Down (curl error)")
        url_status[url] = False

def monitor_websites():
    """Threaded function to continuously monitor URLs."""
    while True:
        for url in monitored_urls:
            check_website(url)
        time.sleep(60)  # Run every minute

@app.route('/', methods=['GET', 'POST'])
def index():
    global monitored_urls
    if request.method == 'POST':
        url = request.form['url']
        if url and url not in monitored_urls:
            monitored_urls.append(url)
            url_status[url] = True
            save_urls()
            flash(f'Added {url} to monitored URLs.', 'success')
        else:
            flash('Invalid URL or already monitored.', 'danger')
        return redirect(url_for('index'))

    return render_template('index.html', monitored_urls=monitored_urls, url_status=url_status, monitoring_logs=monitoring_logs, parse=parse)

@app.route('/remove/<path:url>')
def remove_url(url):
    global monitored_urls
    decoded_url = parse.unquote(url)  # Decode the URL
    if decoded_url in monitored_urls:
        monitored_urls.remove(decoded_url)
        save_urls()  # Save changes to file
        flash(f'Removed {decoded_url} from monitored URLs.', 'success')
    else:
        flash(f'URL {decoded_url} not found.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    monitored_urls = load_urls()
    threading.Thread(target=monitor_websites, daemon=True).start()
    app.run(debug=True)
