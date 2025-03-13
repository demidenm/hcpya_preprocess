import svgwrite
from svgwrite import cm, mm

# Create a new SVG drawing
dwg = svgwrite.Drawing('motor_task_diagram.svg', size=('800px', '375'), profile='full')

# Add a white background with border
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white', stroke='black', stroke_width=1))

# Add title
dwg.add(dwg.text('Motor Task Diagram', insert=(400, 75), text_anchor='middle', font_family='Arial', font_size=24, font_weight='bold'))

# Define colors
colors = {
    'fixation': '#E0E0E0',
    'cue': '#FFD700',
    'left_hand': '#FF6347',
    'right_hand': '#4682B4',
    'left_foot': '#32CD32',
    'right_foot': '#9370DB',
    'tongue': '#FF69B4'
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
time_points = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135]
for i, time in enumerate(time_points):
    x_pos = start_x + (end_x - start_x) * (time / 150)
    dwg.add(dwg.line(start=(x_pos, timeline_y - tick_height/2), end=(x_pos, timeline_y + tick_height/2), stroke='black', stroke_width=1))
    dwg.add(dwg.text(f"{time}s", insert=(x_pos, timeline_y + text_offset), text_anchor='middle', font_family='Arial', font_size=12))

# Define blocks for a single run
blocks = [
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'left_hand', 'label': 'Left Hand', 'duration': 12},
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'right_hand', 'label': 'Right Hand', 'duration': 12},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 15},
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'left_foot', 'label': 'Left Foot', 'duration': 12},
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'right_foot', 'label': 'Right Foot', 'duration': 12},
    {'type': 'fixation', 'label': 'Fixation', 'duration': 15},
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'tongue', 'label': 'Tongue', 'duration': 12},
    {'type': 'cue', 'label': 'Cue', 'duration': 3},
    {'type': 'left_hand', 'label': 'Left Hand', 'duration': 12},
]

# Draw blocks
current_time = 0
for block in blocks:
    block_width = (end_x - start_x) * (block['duration'] / 130)
    x_pos = start_x + (end_x - start_x) * (current_time / 130)
    
    if block['type'] != 'cue':
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
    else:
        # Draw cue as a smaller rectangle
        dwg.add(dwg.rect(
            insert=(x_pos, timeline_y - block_height/2),
            size=(block_width, block_height/2 - tick_height/2),
            fill=colors[block['type']],
            stroke='black',
            stroke_width=1
        ))
        
        # Add label inside the cue
        dwg.add(dwg.text(
            block['label'],
            insert=(x_pos + block_width/2, timeline_y - block_height/4),
            text_anchor='middle',
            font_family='Arial',
            font_size=8
        ))
    
    current_time += block['duration']

# Add description text
description_text = [
    "- Each movement block is preceded by a 3-second cue",
    "- Two runs with 13 blocks each (shown partially above)",
    "- 2 tongue movements, 4 hand movements (2L, 2R), 4 foot movements (2L, 2R), and 3 fixation blocks per run"
]

for i, line in enumerate(description_text):
    dwg.add(dwg.text(
        line,
        insert=(400, 325 + i * 15),
        text_anchor='middle',
        font_family='Arial',
        font_size=12
    ))

# Save the SVG file
dwg.save()