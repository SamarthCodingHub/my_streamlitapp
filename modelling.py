import streamlit as st
import requests
import py3Dmol
import stmol
from Bio.PDB import PDBParser
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.hydrogenbonds.hbond_analysis import HydrogenBondAnalysis
#from ramachandraw.parser import get_phi_psi
#from ramachandraw.utils import fetch_pdb, plot
from openeye import oechem, oedepict, oegrapheme  # Import OpenEye modules

# ----------------------
# App Configuration
# ----------------------
st.set_page_config(
    page_title="Protein Molecule Mosaic",
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

def analyze_hydrogen_bonds(pdb_data):
    """Analyze hydrogen bonds in the provided PDB data."""
    with open("temp.pdb", "w") as f:
        f.write(pdb_data)

    u = mda.Universe("temp.pdb")
    
    hbonds = HydrogenBondAnalysis(
        universe=u,
        donors_sel="name N",  # Nitrogen atoms as donors
        hydrogens_sel="name H",  # Hydrogen atoms for analysis
        acceptors_sel="name O",  # Oxygen atoms as acceptors
        d_a_cutoff=3.5,
        d_h_a_angle_cutoff=150,
    )
    
    hbonds.run()
    
    return hbonds.count_by_time()

def predict_binding_affinity(features):
    """Predict binding affinity based on input features."""
    model = joblib.load("model.pkl")  # Load your pre-trained model here
    return model.predict(np.array(features).reshape(1, -1))

def visualize_ligand_counts(ligands):
    """Create a bar chart of ligand counts."""
    labels = list(ligands.keys())
    counts = [len(ligands[ligand_type]) for ligand_type in labels]
    
    fig = go.Figure(data=[
        go.Bar(name='Ligand Counts', x=labels, y=counts)
    ])
    
    fig.update_layout(title='Ligand Type Counts',
                      xaxis_title='Ligand Type',
                      yaxis_title='Count')
    
    return fig

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

def generate_ramachandran_plot_openeye(pdb_data):
    """Generate Ramachandran plot using OpenEye Toolkit."""
    try:
        # Create an OEGraphMol object from PDB data
        mol = oechem.OEGraphMol()
        if not oechem.OEReadPDBFile(oechem.OEStringIStream(pdb_data), mol):
            st.error("Failed to read PDB data into OpenEye molecule.")
            return None

        # Create an OERamachandranPlot object
        ramaplot = oegrapheme.OERamachandranPlot()
        ramaplot.AddMolecule(mol)

        # Create an image
        image = oedepict.OEImage(600, 400)

        # Render the Ramachandran plot
        oegrapheme.OERenderRamachandranPlot(image, ramaplot, oechem.OERamaType_General)

        # Convert the image to a format that Streamlit can display
        png_data = oedepict.OEWriteImageToString(".png", image)  # Write to PNG format
        return png_data  # Return PNG data
    except Exception as e:
        st.error(f"Error generating Ramachandran plot with OpenEye: {e}")
        return None

# ----------------------
# UI Components
# ----------------------
def sidebar_controls():
    """Render sidebar controls with tooltips"""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/RCSB_PDB_logo.svg/2560px-RCSB_PDB_logo.svg.png", 
                width=200)
        st.title("Protein Molecule Mosaic")
        
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
                
            # Generate and display Ramachandran plot
            with st.expander("Ramachandran Plot (OpenEye)"):
                rama_png = generate_ramachandran_plot_openeye(pdb_data)
                if rama_png:
                    st.image(rama_png, caption="Ramachandran Plot", use_column_width=True)
                else:
                    st.warning("Unable to generate Ramachandran plot using OpenEye.")
                
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
            
            with st.expander("Hydrogen Bond Analysis"):
                hbond_counts = analyze_hydrogen_bonds(pdb_data)
                total_hbonds = np.sum(hbond_counts)  # Corrected summation of NumPy array elements
                st.write(f"Total Hydrogen Bonds: {total_hbonds}")
                if total_hbonds > 0:
                    st.write(f"Counts per Frame: {hbond_counts}")
            
            with st.expander("Binding Affinity Prediction"):
                features_input = st.text_input("Enter Features (comma-separated):", "0.5, 1.2, 0.3")
                if st.button("Predict Binding Affinity"):
                    feature_list = [float(x) for x in features_input.split(",")]
                    affinity = predict_binding_affinity(feature_list)
                    if affinity is not None:
                        st.write(f"Predicted Binding Affinity: {affinity[0]}")
            
            with st.expander("Ligand Type Visualization"):
                fig = visualize_ligand_counts(ligands)
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()
