import imaplib
import email
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
from io import BytesIO
import schedule

load_dotenv()
def connect_to_mail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    my_email = os.getenv("EMAIL")
    print(my_email)
    password = os.getenv("PASSWORD")
    print(password)
    mail.login(my_email, password)
    mail.select("inbox")
    status, messages = mail.search(None, f'(FROM "dailyleadsourcer@gmail.com" ON {today_date})')
    return [mail, messages]


from datetime import datetime


today = datetime.today()
today_date = datetime.today().strftime('%d-%b-%Y')
day = today.day
month = today.month
year  = today.year

print(day, month, year)

def sendWebhook(df_filtered) :
    webhook_url = os.getenv("WEBHOOK")
    footer_icon_url ="https://imgur.com/nOgw6oi.jpeg"
    for index, row in df_filtered.iterrows():
        data = {
            "embeds": [
                {
                    "title": f"{row['Product Name']}",
                    "url" : f"{row.get('Store')}",
                    "fields": [
                        {"name": "Cost", "value": str(row.get('Store Price')), "inline": False},
                        {"name": "Sale Price", "value": f"£{str(row.get('Amazon Buy Box'))}", "inline": True},
                        {"name": "Profit", "value": f"£{str(row.get('Profit (ex. VAT)'))}", "inline": True},
                        {"name": "ROI", "value": f"{round((row.get('ROI%')*100), 2)}%", "inline": False},
                        {"name": "ASIN", "value": str(row.get('Asin')), "inline": True},
                        {"name": "FBA Offers", "value": str(row.get('FBA offers')), "inline": True}
                    ],
                    "footer": {
                        "text": "Powered by Xanon",
                        "icon_url": footer_icon_url  # URL for footer icon
                    },
                    "color": 0x1A91FF,

                }
            ],
            "content" : str(row.get('Asin'))
        }
        roleid = os.getenv("ROLEID")
        ping = {"content": f"<@&{roleid}>"}
        response = requests.post(webhook_url, json=data)
        ping = requests.post(webhook_url, json=ping)
        if response.status_code == 204:

            print("Embed sent successfully.")
        else:
            print(response.text)
            print(f"Failed to send embed. Status code: {response.status_code}")
        time.sleep(600)
# Search for emails from dailyleadsourcer@gmail.com



def run():
    mail,messages = connect_to_mail()
    for num in messages[0].split():
        mail,mess = connect_to_mail()
        status, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        for part in msg.walk():
            # Check if the part is an Excel file
            if part.get_content_type() in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
                # Load the file into memory using BytesIO
                file_data = part.get_payload(decode=True)
                file_stream = BytesIO(file_data)
                
                # Read the Excel file directly from memory, assuming headers are on the 6th row
                df = pd.read_excel(file_stream, header=5)
                
                    # Filter the required columns
                df_filtered = df[['Product Name', 'Store', 'Store Price', 'Amazon Buy Box', 'Profit (ex. VAT)', 'ROI%', 'Asin', 'FBA offers']]
                
                sendWebhook(df_filtered)
                
                print("File processed")

schedule.every().monday.at("19:00").do(run)
schedule.every().tuesday.at("19:00").do(run)
schedule.every().wednesday.at("19:00").do(run)
schedule.every().thursday.at("19:00").do(run)
schedule.every().friday.at("19:00").do(run)

while True:
    schedule.run_pending()  # Check if any scheduled tasks need to run
    time.sleep(50)  # Sleep for 60 seconds to avoid excessive CPU usage
