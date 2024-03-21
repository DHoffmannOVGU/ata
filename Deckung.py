import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from VK_ST_0 import get_all_collections, get_data_from_firestore, field_mapping, upload_data_to_firestore
from data_objects import deckung_properties

# Initialize Firestore client
# key_dict = st.secrets["textkey"]
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds)

db = firestore.Client.from_service_account_json("ata-firestore-key.json")



# # st.set_page_config(layout="wide")
image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo')


# Upload image
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])


# Function to safely convert a value to float
def try_convert_to_float(value, default=0.0):
    try:
        return float(value) if value else default
    except ValueError:
        return default








vk_st_0_field_mapping = {
    "Gewicht": "Fertigung Gesamt"
}


material_cost_field_mapping = {
    "bis 90mm Einsatz": ("0 – 80mm", "Calculated Weight(Kg)"),
    "bis 90mm Fertig": ("0 – 80mm", "Delivery Weight(Kg)"),
    "bis 90mm Preis": ("0 – 80mm", "Price(€)"),
    "ab 100mm Einsatz": ("80 – 170mm", "Calculated Weight(Kg)"),
    "ab 100mm Fertig": ("80 – 170mm", "Delivery Weight(Kg)"),
    "ab 100mm Preis": ("80 – 170mm", "Price(€)"),
    "Profile Einsatz": ("Profile, Rohre etc.", "Calculated Weight(Kg)"),
    "Profile fertig": ("Profile, Rohre etc.", "Delivery Weight(Kg)"),
    "Profile Preis": ("Profile, Rohre etc.", "Price(€)")
}


# Initialize session state for each property
if "deckung_data" not in st.session_state:
    st.session_state.deckung_data = {prop: "" for prop in deckung_properties}


if 'Material' not in st.session_state:
    # Initialize 'df' with an empty DataFrame or default values if not in session state
    st.session_state['Material'] = pd.DataFrame(
        index=["0 – 80mm", "80 – 170mm", "Profile, Rohre etc.", "Schrauben, Schild", "Zuschlag", "Total"],
        columns=["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)", "Price per Kg(€/Kg)"]
    ).to_dict(orient='index')


# Initialize session state for Erlös, Deckungsbeitrag, and DB if not already initialized
if "Erlös" not in st.session_state:
    st.session_state.erlos = 0.0


if "Deckungsbeitrag" not in st.session_state:
    st.session_state.deckungsbeitrag = 0.0


if "DB (%)" not in st.session_state:
    st.session_state.db_percentage = 0.0


# Now 'df' is defined from the session state
df = pd.DataFrame.from_dict(st.session_state['Material']).transpose()

if 'total_material_cost' not in st.session_state:
    st.session_state['total_material_cost'] = 0.0


if 'current_collection' not in st.session_state:
    st.session_state.current_collection = None


collection_names = get_all_collections(db)
selected_collection = st.selectbox('Select Collection:', options=collection_names, key="Deckung")


if st.session_state.current_collection != selected_collection:
    st.session_state.current_collection = selected_collection
    st.session_state['deckung_data'] = {prop: "" for prop in deckung_properties}  # Reset deckung_data
    st.session_state.erlos = 0.0  # Reset to default or fetch new value
    st.session_state.deckungsbeitrag = 0.0  # Reset to default or fetch new value
    st.session_state.db_percentage = 0.0  # Reset to default or fetch new value
    # Load new data from Firestore for the selected collection
    if selected_collection:
        existing_deckung_data = get_data_from_firestore(db, selected_collection, 'Deckung')
        if existing_deckung_data:
            # Update session state with existing data
            for key, value in existing_deckung_data.items():
                if key in st.session_state.deckung_data:
                    st.session_state.deckung_data[key] = value
                    # st.write(f"{key}: {value}")
            # st.write("Debug - Updated Session State:", st.session_state.deckung_data)
        details_data = get_data_from_firestore(db, selected_collection, 'Details')
        if details_data:
            for app_field, firestore_field in field_mapping.items():
                st.session_state.deckung_data[app_field] = details_data.get(firestore_field, "")
        vk_st_0_data = get_data_from_firestore(db, selected_collection, 'VK-ST-0')
        if vk_st_0_data:
            for app_field, firestore_field in vk_st_0_field_mapping.items():
                st.session_state.deckung_data[app_field] = vk_st_0_data.get(firestore_field, "")
            for firestore_field, (row_index, column_name) in material_cost_field_mapping.items():
                if firestore_field in vk_st_0_data:
                    value = float(vk_st_0_data[firestore_field]) if vk_st_0_data[firestore_field] else 0.0
                    df.at[row_index, column_name] = value
            st.session_state['Material'] = df.to_dict(orient="index")
        try:
            deckungsbeitrag_data = get_data_from_firestore(db, selected_collection, 'Deckung')

            if deckungsbeitrag_data:
                # Safely convert to float, default to 0.0 if conversion fails
                st.session_state.erlos = try_convert_to_float(deckungsbeitrag_data.get('Erlös', 0.0))
                st.session_state.deckungsbeitrag = try_convert_to_float(
                    deckungsbeitrag_data.get('Deckungsbeitrag', 0.0))
                # Debugging
                st.write("Deckungsbeitrag from DB:", st.session_state.deckungsbeitrag)
                st.session_state.db_percentage = try_convert_to_float(deckungsbeitrag_data.get('DB (%)', 0.0))
            else:
                st.write("No data found for the selected collection.")

            # Debugging: Display the fetched data
            st.write("Fetched Data:", deckungsbeitrag_data)

        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")


st.write("Current Selection:", selected_collection)
st.write("Session State Collection:", st.session_state.current_collection)

st.title("Deckung")

# Project Details Expander
with st.expander("Project Details"):
    for prop in ['Kunde', 'Benennung', 'Zeichnungs- Nr.', 'Ausführen Nr.']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()


# Product Details Expander
with st.expander("Product Details"):
    for prop in ['Gewicht', 'Material Kosten']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        if prop == 'Material Kosten':
            # Default to the stored total cost if available, otherwise use the current value
            default_value = st.session_state.get('total_material_cost', float(st.session_state.deckung_data[prop]) if
            st.session_state.deckung_data[prop] else 0.0)
            st.session_state.deckung_data[prop] = st.number_input(prompt, value=default_value, step=0.1)
        elif deckung_properties[prop] == float:
            current_value = float(st.session_state.deckung_data[prop]) if st.session_state.deckung_data[prop] else 0.0
            st.session_state.deckung_data[prop] = st.number_input(prompt, value=current_value, step=0.1)
        else:
            st.session_state.deckung_data[prop] = st.text_input(prompt,
                                                                value=st.session_state.deckung_data[prop]).strip()


with st.expander("Material Cost Details"):
    # Display the DataFrame using Streamlit's dataframe function
    st.dataframe(df)

    if st.button('Calculate Totals', key="Calculate_Totals"):
        df = pd.DataFrame.from_dict(st.session_state['Material']).transpose()

        # Convert the DataFrame columns to numeric values where possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        # Compute the total for each column (excluding "Price per kg") and update the "Total" row values
        df.loc["Total", ["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)"]] = df.loc[
                                                                                        :"Zuschlag",
                                                                                        ["Calculated Weight(Kg)",
                                                                                         "Delivery Weight(Kg)",
                                                                                         "Price(€)"]].sum()
        # Update the session state with the edited DataFrame
        st.session_state['Material'] = df.to_dict(orient="index")

        # Store the total material cost in session state
        st.session_state['total_material_cost'] = df.loc["Total", "Price(€)"]

        # Update the "Material Kosten" in "Product Details" if it's already been rendered
        if 'Material Kosten' in st.session_state.deckung_data:
            st.session_state.deckung_data['Material Kosten'] = st.session_state['total_material_cost']


with st.expander("Deckungsbeitrag"):
    # Input fields
    # st.session_state.erlos = float(st.session_state.erlos) if st.session_state.erlos else 0.0
    st.session_state.erlos = st.number_input("Erlös", value=st.session_state.erlos)
    # st.session_state.db_percentage = float(st.session_state.db_percentage) if st.session_state.db_percentage else 0.0
    st.session_state.db_percentage = st.number_input("DB (%)", value=st.session_state.db_percentage, step=0.01)
    # st.session_state.deckungsbeitrag = float(st.session_state.deckungsbeitrag) if st.session_state.deckungsbeitrag
    # else 0.0
    st.session_state.deckungsbeitrag = st.number_input("Deckungsbeitrag", value=st.session_state.deckungsbeitrag)
    st.write("Deckungsbeitrag in UI:", st.session_state.deckungsbeitrag)


# Gesamtstuden expander
with st.expander("Gesamtstuden"):
    for prop in ['Brennen', 'Schlossern', 'Schweißen', 'sonstiges (Eur/hour)', 'sonstiges (hour)']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()


# Grenzkosten expander
with st.expander("Grenzkosten"):
    for prop in ['Prüfen , Doku', 'Strahlen / Streichen', 'techn. Bearb.', 'mech. Vorbearb.', 'mech. Bearbeitung',
                 'Zwischentransporte', 'transporte']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()


# Combine data for downloads
combined_data = {
    **st.session_state.deckung_data,  # Project and Product Details
    **st.session_state['Material'],  # Material Cost Details
    'Erlös': st.session_state.erlos,
    'DB (%)': st.session_state.db_percentage,
    'Deckungsbeitrag': st.session_state.deckungsbeitrag,
}

# Convert the combined data to a pandas DataFrame
df = pd.DataFrame([combined_data])

# Add a button to download the data as Excel
if st.button("Download as Excel", key="Deckung_Excel"):
    # Convert relevant values to numeric types
    hourly_rate = pd.to_numeric(st.session_state.deckung_data['sonstiges (Eur/hour)'], errors='coerce')
    hours = pd.to_numeric(st.session_state.deckung_data['sonstiges (hour)'], errors='coerce')
    # Create a dictionary with the data
    data_dict = {
        'Kunde': st.session_state.deckung_data['Kunde'],
        'Benennung': st.session_state.deckung_data['Benennung'],
        'Anfr. Nr.': st.session_state.deckung_data['Zeichnungs- Nr.'],
        'Gewicht': st.session_state.deckung_data['Gewicht'],
        'Material': st.session_state.deckung_data['Material Kosten'],
        'Brennen': st.session_state.deckung_data['Brennen'],
        'Schlossern': st.session_state.deckung_data['Schlossern'],
        'Schweißen': st.session_state.deckung_data['Schweißen'],
        'sonstiges': hourly_rate * hours,
        'Gesamtstunden': (
                st.session_state.deckung_data['Brennen'] +
                st.session_state.deckung_data['Schlossern'] +
                st.session_state.deckung_data['Schweißen'] +
                st.session_state.deckung_data['sonstiges (hour)'] +
                st.session_state.deckung_data['sonstiges (Eur/hour)']
        ),
        'Stunden / Tonne': 0 if st.session_state.deckung_data['Gewicht'] == 0 else st.session_state.deckung_data[
                                                                                       'Gesamtstunden'] /
                                                                                   st.session_state.deckung_data[
                                                                                       'Gewicht'],
        'Fertigung EUR': (
                st.session_state.deckung_data['Brennen'] +
                st.session_state.deckung_data['Schlossern'] +
                st.session_state.deckung_data['Schweißen'] +
                st.session_state.deckung_data['sonstiges (hour)'] +
                st.session_state.deckung_data['sonstiges (Eur/hour)']
        ),
        'Glühen': 0,
        'Prüfen , Doku': st.session_state.deckung_data['Prüfen , Doku'],
        'Strahlen / Streichen': st.session_state.deckung_data['Strahlen / Streichen'],
        'techn. Bearb.': st.session_state.deckung_data['techn. Bearb.'],
        'mech. Vorbearb.': st.session_state.deckung_data['mech. Vorbearb.'],
        'mech. Bearbeitung': st.session_state.deckung_data['mech. Bearbeitung'],
        'Zwischentransporte': st.session_state.deckung_data['Zwischentransporte'],
        'Transporte': st.session_state.deckung_data['transporte'],
        'Grenzkosten': (
                st.session_state.deckung_data['Prüfen , Doku'] +
                st.session_state.deckung_data['Strahlen / Streichen'] +
                st.session_state.deckung_data['techn. Bearb.'] +
                st.session_state.deckung_data['mech. Vorbearb.'] +
                st.session_state.deckung_data['mech. Bearbeitung'] +
                st.session_state.deckung_data['Zwischentransporte'] +
                st.session_state.deckung_data['transporte']
        ),
        'Erlös': st.session_state.erlos,
        'DB': st.session_state.deckungsbeitrag,
        'Soll 10%': st.session_state.erlos * 0.1,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag
    }
    data_dict.update({
        'Erlös': st.session_state.erlos,
        'DB (%)': st.session_state.db_percentage,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag,
        'Soll 10%': st.session_state.erlos * 0.1
    })

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame([data_dict])
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.T.to_excel(writer, sheet_name='user_data', header=False)
    excel_file.seek(0)

    # Download the Excel file using st.download_button
    st.download_button(label="Click here to download the Excel file", key="download_excel", data=excel_file,
                       file_name="user_data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Add a button to download the data as JSON
if st.button("Download as JSON", key="Deckung_json"):
    # Convert the DataFrame to JSON
    json_data = df.to_json(orient="records")

    # Download the JSON file using st.download_button
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

if st.button("Upload to Database", key="upload_to_db"):
    # Prepare the data to upload
    combined_data_to_upload = {
        **st.session_state.deckung_data,  # Project and Product Details
        **st.session_state['Material'],  # Material Cost Details
        'Erlös': st.session_state.erlos,
        'DB (%)': st.session_state.db_percentage,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag
    }

    # Call the function to upload data to Firestore
    try:
        upload_data_to_firestore(db, selected_collection, "Deckung", combined_data_to_upload)

    except Exception as e:
        st.error(f"An error occurred: {e}")
