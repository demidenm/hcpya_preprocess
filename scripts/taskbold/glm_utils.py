import nbformat 
import os
import re
import pandas as pd
from IPython.display import display, Markdown
from statsmodels.stats.outliers_influence import variance_inflation_factor


def compute_vifs(design_matrix):
    vif_data = pd.DataFrame()
    vif_data['Var'] = design_matrix.columns
    vif_data['VIF'] = [variance_inflation_factor(design_matrix.values, i) for i in range(design_matrix.shape[1])]
    return vif_data


import nbformat 
import os
import re
from IPython.display import display, Markdown

def generate_tablecontents(notebook_name, auto_number=True):
    """Generate a Table of Contents from markdown headers in the current Jupyter Notebook.
    *Function recommended by claude for table of contents formatting. Iteratively fixed in code
    
    Parameters:
        notebook_name (str): Name of the notebook file to process
        auto_number (bool): Whether to automatically number headers (default: True)
    """
    toc = ["# Table of Contents\n"]
    
    # Counters for header levels
    counters = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    current_level = 0
    
    try:
        # Get the notebook file path
        notebook_path = os.getcwd()
        notebook_file = os.path.join(notebook_path, notebook_name)
        
        if not os.path.exists(notebook_file):
            print(f"Notebook file '{notebook_name}' not found in '{notebook_path}'.")
            return
        
        # Load the notebook content
        with open(notebook_file, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Collect headers
        headers = []
        for cell in notebook.cells:
            if cell.cell_type == "markdown":  # Only process markdown cells
                lines = cell.source.split("\n")
                for line in lines:
                    # Match headers with optional existing numbering
                    match = re.match(r"^(#+)\s+((?:[\d.]+\s+)?)(.*)", line)
                    if match:
                        level = len(match.group(1))  # Number of `#` determines header level
                        existing_number = match.group(2).strip()  # Capture section number if present
                        header_text = match.group(3).strip()  # Extract actual text
                        headers.append((level, existing_number, header_text))
        
        # Process headers and create TOC
        for level, existing_number, header_text in headers:
            # Strip any existing numbers from the header text for the anchor
            original_header = header_text
            
            # Auto-numbering logic for display (but not for anchors)
            display_number = ""
            if auto_number:
                # Reset lower-level counters when moving to higher level
                if level < current_level:
                    for i in range(level + 1, 7):
                        counters[i] = 0
                
                # Increment the counter for current level
                if level == 1:
                    counters[1] += 1
                    display_number = f"{counters[1]}. "
                elif level > 1:
                    # Only increment if it's a new section at this level
                    if level > current_level:
                        counters[level] += 1
                    else:
                        counters[level] += 1
                    
                    # Build the section number (e.g., "1.2.3.")
                    display_number = ""
                    for i in range(1, level + 1):
                        display_number += f"{counters[i]}."
                    display_number += " "
                
                current_level = level
            elif existing_number:
                display_number = f"{existing_number} "
            
            # Create the display text with numbering
            display_text = f"{display_number}{original_header}"
            
            # Create the anchor exactly as Jupyter would
            # Jupyter preserves the case but replaces spaces with hyphens
            anchor = original_header.replace(" ", "-")
            
            # Add entry to TOC with proper indentation
            toc.append(f"{'  ' * (level - 1)}- [{display_text}](#{anchor})")

        # Display table of contents in markdown
        display(Markdown("\n".join(toc)))
        
    except Exception as e:
        print(f"Error generating table of contents: {str(e)}")