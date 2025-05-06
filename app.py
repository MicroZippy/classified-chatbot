import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from dotenv import load_dotenv

# — Load Apify token from environment/secrets —
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

# — Streamlit setup —
st.set_page_config(page_title="Classifieds Live", layout="centered")
st.title("🛍️ Classified Aggregator (Live Kijiji + Facebook)")

# — Kijiji scraper —
def fetch_kijiji(query, max_items=5):
    q = quote_plus(query)
    url = f"https://www.kijiji.ca/b-for-sale/?search={q}&location=Toronto%2C+ON"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for card in soup.select("div.search-item")[:max_items]:
        t = card.select_one("a.title")
        p = card.select_one("div.price")
        i = card.select_one("img[src]")
        if not (t and p and i): continue
        results.append({
            "title":  t.get_text(strip=True),
            "price":  p.get_text(strip=True),
            "link":   "https://www.kijiji.ca" + t["href"],
            "image":  i["src"],
            "source": "Kijiji"
        })
    return results

# — Facebook Marketplace via Apify actor —
def fetch_facebook(query, max_items=5):
    actor_id = "apify/facebook-marketplace-scraper"
    run_url = (
        f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    )
    payload = {"searchString": query, "maxItems": max_items}
    r = requests.post(run_url, json=payload)
    r.raise_for_status()
    dataset_id = r.json().get("defaultDatasetId")
    if not dataset_id:
        return []
    ds_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_TOKEN}&format=json&clean=1"
    )
    listings = requests.get(ds_url).json()
    results = []
    for it in listings:
        results.append({
            "title":  it.get("title"),
            "price":  it.get("price"),
            "link":   it.get("url"),
            "image":  it.get("images", [None])[0],
            "source": "Facebook"
        })
    return results

# — Main UI —
query = st.text_input("Search live classifieds (e.g. 'road bike under $500')")
if query:
    st.markdown(f"**Searching for:** {query}")
    kijiji = fetch_kijiji(query)
    fb     = fetch_facebook(query)
    all_items = kijiji + fb

    if not all_items:
        st.error("No results found. Try a different search.")
    else:
        st.write(f"### {len(all_items)} listings:")
        for item in all_items:
            st.image(item["image"], width=300)
            st.markdown(
                f"**{item['title']}** — *{item['price']}*  \n_Source: {item['source']}_"
            )
            st.markdown(f"[View Listing]({item['link']})")
            st.markdown("---")

