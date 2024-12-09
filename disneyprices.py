import requests
import datetime
import csv


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }

disney_url = 'https://disneycruise.disney.go.com/dcl-apps-productavail-vas/authz/private'

response = requests.post(disney_url, headers=headers, json={})

cookies = response.cookies

url = 'https://disneycruise.disney.go.com/dcl-apps-productavail-vas/available-products/'

payload = {
    "currency": "USD",
    "filters": ["disney-adventure;filterId=urlFriendlyId"],
    "affiliations": [],
    "exploreMorePage": 1,
    "exploreMorePageHistory": False,
    "includeAdvancedBookingPrices": True,
    "page": 1,
    "pageHistory": False,
    "partyMix": [
        {
            "accessible": False,
            "adultCount": 2,
            "childCount": 0,
            "nonAdultAges": [],
            "partyMixId": "0"
        }
    ],
    "region": "INTL",
    "storeId": "DCL"
}


#remove the accept-encoding:gzip, deflate, br, zstd

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-us",
    "content-length": "337",
    "content-type": "application/json",
    "origin": "https://disneycruise.disney.go.com",
    "priority": "u=1, i",
    "referer": "https://disneycruise.disney.go.com/cruises-destinations/list/",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

response = requests.post(url, cookies=cookies, headers=headers, json=payload)

#next steps: post a request to the URL with the breakdown of actual prices in a for loop for each product type

url_1 = 'https://disneycruise.disney.go.com/dcl-apps-productavail-vas/available-sailings/'

if response.status_code == 200:
    data = response.json()
    product_names = [item.get('productId') for item in data.get('products', [])]
    data_export = []
    for name in product_names:
        payload_1 = {
            "currency": "USD",
    "filters": [],
    "affiliations": [],
    "includeAdvancedBookingPrices": True,
    "itineraryId": "",
    "partyMix": [
        {
            "accessible": False,
            "adultCount": 2,
            "childCount": 0,
            "nonAdultAges": [],
            "partyMixId": "0"
        }
    ],
    "0": {
        "accessible": False,
        "adultCount": 2,
        "childCount": 0,
        "nonAdultAges": [],
        "partyMixId": "0"
    },
    "productId": name,
    "region": "INTL",
    "storeId": "DCL"
        }
        response_1 = requests.post(url_1, cookies=cookies, headers=headers, json=payload_1)
        data_1=response_1.json()

        for sailings in data_1["sailings"]:
          sailing_id = sailings["sailingId"]
          cruise_name = sailings.get('ship',{}).get('name', {})
          departure_date = sailings["sailDateFrom"]
          arrival_date = sailings["sailDateTo"]
          travel_parties = sailings.get('travelParties', {})

          # Iterate through the elements of "travelParties"
          for party in travel_parties.get('0', []):
              stateroom_sub_type = party.get('stateroomSubType', '')
              total = party.get('price', {}).get('summary', {}).get('total', 0.0)

              # Print the extracted information
              data_export.append([sailing_id, cruise_name, departure_date, arrival_date, stateroom_sub_type, total])

data_export.insert(0, ['Sailing_ID', 'Cruise_name', 'Sail_date', 'Return_date', 'Room_type','Price'])


current_date = datetime.datetime.now().strftime('%Y-%m-%d')
file_name = f'disney_cruise_prices_{current_date}.csv'
with open(file_name, mode='w', newline='') as file:
  writer = csv.writer(file)
  for row in data_export:
    writer.writerow(row)


import os
import smtplib
from email.message import EmailMessage
import csv

# Email configuration
sender_email = "tnchhk@gmail.com"
receiver_email = "tnchhk@gmail.com; timothy_ng@cathaypacific.com"
subject = "Daily Disney Cruise Prices"
body = "Please find attached the daily Disney Cruise prices."

# Attach the CSV file to the email
file_name = f'disney_cruise_prices_{current_date}.csv'
attachment_path = os.path.abspath(file_name)

msg = EmailMessage()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.set_content(body)

with open(attachment_path, 'rb') as file:
    attachment_data = file.read()
    msg.add_attachment(attachment_data, maintype='application', subtype='csv', filename=file_name)

# Send the email
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "email"
smtp_password = "password"

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)

print("Email sent successfully.")
