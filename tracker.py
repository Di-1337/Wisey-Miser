import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Example product
url = "https://www.myntra.com/tops/some-top-id"
product_name = "Top 1"

csv_file = f"{product_name.replace(' ', '_')}.csv"

# --- scrape the price ---
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# adapt this selector depending on Myntra’s structure
price_tag = soup.find("span", {"class": "pdp-price"})  
price = None
if price_tag:
    price = price_tag.get_text(strip=True).replace("Rs. ", "").replace(",", "")
    price = int(price)

# --- log with date ---
today = datetime.today().strftime("%Y-%m-%d")

# if CSV exists, load it
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.DataFrame(columns=["Date", "Price"])

# add today’s entry if not already there
if today not in df["Date"].values:
    df = pd.concat([df, pd.DataFrame([[today, price]], columns=["Date", "Price"])])
    df.to_csv(csv_file, index=False)

print("Logged:", today, price)

# --- plot graph ---
df["Date"] = pd.to_datetime(df["Date"])
plt.figure(figsize=(8, 5))
plt.plot(df["Date"], df["Price"], marker="o", linestyle="-", label=product_name)

# annotate prices
for i, row in df.iterrows():
    plt.text(row["Date"], row["Price"], str(row["Price"]), ha="center", va="bottom")

plt.xlabel("Date")
plt.ylabel("Price (Rs.)")
plt.title(f"Price Tracker for {product_name}")
plt.legend()
plt.grid(True)
plt.show()