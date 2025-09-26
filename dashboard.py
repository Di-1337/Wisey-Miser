import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import requests
import json

st.set_page_config(page_title="Wisey Miser", layout="wide")
st.title("👗 Wisey Miser - Price Tracker")

# --- Setup ---
products_file = "products.csv"
history_folder = "history"
os.makedirs(history_folder, exist_ok=True)

# Load existing products
if os.path.exists(products_file):
    try:
        products_df = pd.read_csv(products_file)
    except pd.errors.EmptyDataError:
        products_df = pd.DataFrame(columns=["Name", "URL", "ImageURL"])
else:
    products_df = pd.DataFrame(columns=["Name", "URL", "ImageURL"])

# --- Functions ---
def get_product_id(url):
    """Extract product ID from Myntra URL"""
    return url.rstrip('/').split('/')[-1]

def fetch_product_data(product_id):
    """Fetch product data from Myntra JSON API"""
    api_url = f"https://www.myntra.com/productpage/v3/{product_id}?appVersion=1.0.0&analytics=true"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def extract_product_details(json_data):
    """Get title, price, image URL from JSON"""
    try:
        product = json_data['product']
        title = product['name']
        price = product['price']['finalPrice']
        image_url = product['media']['imageUrls'][0]
        return title, price, image_url
    except KeyError:
        return None, None, None

# --- Input multiple product links ---
urls_input = st.text_area("Paste one or more Myntra product links (one per line):")
urls_list = [url.strip() for url in urls_input.split("\n") if url.strip()]

if st.button("Add / Update Products"):
    for url_input in urls_list:
        product_id = get_product_id(url_input)
        json_data = fetch_product_data(product_id)
        if json_data:
            title, price, img_url = extract_product_details(json_data)
            
            # --- Update products.csv ---
            if title not in products_df["Name"].values:
                products_df = pd.concat(
                    [products_df, pd.DataFrame([[title, url_input, img_url]], columns=products_df.columns)]
                )
                products_df.to_csv(products_file, index=False)
            
            # --- Save history ---
            hist_file = os.path.join(history_folder, f"{title.replace(' ', '_')}.csv")
            today = datetime.today().strftime("%Y-%m-%d")
            if os.path.exists(hist_file):
                df_hist = pd.read_csv(hist_file)
            else:
                df_hist = pd.DataFrame(columns=["Date","Price"])
            if today not in df_hist["Date"].values:
                df_hist = pd.concat([df_hist, pd.DataFrame([[today, price]], columns=df_hist.columns)])
                df_hist.to_csv(hist_file, index=False)
            
            st.success(f"✅ {title} added/updated with price ₹{price}")
        else:
            st.error(f"❌ Failed to fetch data for {url_input}")

# --- Display products ---
st.subheader("Tracked Products")
for _, row in products_df.iterrows():
    name, url, img_url = row
    hist_file = os.path.join(history_folder, f"{name.replace(' ', '_')}.csv")

    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if img_url and str(img_url).startswith("http"):
                st.image(img_url, width=120)
            else:
                st.write("No image available")

        with cols[1]:
            st.subheader(name)
            if os.path.exists(hist_file):
                df_hist = pd.read_csv(hist_file)
                latest_price = df_hist.iloc[-1]["Price"]
                st.write(f"**Latest Price:** ₹{latest_price}")
            st.markdown(f"[View Product]({url})")

            if st.button(f"📈 Show graph for {name}", key=name):
                if os.path.exists(hist_file):
                    df_hist = pd.read_csv(hist_file)
                    df_hist["Date"] = pd.to_datetime(df_hist["Date"])
                    fig, ax = plt.subplots()
                    ax.plot(df_hist["Date"], df_hist["Price"], marker="o", linestyle="-")
                    for i, row_hist in df_hist.iterrows():
                        ax.text(row_hist["Date"], row_hist["Price"], str(row_hist["Price"]), ha="center", va="bottom")
                    ax.set_title(f"Price Trend for {name}")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price (₹)")
                    st.pyplot(fig)