import streamlit as st
import streamlit_antd_components as sac

from PIL import Image
image = Image.open('logo_ata.png')

def page_navigation():
    apps = {
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",
        "ATA-Dashboard-App": "https://ata-dashboard-app.streamlit.app/"
    }
    subpage_list = []
    for app_name, app_url in apps.items():
        subpage_list.append(sac.MenuItem(app_name, icon="project", href=app_url))
        
    print(subpage_list)

    with st.sidebar:
        st.image(image, caption='Ata Logo')
        sac.menu(items = [sac.MenuItem("App navigation", type="group",  children=subpage_list)], index=1)  