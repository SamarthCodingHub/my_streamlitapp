import streamlit as st
import requests

st.title('Protein at once')
protein_name = st.text_input("Enter Protein Name:")

def fetch_protein_info(name):
    url = f"https://www.uniprot.org/uniprot/?query={name}&format=tab&columns=id,protein names,organism,sequence"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching data"

if st.button("Get Protein Info"):
    if protein_name:
        info = fetch_protein_info(protein_name)
        st.text(info)
    else:
        st.warning("Please enter a protein name.")


