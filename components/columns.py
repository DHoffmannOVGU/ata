import streamlit as st

def two_text_columns(col1_name, col2_name):
    col1, col2 = st.columns(2)
    with col1:
        col1_data = st.text_input(col1_name)
    with col2:
        col2_data = st.text_input(col2_name)

    return col1_data, col2_data

def three_text_columns(col1_name, col2_name, col3_name):
    col1, col2, col3 = st.columns(3)
    with col1:
        col1_data = st.text_input(col1_name)
    with col2:
        col2_data = st.text_input(col2_name)
    with col3:
        col3_data = st.text_input(col3_name)

    return col1_data, col2_data, col3_data

def four_text_columns(col1_name, col2_name, col3_name, col4_name, values=[]):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        col1_data = st.text_input(col1_name, )
    with col2:
        col2_data = st.text_input(col2_name)
    with col3:
        col3_data = st.text_input(col3_name)
    with col4:
        col4_data = st.text_input(col4_name)

    return col1_data, col2_data, col3_data, col4_data