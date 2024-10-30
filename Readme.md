# Website Monitor

### A simple web application for monitoring website status using Flask, with notifications sent to a Discord webhook in case of downtime or issues. This project is designed for Linux environments and utilizes ping and curl commands to check website availability.

Features

- Add and remove websites to be monitored for uptime.
- Ping and HTTP status checks to verify website health.
- Discord notifications when a website is down or inaccessible.
- Automatic logging of website status.

Prerequisites
```
Python 3.x
Flask
curl and ping (installed by default on most Linux distributions)
Internet access for Discord notifications
```

Installation
Clone the Repository
```
git clone https://github.com/your-username/website-monitor.git
cd website-monitor
```

Install Required Packages
```
pip install -r requirements.txt
```
Set Up the Discord Webhook
Replace DISCORD_WEBHOOK_URL in app.py with your Discord webhook URL.

Run the Application
```
python app.py
```

Usage

Add URLs to monitor by entering them on the main page.
View Monitored URLs in the list on the dashboard.
Remove URLs from monitoring as needed.

or you can use amidown.sh 
```
chmod +x amidown.sh
./amidown.sh [subdomain].txt

Monitoring
The application continuously checks the listed websites' availability every 5 seconds, sending notifications to Discord if any site becomes inaccessible.

Project Structure

```
website-monitor/
├── app.py               # Main application code
├── templates/
│   └── index.html       # HTML file for the main dashboard
├── requirements.txt     # Required Python packages
├── monitor.log          # Log file (generated after running the app)
└── monitored_urls.json  # Stores URLs being monitored
```

Contributions are welcome! 

