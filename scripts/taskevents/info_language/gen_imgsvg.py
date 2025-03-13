import svgwrite
from svgwrite import cm, mm

# Create a new SVG drawing
dwg = svgwrite.Drawing('language_task.svg', size=('800px', '400px'), profile='tiny')

# Add a white background
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

# Add title
dwg.add(dwg.text('Language Task: Block Structure', insert=(400, 30), 
                 text_anchor='middle', font_size=20, font_weight='bold', font_family='Arial'))

# Define colors
story_color = '#4682B4'  # Steel Blue
math_color = '#CD5C5C'   # Indian Red
response_color = '#66CDAA'  # Medium Aquamarine
change_color = '#DDA0DD'  # Plum

# Y positions for different task types
story_y = 100
math_y = 220
timeline_y = 320

# Define block widths (time proportions)
presentation_width = 150
question_width = 80
response_width = 60
change_width = 40
gap_width = 20

# Starting x position
start_x = 50

# Create timeline
dwg.add(dwg.line(start=(start_x, timeline_y), end=(start_x + 2*(presentation_width + question_width + response_width + change_width + gap_width), timeline_y), 
                stroke='black', stroke_width=2))

# Add time markers
for i in range(5):
    x_pos = start_x + i * 100
    dwg.add(dwg.line(start=(x_pos, timeline_y-5), end=(x_pos, timeline_y+5), stroke='black', stroke_width=1))
    dwg.add(dwg.text(f'{i*10}s', insert=(x_pos, timeline_y+20), text_anchor='middle', font_size=10, font_family='Arial'))

# Function to add a block
def add_block(x, y, width, height, color, label, sublabel=None):
    dwg.add(dwg.rect(insert=(x, y-height/2), size=(width, height), fill=color, stroke='black', stroke_width=1, rx=5, ry=5))
    dwg.add(dwg.text(label, insert=(x + width/2, y+5), text_anchor='middle', font_size=12, font_family='Arial', font_weight='bold'))
    if sublabel:
        dwg.add(dwg.text(sublabel, insert=(x + width/2, y+25), text_anchor='middle', font_size=10, font_family='Arial'))

# Function to add a connector between timeline and blocks
def add_connector(x, y, timeline_y):
    dwg.add(dwg.line(start=(x, y), end=(x, timeline_y), stroke='black', stroke_width=1, stroke_dasharray='5,3'))

# Story Block
current_x = start_x

# Story Presentation
add_block(current_x, story_y, presentation_width, 60, story_color, 'Story Presentation', '5-9 sentences')
add_connector(current_x, story_y + 25, timeline_y)
add_connector(current_x + presentation_width, story_y + 25, timeline_y)

# Story Question
current_x += presentation_width
add_block(current_x, story_y, question_width, 60, story_color, 'Question', '2-alternative')
add_connector(current_x, story_y + 25, timeline_y)
add_connector(current_x + question_width, story_y + 25, timeline_y)

# Story Response
current_x += question_width
add_block(current_x, story_y, response_width, 60, response_color, 'Response')
add_connector(current_x, story_y + 25, timeline_y)
add_connector(current_x + response_width, story_y + 25, timeline_y)

# Change Block
current_x += response_width
add_block(current_x, story_y, change_width, 60, change_color, 'Change')
add_connector(current_x, story_y + 25, timeline_y)
add_connector(current_x + change_width, story_y + 25, timeline_y)

# Gap
current_x += change_width 

# Math Block
# Math Presentation
add_block(current_x, math_y, presentation_width, 60, math_color, 'Math Presentation', 'arithmetic operations')
add_connector(current_x, math_y + 25, timeline_y)
add_connector(current_x + presentation_width, math_y + 25, timeline_y)

# Math Question
current_x += presentation_width
add_block(current_x, math_y, question_width, 60, math_color, 'Question', '2-alternative')
add_connector(current_x, math_y + 25, timeline_y)
add_connector(current_x + question_width, math_y + 25, timeline_y)

# Math Response
current_x += question_width
add_block(current_x, math_y, response_width, 60, response_color, 'Response')
add_connector(current_x, math_y + 25, timeline_y)
add_connector(current_x + response_width, math_y + 25, timeline_y)

# Change Block
current_x += response_width
add_block(current_x, math_y, change_width, 60, change_color, 'Change')
add_connector(current_x, math_y + 25, timeline_y)
add_connector(current_x + change_width, math_y + 25, timeline_y)

# Add legend
legend_x = 600
legend_y = 30
legend_items = [
    ("Story Blocks", story_color),
    ("Math Blocks", math_color),
    ("Response Window", response_color),
    ("Change Block", change_color)
]

for i, (label, color) in enumerate(legend_items):
    y_offset = i * 25
    dwg.add(dwg.rect(insert=(legend_x, legend_y + y_offset), size=(20, 15), fill=color, stroke='black', stroke_width=1))
    dwg.add(dwg.text(label, insert=(legend_x + 30, legend_y + y_offset + 12), font_size=12, font_family='Arial'))

# Add experiment notes
notes = [
    "• Story: Aesop's fables followed by comprehension question",
    "• Math: Adaptive difficulty arithmetic problems"
]

for i, note in enumerate(notes):
    dwg.add(dwg.text(note, insert=(50, 370 + i*20), font_size=11, font_family='Arial'))

# Save the drawing
dwg.save()