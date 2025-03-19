import streamlit as st
import requests

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


