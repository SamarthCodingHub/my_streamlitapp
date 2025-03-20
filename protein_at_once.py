import streamlit as st
import requests
import json  

st.set_page_config(
    page_title="Explore Protein Like No Where",
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


with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/RCSB_PDB_logo.svg/2560px-RCSB_PDB_logo.svg.png",
        width=200,
    )
    st.title("Protein Data Explorer")
    st.markdown("Explore protein data from Database.")

st.title('Protein at Once')
protein_input = st.text_input('Enter Protein Name or PDB ID:')

@st.cache_data
def fetch_protein_data(protein_id):
    url = f"https://data.rcsb.org/rest/v1/core/entry/{protein_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

def format_data_as_text(data):
    """Format the JSON data into a plain text."""
    text_output = []

    text_output.append(f"Protein ID: {data.get('id', 'N/A')}")

    # Handle 'struct' data
    if 'struct' in data:
        if isinstance(data['struct'], list):
            titles = [struct_info.get('title', 'N/A') for struct_info in data['struct']]
            text_output.append(f"Name: {', '.join(titles)}")
        elif isinstance(data['struct'], dict):
            text_output.append(f"Name: {data['struct'].get('title', 'N/A')}")
        else:
            text_output.append(f"Name: N/A")
    else:
        text_output.append(f"Name: N/A")

    # Handle 'rcsb_entry_info'
    if 'rcsb_entry_info' in data:
        rcsb_data = data['rcsb_entry_info']
        text_output.append(f"Release Date: {rcsb_data.get('initial_release_date', 'N/A')}")
    else:
        text_output.append(f"Release Date: N/A")

    # Handle organism data
    organisms = []
    if 'rcsb_entity_source_organism' in data:
        if isinstance(data['rcsb_entity_source_organism'], list):
            for entity in data['rcsb_entity_source_organism']:
                if isinstance(entity, dict) and 'rcsb_source_organism' in entity:
                    for org in entity.get('rcsb_source_organism', []):
                        if isinstance(org, dict):
                            organisms.append(org.get('ncbi_scientific_name', 'N/A'))

    text_output.append(f"Organism: {', '.join(organisms) if organisms else 'N/A'}")

    return "\n".join(text_output)


if st.button('Get Info'):
    if protein_input:
        with st.spinner(f"Fetching data for {protein_input}..."):
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
