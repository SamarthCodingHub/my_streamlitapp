import streamlit as st
import requests
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

st.set_page_config(
    page_title="Protein Data Explorer",
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
    st.markdown("Explore protein data from RCSB PDB.")

st.title('Protein Structure Viewer')
protein_input = st.text_input('Enter Protein PDB ID:')

@st.cache_data
def fetch_pdb_data(pdb_id):
    """Fetch PDB data from RCSB PDB."""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching PDB data: {e}")
        return None

def parse_pdb_coordinates(pdb_data):
    """Parse atomic coordinates from PDB data."""
    x, y, z = [], [], []
    for line in pdb_data.splitlines():
        if line.startswith("ATOM") and line[13:15] == "CA":  # Extract alpha carbon atoms (CA)
            try:
                x.append(float(line[30:38].strip()))
                y.append(float(line[38:46].strip()))
                z.append(float(line[46:54].strip()))
            except ValueError:
                continue
    return x, y, z

def plot_protein_structure(x, y, z):
    """Plot protein structure using Matplotlib."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, marker='o', linestyle='-', color='blue')
    
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    
    plt.title('Protein Backbone Structure (Alpha Carbons)')
    
    return fig

if st.button('Visualize Protein'):
    if protein_input:
        with st.spinner(f"Fetching data for {protein_input}..."):
            pdb_data = fetch_pdb_data(protein_input)
            if pdb_data:
                x, y, z = parse_pdb_coordinates(pdb_data)
                if x and y and z:
                    st.markdown("### Protein Structure Visualization")
                    fig = plot_protein_structure(x, y, z)
                    st.pyplot(fig)  # Display the plot
                    
                    with st.expander("View Raw PDB Data"):
                        st.text(pdb_data)
                else:
                    st.error("No valid atomic coordinates found in the PDB file.")
            else:
                st.error("Protein not found or invalid PDB ID.")
    else:
        st.warning("Please enter a valid Protein PDB ID.")
