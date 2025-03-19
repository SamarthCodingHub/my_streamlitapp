import streamlit as st
import requests

# Title of the app
st.title("Ligand Information Viewer")

# Input for ligand name or identifier
ligand_id = st.text_input("Enter Ligand Name or PubChem ID:")

def fetch_ligand_data(ligand_id):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{ligand_id}/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ligand not found.")
        return None

if ligand_id:
    data = fetch_ligand_data(ligand_id)
    if data:
        # Extract required information
        compound = data['PC_Compounds'][0]
        st.subheader("Ligand Information")
        st.write(f"**Molecular Formula:** {compound['formula']}")
        st.write(f"**Molecular Weight:** {compound['mw']}")
        st.write(f"**SMILES:** {compound['smiles']}")

st.subheader("2D Structure")
st.image(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{ligand_id}/PNG", caption="2D Structure")

st.subheader("3D Structure")
st.markdown(f"[View 3D Structure](https://pubchem.ncbi.nlm.nih.gov/pc3d/{ligand_id})")

