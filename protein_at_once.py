import streamlit as st
import requests
import py3Dmol
import stmol  


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


if st.button('Visualize Protein', key='visualize_button'):
    if protein_input:
        with st.spinner(f"Fetching data for {protein_input}..."):
            pdb_data = fetch_pdb_data(protein_input)
            if pdb_data:
                # Display the 3D structure using py3Dmol and stmol
                st.markdown("### Protein Structure Visualization")
                
                # Create py3Dmol viewer
                view = py3Dmol.view(width=800, height=400)
                view.addModel(pdb_data, "pdb")  # it will load the protein
                view.setStyle({'cartoon': {'color': 'spectrum'}})  # cartoon and rainbow colour
                view.setBackgroundColor('white')  # bg white
                view.zoomTo()  # we can zoom
                
                # Render the viewer in Streamlit using stmol.showmol()
                stmol.showmol(view, height=500, width=800)
                
                # Optionally display raw PDB data in an expandable section
                with st.expander("View Raw PDB Data"):
                    st.text(pdb_data)
            else:
                st.error("Protein not found or invalid PDB ID.")
    else:
        st.warning("Please enter a valid Protein PDB ID.")

