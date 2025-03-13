import svgwrite
from svgwrite import cm, mm

# Create a new SVG document
dwg = svgwrite.Drawing('workmemory_task_diagram.svg', size=('800px', '250'), profile='tiny')

# Add a white background
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

# Add title
dwg.add(dwg.text('Working Memory Task Diagram', insert=(400, 30), 
                 text_anchor='middle', font_family='Arial', font_size=20, font_weight='bold'))

# Define colors
cue_color = '#6495ED'    # cornflower blue
stim_color = '#3CB371'    # medium sea green
target_color = '#FF7F50'  # coral
lure_color = '#9370DB'    # medium purple
fixation_color = '#D3D3D3' # light gray

# Define y-positions for different elements
timeline_y = 150
box_height = 60
box_y = timeline_y - box_height - 10
text_y = box_y - 15
arrow_y = timeline_y + 20

# Start position
start_x = 50

# Add the timeline
dwg.add(dwg.line(start=(start_x, timeline_y), end=(750, timeline_y), 
                 stroke='black', stroke_width=2))

# Arrow at the end of timeline
dwg.add(dwg.polygon(points=[(750, timeline_y), (740, timeline_y-5), (740, timeline_y+5)],
                    fill='black'))

# Add "Time" label
dwg.add(dwg.text('Time →', insert=(725, timeline_y+30), 
                 font_family='Arial', font_size=14, text_anchor='middle'))

# Function to add a box with label
def add_box(x_pos, width, color, label, sublabel=None):
    # Add box
    dwg.add(dwg.rect(insert=(x_pos, box_y), size=(width, box_height), 
                    fill=color, stroke='black', stroke_width=1, rx=5, ry=5))
    
    # Add main label
    dwg.add(dwg.text(label, insert=(x_pos + width/2, box_y + 25), 
                    text_anchor='middle', font_family='Arial', font_size=14))
    
    # Add sublabel if provided
    if sublabel:
        dwg.add(dwg.text(sublabel, insert=(x_pos + width/2, box_y + 45), 
                        text_anchor='middle', font_family='Arial', font_size=12))
    
    # Add tick mark on timeline
    dwg.add(dwg.line(start=(x_pos, timeline_y-5), end=(x_pos, timeline_y+5), 
                    stroke='black', stroke_width=1))
    
    return x_pos + width

# Define box widths
cue_width = 60
stim_width = 50
fixation_width = 80

# Current position
current_x = start_x

# First Block - 0-back
dwg.add(dwg.text('Block 1 (0-back)', insert=(current_x + 50, text_y), 
                font_family='Arial', font_size=16, font_weight='bold'))

# Add cue
current_x = add_box(current_x, cue_width, cue_color, 'Cue', '0-back')

# Add stimuli for first block
for i in range(3):
    if i == 1:  # Target
        current_x = add_box(current_x, stim_width, target_color, 'Target', 'Stimulus')
    else:  # Regular stimuli
        current_x = add_box(current_x, stim_width, stim_color, 'Nonlure', 'Stimulus')

# Space between blocks
current_x += 0

# Second Block - 2-back
dwg.add(dwg.text('Block 2 (2-back)', insert=(current_x + 50, text_y), 
                font_family='Arial', font_size=16, font_weight='bold'))

# Add cue
current_x = add_box(current_x, cue_width, cue_color, 'Cue', '2-back')

# Add stimuli for second block
for i in range(4):
    if i == 1:  # Target
        current_x = add_box(current_x, stim_width, target_color, 'Target', 'Stimulus')
    elif i == 2:  # Lure
        current_x = add_box(current_x, stim_width, lure_color, 'Lure', 'Stimulus')
    else:  # Regular stimuli
        current_x = add_box(current_x, stim_width, stim_color, 'Nonlure', 'Stimulus')

# Add fixation block
current_x = add_box(current_x, fixation_width, fixation_color, 'Fixation', 'Rest Period')

# Add legend
legend_x = 100
legend_y = 200
legend_spacing = 120

# Function to add legend item
def add_legend_item(x_pos, color, label):
    dwg.add(dwg.rect(insert=(x_pos, legend_y), size=(15, 15), 
                    fill=color, stroke='black', stroke_width=1))
    dwg.add(dwg.text(label, insert=(x_pos + 25, legend_y + 12), 
                    font_family='Arial', font_size=12))

# Add legend items
add_legend_item(legend_x, cue_color, 'Cue')
add_legend_item(legend_x + legend_spacing, stim_color, 'Nonlure Stim')
add_legend_item(legend_x + legend_spacing*2, target_color, 'Target Stim')
add_legend_item(legend_x + legend_spacing*3, lure_color, 'Lure Stim')
add_legend_item(legend_x + legend_spacing*4, fixation_color, 'Fixation Block')

# Save the drawing
dwg.save()

