import streamlit as st
import pandas as pd   
import py3Dmol
import requests   
from stmol import showmol

st.title("Protein Structure Viewer")
st.write("Enter a PDB ID to view the protein structure.")
    
pdb_id = st.text_input("Enter PDB ID:", "5BRO")
    
def fetch_pdb(pdb_id):
    pdb_url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    return pdb_url

pdb_url = fetch_pdb(pdb_id)
    
def render_mol(pdb_url):
    view = py3Dmol.view(width=400, height=400)

def fetch_pdb(pdb_id):
    pdb_url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    return pdb_url

pdb_url = fetch_pdb(pdb_id)

def render_mol(pdb_url):
    view = py3Dmol.view(width=400, height=400)
    pdb_data = requests.get(pdb_url).text
    view.addModel(pdb_data, "pdb")
    view.setStyle({'stick': {}})
    view.zoomTo()
    return view   

if pdb_id:
    try:
        mol_view = render_mol(pdb_url)
        st.py3Dmol(mol_view)
    except Exception as e:
        st.error(f"Error fetching or rendering PDB: {e}")


