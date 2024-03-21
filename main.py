import streamlit as st
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from components.sidebar import page_navigation
from components.columns import two_text_columns
from utils import initialize_firestore_client
from data_objects import deckung_properties, vk_st0_data, vk0_data, customers

# Initialize session state data if it doesn't exist
if 'main_data' not in st.session_state:
    st.session_state.main_data = {}

# Initialize Firestore client

db = initialize_firestore_client()

# Function to instantiate a new project and save it to Firestore
def instantiate_project(kunde, benennung, zeichnungs_nr, ausfuehren_nr, db):
    doc_ref = db.collection(zeichnungs_nr).document('Details')
    doc = doc_ref.get()
    if doc.exists:
        #print(f"A project with Zeichnungs Nr {zeichnungs_nr} already exists.")
        return False
    else:
        project_data = {
            "Kunde": kunde,
            "Benennung": benennung,
            "Ausführen Nr": ausfuehren_nr,
            "Zeichnungs- Nr.": zeichnungs_nr
        }
        doc_ref.set(project_data)
        #print(f"Project with Zeichnungs Nr {zeichnungs_nr} created successfully.")

        vk_st0_doc_ref = db.collection(zeichnungs_nr).document('VK-ST-0')
        vk_st0_doc_ref.set(vk_st0_data)
        st.success("'VK-ST-0' document created successfully.")

        # Create VK-0 document and add to Firebase
        vk0_doc_ref = db.collection(zeichnungs_nr).document('VK-0')
        vk0_doc_ref.set(vk0_data)
        st.success("'VK-0' document created successfully.")

        # Create Deckung document and add to Firebase
        deckung_doc_ref = db.collection(zeichnungs_nr).document('Deckung')
        deckung_data = {prop: 0 for prop in deckung_properties}
        deckung_doc_ref.set(deckung_data)
        st.success("'Deckung' document created successfully.")

        return True
    

image = Image.open('logo_ata.png')
# st.image(image , use_column_width=True)

st.title('Project Instantiation')
page_navigation()


with st.expander('Project Details', expanded=True):
    # Input fields for project instantiation
    col1, col2 = st.columns([4,1])
    with col2:
        new_customer = st.checkbox('New customer?')   
    with col1:
        if not new_customer:    
            kunde = st.selectbox('Kunde', customers)
        else:
            kunde = st.text_input('Kunde', key='new_customer')

    benennung, zeichnungs_nr = two_text_columns("Benennung", "Zeichnungs-Nr.")
    ausfuehren_nr = st.number_input('Ausführen Nr', min_value=0, max_value=10000)


with st.expander('Project Documents'):
    project_picture = st.file_uploader('Bild 3D Objekt', type=['png', 'jpg', 'jpeg'])
    if project_picture:
        st.image(project_picture, caption='Uploaded Image', use_column_width=True)

    project_documents = st.file_uploader('Project Documents', type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt'], accept_multiple_files=True)


submit_button = st.button(label='Create Project', use_container_width=True, type="primary")
if submit_button:
    success = instantiate_project(kunde, benennung, zeichnungs_nr, ausfuehren_nr, db)
    if success:
        st.success('Project Created Successfully!')
        #Clear the input fields
        kunde = ''
        benennung = ''
        zeichnungs_nr = ''
        ausfuehren_nr = 0
        project_picture = None
        project_documents = None
    else:
        st.error('A project with this Zeichnungs Nr already exists.')

