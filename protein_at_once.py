import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="explore protein like no where",
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
    st.markdown("Explore protein data from Database.")



st.title('Protein at once')
protein_input = st.text_input('Enter Protein Name or PDB ID:')


def fetch_protein_data(protein_id):
    url = f"https://data.rcsb.org/rest/v1/core/entry/{protein_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fromat_data_as_trxt(data):
    """Format the JSON data into a plain text."""
    text_output = []

text_output.append(f"Protein ID: {data.get('id', 'N/A')}")
text_output.append(f"Name: {data.get('name', 'N/A')}")

if 'rcsb' in data:
        rcsb_data = data['rcsb']
        text_output.append(f"Release Date: {rcsb_data.get('release_date', 'N/A')}")
        text_output.append(f"Organism: {rcsb_data.get('organism', 'N/A')}")
    
return "\n".join(text_output)

if st.button('Get Info'):
    if protein_input:
        data = fetch_protein_data(protein_input)
        if data:
            
            formatted_text = format_data_as_text(data)
            st.text_area("Protein Information", value=formatted_text, height=300)

            st.download_button(
                label="Download Data",
                data=formatted_text,
                file_name=f"{protein_input}_data.txt",
                mime="text/plain"
            )
        else:
            st.error('Protein not found or invalid PDB ID.')
    else:
        st.warning('Please enter a protein name or PDB ID.')
            

