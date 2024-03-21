from google.cloud import firestore
from google.oauth2 import service_account
import streamlit as st

def initialize_firestore_client():
    try:
        key_dict = st.secrets["textkey"]
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds)
    except:
        db = firestore.Client.from_service_account_json("ata-firestore-key.json")
    return db

# Function to get all collection names from Firestore database
def get_all_collections(db):
    excluded_collections = {'operators', 'posts', 'projects'}  # Set of collections to exclude
    collections = db.collections()
    return [collection.id for collection in collections if collection.id not in excluded_collections]

# Function to get all document IDs from a Firestore collection
def get_all_document_ids(db, collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.id for doc in docs]

# Function to get data from Firestore for a specific document in a collection
def get_data_from_firestore(db, collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

# Function to upload data to Firestore
def upload_data_to_firestore(db, collection_name, document_id, data):
    doc_ref = db.collection(collection_name).document(document_id)
    doc_ref.set(data)
    st.success("Data uploaded successfully!")
