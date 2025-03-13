import svgwrite
from svgwrite import cm, mm

# Create a new SVG drawing
dwg = svgwrite.Drawing('relational_task_diagram.svg', size=('800px', '400px'), profile='full')

# Add a white background with border
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white', stroke='black', stroke_width=1))

# Add title
dwg.add(dwg.text('Relational Task Diagram', insert=(400, 50), text_anchor='middle', font_family='Arial', font_size=24, font_weight='bold'))

# Define colors
colors = {
    'relational': '#4682B4',  # Blue
    'matching': '#FF6347',    # Red
    'fixation': '#E0E0E0'     # Light gray
}

# Define timeline parameters
start_x = 50
end_x = 750
timeline_y = 250
block_height = 100
timeline_height = 2
tick_height = 10
text_offset = 25

# Draw timeline
dwg.add(dwg.line(start=(start_x, timeline_y), end=(end_x, timeline_y), stroke='black', stroke_width=timeline_height))

# Add time markers (seconds)
time_points = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]
for i, time in enumerate(time_points):
    x_pos = start_x + (end_x - start_x) * (time / 150)
    dwg.add(dwg.line(start=(x_pos, timeline_y - tick_height/2), end=(x_pos, timeline_y + tick_height/2), stroke='black', stroke_width=1))
    dwg.add(dwg.text(f"{time}s", insert=(x_pos, timeline_y + text_offset), text_anchor='middle', font_family='Arial', font_size=12))

# Define blocks for a single run based on task description
# 3 relational blocks (18s each), 3 matching blocks (18s each), 3 fixation blocks (16s each)
blocks = [
    {'type': 'relational', 'label': 'Relational Block', 'duration': 18},
    {'type': 'matching', 'label': 'Matching Block', 'duration': 18},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 16},
    {'type': 'relational', 'label': 'Relational Block', 'duration': 18},
    {'type': 'matching', 'label': 'Matching Block', 'duration': 18},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 16},
    {'type': 'relational', 'label': 'Relational Block', 'duration': 18},
    {'type': 'matching', 'label': 'Matching Block', 'duration': 18},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 16},
]

# Total duration is 156 seconds per run

# Draw blocks
current_time = 0
for block in blocks:
    block_width = (end_x - start_x) * (block['duration'] / 156)
    x_pos = start_x + (end_x - start_x) * (current_time / 156)
    
    # Draw the block
    dwg.add(dwg.rect(
        insert=(x_pos, timeline_y - block_height),
        size=(block_width, block_height - tick_height/2),
        fill=colors[block['type']],
        stroke='black',
        stroke_width=1
    ))
    
    # Add label inside the block
    dwg.add(dwg.text(
        block['label'],
        insert=(x_pos + block_width/2, timeline_y - block_height/2),
        text_anchor='middle',
        font_family='Arial',
        font_size=10,
        font_weight='bold'
    ))
    
    # For Relational and Matching blocks, add trial information
    if block['type'] == 'relational':
        # 4 trials per block, 3500ms per trial, 500ms ITI
        trial_info = "4 trials x 3500ms"
        iti_info = "+ ITI"
    elif block['type'] == 'matching':
        # 5 trials per block, 2800ms per trial, 400ms ITI
        trial_info = "5 trials x 2800ms"
        iti_info = "+ ITI"
    else:
        trial_info = ""
        iti_info = ""
    
    if trial_info:
        dwg.add(dwg.text(
            trial_info,
            insert=(x_pos + block_width/2, timeline_y - block_height/2 + 15),
            text_anchor='middle',
            font_family='Arial',
            font_size=8
        ))
        dwg.add(dwg.text(
            iti_info,
            insert=(x_pos + block_width/2, timeline_y - block_height/2 + 30),
            text_anchor='middle',
            font_family='Arial',
            font_size=10
        ))
    
    current_time += block['duration']

# Add description text
description_text = [
    "- Each run contains 3 relational blocks, 3 matching blocks, and 3 fixation blocks (16s each)",

]

for i, line in enumerate(description_text):
    dwg.add(dwg.text(
        line,
        insert=(400, 300 + i * 20),
        text_anchor='middle',
        font_family='Arial',
        font_size=12
    ))



# Matching condition example
matching_x = 600
matching_y = 140




# Save the SVG file
dwg.save()