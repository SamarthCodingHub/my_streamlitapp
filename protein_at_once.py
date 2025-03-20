import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="explore protein like no where",
    page_icon=":dna:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .reportview-container .main .block-container{
            max-width: 90%;
            padding-top: 5rem;
            padding-right: 5rem;
            padding-left: 5rem;
            padding-bottom: 5rem;
        }
        img{
            max-width:40%;
            margin-bottom:40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/RCSB_PDB_logo.svg/2560px-RCSB_PDB_logo.svg.png",
        width=200,
    )  # Replace with a direct link to a smaller image
    st.title("Protein Data Explorer")
    st.markdown("Explore protein data from RCSB PDB.")



st.title('Protein at once')
protein_input = st.text_input('Enter Protein Name or PDB ID:')


def fetch_protein_data(protein_id):
    url = f"https://data.rcsb.org/rest/v1/core/entry/{protein_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


if st.button('Get Info'):
    if protein_input:
        data = fetch_protein_data(protein_input)
        if data:
            st.json(data)  # Display JSON data in a readable format
        else:
            st.error('Protein not found or invalid PDB ID.')
    else:
        st.warning('Please enter a protein name or PDB ID.')


