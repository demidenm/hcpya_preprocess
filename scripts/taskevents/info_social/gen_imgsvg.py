import svgwrite
from svgwrite import cm, mm

# Create a new SVG drawing
# Remove the 'tiny' profile to avoid limitations
dwg = svgwrite.Drawing('social_task_diagram.svg', size=('800px', '400px'))

# Add a white background
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

# Add title
dwg.add(dwg.text('Social Interaction Task Timeline', insert=(400, 30), 
                 text_anchor='middle', font_size=24, font_family='Arial', font_weight='bold'))

# Define colors
social_color = '#6CA6CD'  # blue for social interaction
random_color = '#CDC6A1'  # beige for random movement
response_color = '#CDAD9B'  # light coral for response window
fixation_color = '#9BCD9B'  # light green for fixation

# Define dimensions
timeline_y = 200
timeline_height = 60
block_spacing = 10
timeline_start_x = 50
timeline_end_x = 750

# Draw main timeline
dwg.add(dwg.line(start=(timeline_start_x, timeline_y), 
                end=(timeline_end_x, timeline_y), 
                stroke='black', stroke_width=2))

# Define blocks
blocks = [
    {'type': 'fixation', 'label': 'Fixation', 'duration': 15},
    {'type': 'social', 'label': 'Mental Interact Vid', 'duration': 20},
    {'type': 'response', 'label': 'Response', 'duration': 5},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 15},
    {'type': 'random', 'label': 'Random Move Vid', 'duration': 20},
    {'type': 'response', 'label': 'Response', 'duration': 5},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 15},
]

# Calculate total duration for scaling
total_duration = sum(block['duration'] for block in blocks)
timeline_width = timeline_end_x - timeline_start_x

# Draw blocks
current_x = timeline_start_x
for block in blocks:
    block_width = (block['duration'] / total_duration) * timeline_width
    
    # Set color based on block type
    if block['type'] == 'social':
        color = social_color
    elif block['type'] == 'random':
        color = random_color
    elif block['type'] == 'response':
        color = response_color
    else:  # fixation
        color = fixation_color
    
    # Draw block
    dwg.add(dwg.rect(insert=(current_x, timeline_y - timeline_height/2), 
                    size=(block_width, timeline_height), 
                    fill=color, stroke='black', stroke_width=1))
    
    # Add label
    if block_width > 40:  # Only add text if there's enough space
        dwg.add(dwg.text(block['label'], 
                        insert=(current_x + block_width/2, timeline_y + 5), 
                        text_anchor='middle', font_size=12, font_family='Arial'))
    
    # Add time marker
    dwg.add(dwg.line(start=(current_x, timeline_y + timeline_height/2 + 5), 
                    end=(current_x, timeline_y + timeline_height/2 + 15), 
                    stroke='black', stroke_width=1))
    
    # Move to next block
    current_x += block_width

# Add final time marker
dwg.add(dwg.line(start=(timeline_end_x, timeline_y + timeline_height/2 + 5), 
                end=(timeline_end_x, timeline_y + timeline_height/2 + 15), 
                stroke='black', stroke_width=1))

# Add legends
legend_y = 75
legend_spacing = 30
legend_text_offset = 40
legend_box_size = 20

# Social interaction legend
dwg.add(dwg.rect(insert=(100, legend_y), size=(legend_box_size, legend_box_size), 
                fill=social_color, stroke='black', stroke_width=1))
dwg.add(dwg.text('Mental Interaction Video (20s)', 
                insert=(100 + legend_text_offset, legend_y + legend_box_size - 3), 
                font_size=14, font_family='Arial'))

# Random movement legend
dwg.add(dwg.rect(insert=(100, legend_y + legend_spacing), size=(legend_box_size, legend_box_size), 
                fill=random_color, stroke='black', stroke_width=1))
dwg.add(dwg.text('Random Movement Video (20s)', 
                insert=(100 + legend_text_offset, legend_y + legend_spacing + legend_box_size - 3), 
                font_size=14, font_family='Arial'))

# Response window legend
dwg.add(dwg.rect(insert=(400, legend_y), size=(legend_box_size, legend_box_size), 
                fill=response_color, stroke='black', stroke_width=1))
dwg.add(dwg.text('Response Window (5s)', 
                insert=(400 + legend_text_offset, legend_y + legend_box_size - 3), 
                font_size=14, font_family='Arial'))

# Fixation legend
dwg.add(dwg.rect(insert=(400, legend_y + legend_spacing), size=(legend_box_size, legend_box_size), 
                fill=fixation_color, stroke='black', stroke_width=1))
dwg.add(dwg.text('Fixation Period (15s)', 
                insert=(400 + legend_text_offset, legend_y + legend_spacing + legend_box_size - 3), 
                font_size=14, font_family='Arial'))



# Add response options (centered with horizontal layout)
response_y = 300
# Center the title
dwg.add(dwg.text('Response Options:', insert=(400, response_y), 
                text_anchor='middle', font_size=14, font_family='Arial', font_weight='bold'))

response_options = [
    "Social Interaction",
    "Not Sure",
    "No Interaction (Random)"
]

# Calculate positions for horizontally arranged options
option_spacing = 150  # Space between options
total_width = option_spacing * (len(response_options) - 1)
start_x = 400 - (total_width / 2)

# Add options horizontally
for i, option in enumerate(response_options):
    option_x = start_x + (i * option_spacing)
    dwg.add(dwg.text(option, insert=(option_x, response_y + 25), 
                    text_anchor='middle', font_size=12, font_family='Arial'))

# Save the drawing
dwg.save()