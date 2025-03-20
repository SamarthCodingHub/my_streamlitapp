import streamlit as st
from stmol import showmol
import py3Dmol


st.title("protein and small molecules information")

pdb_id=st.text_input("Enter Protein PDB ID:")

if pdb_id:
	 protein_data = fetch_protein_data(pdb_id)

 xyzview = py3Dmol.view(query=f'pdb:{pdb_id}')
 xyzview.setStyle({'stick': {}})
 xyzview.setBackgroundColor('white')
 showmol(xyzview)

 st.header("small molecule Information")
 ligands = fetch_ligand_data(pdb_id)
 st.write(ligands)



 if 'active_site' in protein_data:
     st.header("Active Site Visualization")
     active_site_view = py3Dmol.view(query=f'pdb:{protein_data["active_site"]}')
     showmol(active_site_view)

 st.header("Similar Proteins")
    similar_proteins = fetch_similar_proteins(pdb_id)  
    st.write(similar_proteins)
