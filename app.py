import streamlit as st

# -- CONFIGURE PAGE --
st.set_page_config(page_title="Classified Chatbot", layout="centered")
st.title("🛍️ Classified Chatbot")

# -- MOCK LISTINGS --
mock_listings = [
    {
        "title": "Trek Marlin 7 Mountain Bike",
        "price": "$499",
        "location": "Toronto, ON",
        "description": "2021 model, light trail use. Includes bottle cage.",
        "image": "https://images.unsplash.com/photo-1605711089345-2f29c0b40be0?auto=format&fit=crop&w=800&q=60",
        "link": "https://www.kijiji.ca/v-mountain-bike/toronto/trek-marlin-7/1234567890"
    },
    {
        "title": "Specialized Sirrus X 2.0",
        "price": "$475",
        "location": "Etobicoke, ON",
        "description": "Lightweight hybrid commuter, frame size M.",
        "image": "https://images.unsplash.com/photo-1591012911204-31c831be1e42?auto=format&fit=crop&w=800&q=60",
        "link": "https://www.facebook.com/marketplace/item/9876543210"
    }
]

# -- USER INTERFACE --
query = st.text_input("What are you looking for? (e.g., 'bike under $500 in Toronto')")
if query:
    st.markdown(f"**You searched for:** {query}")
    st.write("### Top mock listings:")
    for item in mock_listings:
        st.image(item["image"], width=300)
        st.markdown(f"**{item['title']}** — *{item['price']}*")
        st.markdown(f"📍 {item['location']}  \n💬 {item['description']}")
        st.markdown(f"[View Listing]({item['link']})")
        st.markdown("---")
