import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os
from utils import get_all_collections, get_data_from_firestore, upload_data_to_firestore, initialize_firestore_client
from data_objects import properties, units, field_mapping

# Initialize Firestore client

db = initialize_firestore_client()

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Define data types and properties
properties = {
    'Kunde': str,
    'Gegenstand': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Brennen': float,
    'Richten': float,
    'Heften_Zussamenb_Verputzen': float,
    'Anzeichnen': float,
    'Schweißen': float,
}

firestore_data = {}

# Display a select box with all collection names
collection_names = get_all_collections(db)
selected_collection = st.selectbox('Select Collection:', options=collection_names)

# Initialize session state for each property
if "vk_0_data" not in st.session_state:
    st.session_state.vk_0_data = {prop: "" for prop in properties}

# Fetch and display the data for a known document ID ('Details') from the selected collection
if selected_collection:
    firestore_data = get_data_from_firestore(db, selected_collection, 'Details')

# Update the session state data with existing values from the Firestore database
if firestore_data:
    for prop in st.session_state.vk_0_data.keys():
        if prop in firestore_data:
            st.session_state.vk_0_data[prop] = firestore_data[prop]

col1, col2 = st.columns(2)

props_col1 = list(properties.keys())[:len(properties) // 2]
props_col2 = list(properties.keys())[len(properties) // 2:]

for prop in props_col1:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_0_data[prop] = col1.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()

for prop in props_col2:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_0_data[prop] = col2.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()

field_mapping = {
    'Kunde': 'Kunde',
    'Gegenstand': 'Benennung',
    'Zeichnungs- Nr.': 'Zeichnungs- Nr.',
    'Ausführen Nr.': 'Ausführen Nr.'
}

# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame(st.session_state.vk_0_data, index=[0])  # Specify index to create a DataFrame with one row

# Transpose the DataFrame to have each column stacked vertically
df_transposed = df.transpose()

# Download Excel and JSON
if st.button("Download Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_transposed.to_excel(writer, sheet_name='Sheet1', header=False)  # Set header to False to exclude column names
    output.seek(0)
    st.download_button("Download Excel File", output, key="download_excel", file_name="data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.button("Download JSON"):
    json_data = df.to_json(orient="records")
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

# Upload to Database
if st.button("Upload to Database"):
    # Convert session state data to the appropriate format for Firestore
    # Assuming your Firestore expects a dictionary with specific keys
    upload_data = {field_mapping.get(k, k): v for k, v in st.session_state.vk_0_data.items()}
    upload_data_to_firestore(db, selected_collection, 'VK-0', upload_data)
