import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Function to scrape emails from a website
def scrape_emails(url):
    try:
        print(f"\n[🔍] Scraping emails from: {url}")
        
        # Use Selenium to get the page source
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (no UI)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        page_source = driver.page_source
        driver.quit()

        # Parse the HTML
        soup = BeautifulSoup(page_source, "html.parser")
        text = soup.get_text()

        # Find all email addresses using regex
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))

        if emails:
            print(f"[✅] Extracted Emails: {emails}")
            return emails
        else:
            print("[❌] No emails found.")
            return set()

    except Exception as e:
        print(f"[⚠️] Error scraping emails: {e}")
        return set()

# Function to send an email with a custom message
def send_email(sender_email, sender_password, recipient_email, extracted_emails, custom_message):
    try:
        subject = "Extracted Emails Report"
        body = f"{custom_message}\n\nHere are the extracted emails:\n\n{', '.join(extracted_emails)}"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print("[✅] Email sent successfully!")

    except (smtplib.SMTPAuthenticationError, Exception):
        print("[❌] Authentication Error! Check your Gmail App Password.")
    except Exception as e:
        print(f"[❌] Failed to send email: {e}")

# Main execution
if __name__ == "__main__":
    website_url = input("Enter the website URL: ").strip()
    extracted_emails = scrape_emails(website_url)

    if extracted_emails:
        recipient_email = input("Enter recipient email: ").strip()
        sender_email = input("Enter your Gmail address: ").strip()
        sender_password = input("Enter your Gmail App Password: ").strip()
        custom_message = input("Enter your custom message for the email: ").strip()

        send_email(sender_email, sender_password, recipient_email, extracted_emails, custom_message)
    else:
        print("[⚠️] No emails found, so no email will be sent.")
