import streamlit as st
import requests
import nglview as nv
from io import StringIO

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
    """Fetch protein data from RCSB PDB API."""
    url = f"https://files.rcsb.org/download/{protein_id}.pdb"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text  # Return PDB file content as a string
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

if st.button('Get Info'):
    if protein_input:
        with st.spinner(f"Fetching data for {protein_input}..."):
            pdb_data = fetch_protein_data(protein_input)
            if pdb_data:
                # Display NGLView for the protein structure
                st.markdown("### Protein Structure Visualization")
                
                # Create a NGLView widget to visualize the structure
                view = nv.show_text(StringIO(pdb_data), "pdb")
                view.add_representation('cartoon', selection='protein', color='blue')  # Add cartoon representation
                view.add_representation('line', selection='water')  # Add line representation for water
                st.write(view)  # Display the NGLView widget
                
                # Optionally display raw PDB data if needed
                with st.expander("View Raw PDB Data"):
                    st.text(pdb_data)
            else:
                st.error('Protein not found or invalid PDB ID.')
    else:
        st.warning('Please enter a protein name or PDB ID.')
