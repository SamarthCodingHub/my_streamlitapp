import streamlit as st
import requests
import py3Dmol
import stmol
from Bio.PDB import PDBParser
from io import StringIO
import plotly.express as px

# ----------------------
# App Configuration
# ----------------------
st.set_page_config(
    page_title="Protein Molecule Mosaic",  # Updated page title
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# Helper Functions
# ----------------------
@st.cache_data
def fetch_pdb_data(pdb_id):
    """Fetch PDB data from RCSB with error handling"""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching PDB data: {str(e)}")
        return None

def classify_ligand(residue):
    """Enhanced ligand classification from VTK logic and research"""
    resname = residue.get_resname().strip()
    if len(resname) <= 2:
        return 'ion'
    elif has_polydentate_properties(residue):
        return 'polydentate'
    return 'monodentate'

def has_polydentate_properties(residue):
    """Simplified polydentate detection (customize as needed)"""
    return any(atom.name in ['OXT', 'ND1', 'NE2'] for atom in residue)

def extract_ligands(pdb_data):
    """VTK-inspired ligand processing with classification"""
    parser = PDBParser()
    structure = parser.get_structure("temp", StringIO(pdb_data))
    
    ligands = {
        'ion': [],
        'monodentate': [],
        'polydentate': []
    }
    
    for residue in structure.get_residues():
        if residue.id[0] != ' ':
            ligand_type = classify_ligand(residue)
            if ligand_type == 'ion':
                ligands['ion'].append(residue.get_resname())
            else:
                ligands[ligand_type].append({
                    'resname': residue.get_resname(),
                    'chain': residue.parent.id,
                    'resnum': residue.id[1],
                    'type': ligand_type
                })
    return ligands

# ----------------------
# Visualization Functions
# ----------------------
def create_3d_view(pdb_data, style='cartoon', highlight_ligands=True):
    """Create py3Dmol view with multiple rendering options"""
    view = py3Dmol.view(width=800, height=600)
    view.addModel(pdb_data, 'pdb')
    
    if style == 'cartoon':
        view.setStyle({'cartoon': {'color': 'spectrum'}})
    elif style == 'surface':
        view.setStyle({'cartoon': {'color':'white'}})
        view.addSurface(py3Dmol.SAS, {'opacity':0.7})
    elif style == 'sphere':
        view.setStyle({'sphere': {'colorscheme':'Jmol'}})
    
    if highlight_ligands:
        view.addStyle({'hetflag': True}, 
                     {'stick': {'colorscheme':'greenCarbon', 'radius':0.3}})
    
    view.zoomTo()
    return view

# ----------------------
# UI Components
# ----------------------
def sidebar_controls():
    """Render sidebar controls with tooltips"""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/RCSB_PDB_logo.svg/2560px-RCSB_PDB_logo.svg.png", 
                width=200)
        st.title("Protein Molecule Mosaic")  # Updated title in sidebar
        
        analysis_type = st.radio(
            "Analysis Mode:",
            ["Single Structure"],
            help="Analyze single structure"
        )
        
        render_style = st.selectbox(
            "Rendering Style:",
            ["cartoon", "surface", "sphere"],
            index=0,
            help="Choose molecular representation style"
        )
        
        st.markdown("---")
        st.markdown("**Ligand Display Options**")
        show_ligands = st.checkbox("Highlight Ligands", True)
        
        return {
            'analysis_type': analysis_type,
            'render_style': render_style,
            'show_ligands': show_ligands,
        }

# ----------------------
# Main App Logic
# ----------------------
def main():
    controls = sidebar_controls()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("Protein Palette")
        
        pdb_id = st.text_input("Enter PDB ID:", value="3IAR").upper()
        
        pdb_data = fetch_pdb_data(pdb_id) if pdb_id else None
        
        if pdb_data:
            view = create_3d_view(
                pdb_data, 
                style=controls['render_style'],
                highlight_ligands=controls['show_ligands']
            )
            stmol.showmol(view, height=600, width=800)
                
        else:
            st.warning("Please provide a valid PDB ID to visualize the protein structure.")
                
    with col2:
        st.header("Protein Dynamics")  
        
        if pdb_data:
            with st.expander("Ligand Information"):
                ligands = extract_ligands(pdb_data)
                st.write(f"**Ions:** {len(ligands['ion'])}")
                st.write(f"**Ion Names:** {', '.join(ligands['ion'])}")
                st.write(f"**Monodentate Ligands:** {len(ligands['monodentate'])}")
                st.write(f"**Polydentate Ligands:** {len(ligands['polydentate'])}")
            
            with st.expander("Active Sites"):
                active_sites = [res for res in PDBParser()
                    .get_structure("temp", StringIO(pdb_data))
                    .get_residues() if res.get_resname() in ['HIS', 'ASP', 'GLU']]
                st.write(f"**Potential Active Sites:** {len(active_sites)}")
                st.write("Common catalytic residues highlighted")
            
            with st.expander("Flexibility Report"):
                st.plotly_chart(px.histogram(x=range(10), y=range(10), 
                                  title="Residue Flexibility"))
                st.caption("Simulated flexibility data - integrate MD analysis here")

if __name__ == "__main__":
    main()
