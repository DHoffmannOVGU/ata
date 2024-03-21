import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os
from utils import get_all_collections, get_data_from_firestore, upload_data_to_firestore, initialize_firestore_client
from components.sidebar import page_navigation
from components.columns import four_text_columns

db = initialize_firestore_client()

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Define data types and properties
properties = {
    'Kunde': str,
    'Gegenstand': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Fertigung Gesamt': float,
    'bis 90mm Einsatz': float,
    'bis 90mm Fertig': float,
    'bis 90mm Preis': float,
    'ab 100mm Einsatz': float,
    'ab 100mm Fertig': float,
    'ab 100mm Preis': float,
    'Profile Einsatz': float,
    'Profile fertig': float,
    'Profile Preis': float
}

units = {
    'Fertigung Gesamt': 'kg',
    'bis 90mm Einsatz': 'kg',
    'bis 90mm Fertig': 'kg',
    'bis 90mm Preis': '€',
    'ab 100mm Einsatz': 'kg',
    'ab 100mm Fertig': 'kg',
    'ab 100mm Preis': '€',
    'Profile Einsatz': 'kg',
    'Profile fertig': 'kg',
    'Profile Preis': '€'
}

field_mapping = {
    'Kunde': 'Kunde',
    'Gegenstand': 'Benennung',  # Note the different field name here
    'Zeichnungs- Nr.': 'Zeichnungs- Nr.',
    'Ausführen Nr.': 'Ausführen Nr.'
}

# Initialize session state for each property
if "vk_st0_data" not in st.session_state:
    st.session_state.vk_st0_data = {prop: "" for prop in properties}
# Define a key in session state to track the currently selected collection
if 'current_collection' not in st.session_state:
    st.session_state.current_collection = None
# Display a select box with all collection names
collection_names = get_all_collections(db)
# Update session state with selected collection
selected_collection = st.selectbox('Select Collection:', options=collection_names)
firestore_data = {}
details_data = {}
vk_st_0_data = {}

# Check if the selected collection has changed
if st.session_state.current_collection != selected_collection:
    st.session_state.current_collection = selected_collection

    # Clear the previous data from session state
    st.session_state.vk_st0_data = {prop: "" for prop in properties}

    # Load new data from Firestore for the selected collection
    if selected_collection:
        firestore_data = get_data_from_firestore(db, selected_collection, 'Details')
        vk_st_0_data = get_data_from_firestore(db, selected_collection, 'VK-ST-0')

        # Update session state with new data
        if firestore_data:
            for app_field, firestore_field in field_mapping.items():
                st.session_state.vk_st0_data[app_field] = firestore_data.get(firestore_field, "")

# Update session state with data from 'Details'
if details_data:
    for app_field, firestore_field in field_mapping.items():
        if app_field in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']:  # Fields from 'Details'
            st.session_state.data[app_field] = details_data.get(firestore_field, "")

# Update session state with data from 'VK-ST-0'
if vk_st_0_data:
    for prop in properties:
        if prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']:  # Remaining fields
            st.session_state.vk_st0_data[prop] = vk_st_0_data.get(prop, "")

# UI 

st.title("Material List Data")

page_navigation()

# If firestore_data is fetched, update the session state
if firestore_data:
    for app_field, firestore_field in field_mapping.items():
        # Assuming 'Gegenstand' should map to 'Benennung' in Firestore
        if app_field == 'Gegenstand':
            firestore_field = 'Benennung'
        st.session_state.vk_st0_data[app_field] = firestore_data.get(firestore_field, "")

def project_info(project_data):
    col1,  st.columns(len(project_data))
    for i, (key, value) in enumerate(project_data.items()):
        project_data_columns[i].write(f"{key}: {value}")



project_info(details_data)

col1, col2 = st.columns(2)

props_col1 = list(properties.keys())[:len(properties) // 2]
props_col2 = list(properties.keys())[len(properties) // 2:]

for prop in props_col1:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_st0_data[prop] = col1.text_input(prompt, value=st.session_state.vk_st0_data[prop]).strip()

for prop in props_col2:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_st0_data[prop] = col2.text_input(prompt, value=st.session_state.vk_st0_data[prop]).strip()

# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame([st.session_state.vk_st0_data])


# Function to download DataFrame as Excel
def download_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    return output.getvalue()


# Function to download DataFrame as JSON
def download_json(df):
    return df.to_json(orient="records")


# Provide download options
with st.expander("Download Data"):
    if st.button("Download as Excel", use_container_width=True):
        excel_data = download_excel(df)
        st.download_button("Download Excel File", excel_data, file_name="data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    if st.button("Download as JSON", use_container_width=True):
        json_data = download_json(df)
        st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json", use_container_width=True)

if st.button("Upload to Database", use_container_width=True, type="primary"):
    upload_data = {prop: st.session_state.vk_st0_data[prop] for prop in properties if
                   prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']}
    upload_data_to_firestore(db, selected_collection, 'VK-ST-0', upload_data)
