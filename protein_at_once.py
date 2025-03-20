import streamlit as st
import requests
from Bio.PDB import PDBParser
import matplotlib.pyplot as plt
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

def plot_protein_structure(pdb_data):
    """Plot the protein structure using BioPython and Matplotlib."""
    parser = PDBParser()
    structure = parser.get_structure("Protein", StringIO(pdb_data))
    
    # Generate a simple plot of the protein backbone
    x, y, z = [], [], []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.has_id('CA'):  # Only take alpha carbon atoms
                    x.append(residue['CA'].get_coord()[0])
                    y.append(residue['CA'].get_coord()[1])
                    z.append(residue['CA'].get_coord()[2])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, marker='o', linestyle='-', color='b')
    
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    
    plt.title('Protein Backbone Structure')
    
    # Save plot to a BytesIO object
    img = StringIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    return img

if st.button('Get Info'):
    if protein_input:
        with st.spinner(f"Fetching data for {protein_input}..."):
            pdb_data = fetch_protein_data(protein_input)
            if pdb_data:
                # Display protein structure plot using BioPython and Matplotlib
                st.markdown("### Protein Structure Visualization")
                img = plot_protein_structure(pdb_data)
                st.image(img, caption='2D Projection of Protein Backbone', use_column_width=True)
                
                # Optionally display raw PDB data if needed
                with st.expander("View Raw PDB Data"):
                    st.text(pdb_data)
            else:
                st.error('Protein not found or invalid PDB ID.')
    else:
        st.warning('Please enter a protein name or PDB ID.')
