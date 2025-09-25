from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import time

products = {
    "Top1": "https://www.myntra.com/35035821",
    "Top2": "https://www.myntra.com/35662540"
}

data = []

# Setup Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for name, url in products.items():
    driver.get(url)
    time.sleep(5)  # wait for page to load
    
    try:
        # Myntra price element (check page, might need update)
        price_tag = driver.find_element(By.CLASS_NAME, "pdp-price")
        price = int(price_tag.text.strip().replace("₹","").replace(",",""))
        data.append([datetime.now().date(), name, price])
        print(name, price)
    except:
        print("Price not found for", name)

driver.quit()

# Save to CSV
df = pd.DataFrame(data, columns=["Date", "Product", "Price"])
try:
    old_df = pd.read_csv("price_data.csv")
    df = pd.concat([old_df, df], ignore_index=True)
except FileNotFoundError:
    pass

df.to_csv("price_data.csv", index=False)

# Plot price trends
for product in products.keys():
    product_data = df[df["Product"] == product]
    plt.plot(product_data["Date"], product_data["Price"], marker="o", label=product)

plt.xlabel("Date")
plt.ylabel("Price (₹)")
plt.title("Price Tracker")
plt.legend()
plt.xticks(rotation=45)
plt.show()