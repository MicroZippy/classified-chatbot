import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from dotenv import load_dotenv

# — Load your Apify token from Secrets —
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

# — Streamlit setup —
st.set_page_config(page_title="Classified Aggregator", layout="centered")
st.title("🛍️ Classifieds Live")

# — Kijiji scraper function —
def fetch_kijiji(query, max_items=5):
    q = quote_plus(query)
    url = f"https://www.kijiji.ca/b-for-sale/?search={q}&location=Toronto%2C+ON"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for card in soup.select("div.search-item")[:max_items]:
        title_tag = card.select_one("a.title")
        price_tag = card.select_one("div.price")
        img_tag   = card.select_one("img[src]")
        if not (title_tag and price_tag and img_tag):
            continue
        results.append({
            "title":  title_tag.get_text(strip=True),
            "price":  price_tag.get_text(strip=True),
            "link":   "https://www.kijiji.ca" + title_tag["href"],
            "image":  img_tag["src"],
            "source": "Kijiji"
        })
    return results

# — Facebook Marketplace via Apify with error handling —
def fetch_facebook(query, max_items=5):
    actor_id = "apify/facebook-marketplace-scraper"
    token    = APIFY_TOKEN
    run_url  = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={token}"

    # Debug info (appears in your Streamlit logs)
    st.write("APIFY_TOKEN:", token)
    st.write("Run URL:", run_url)

    try:
        r = requests.post(run_url, json={"searchString": query, "maxItems": max_items})
        r.raise_for_status()
        dataset_id = r.json().get("defaultDatasetId")
        if not dataset_id:
            st.warning("⚠️ No dataset returned from Apify run.")
            return []
        ds_url = (
            f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            f"?token={token}&format=json&clean=1"
        )
        items = requests.get(ds_url).json()
        results = []
        for it in items:
            results.append({
                "title":  it.get("title"),
                "price":  it.get("price"),
                "link":   it.get("url"),
                "image":  it.get("images", [None])[0],
                "source": "Facebook"
            })
        return results
    except Exception as e:
        st.error(f"⚠️ Facebook fetch failed: {e}")
        return []

# — Main app flow —
query = st.text_input("Search classifieds (e.g. 'road bike under $500')")

if query:
    st.markdown(f"**Searching for:** {query}")

    kijiji_results   = fetch_kijiji(query)
    facebook_results = fetch_facebook(query)
    all_items        = kijiji_results + facebook_results

    if not all_items:
        st.error("No listings found. Try another search.")
    else:
        st.write(f"### Found {len(all_items)} listings:")
        for item in all_items:
            st.image(item["image"], width=300)
            st.markdown(
                f"**{item['title']}** — *{item['price']}*  \n"
                f"_Source: {item['source']}_"
            )
            st.markdown(f"[View Listing]({item['link']})")
            st.markdown("---")
