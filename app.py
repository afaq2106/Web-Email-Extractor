from flask import Flask, render_template, request, jsonify
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape emails
def scrape_emails(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, "html.parser")
        text = soup.get_text()
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))

        return list(emails) if emails else []
    except Exception as e:
        return []

# Function to send email
def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        return True
    except smtplib.SMTPAuthenticationError:
        return "Authentication Error! Check your Gmail App Password."
    except Exception as e:
        return f"Error: {e}"

# Route for homepage
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        emails = scrape_emails(url)
        return jsonify({"emails": emails})
    return render_template("index.html")

# Route to handle sending emails
@app.route("/send_email", methods=["POST"])
def email_sender():
    data = request.json
    sender_email = data["sender_email"]
    sender_password = data["sender_password"]
    recipient_email = data["recipient_email"]
    subject = data["subject"]
    message = data["message"]

    result = send_email(sender_email, sender_password, recipient_email, subject, message)
    
    if result is True:
        return jsonify({"success": True, "message": "Email sent successfully!"})
    else:
        return jsonify({"success": False, "message": result})

if __name__ == "__main__":
    app.run(debug=True)
    
