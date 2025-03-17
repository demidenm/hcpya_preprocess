import os
import argparse
import svgwrite
from pathlib import Path
from svgwrite import cm, mm

def create_language_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_language") / "language_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)

    # Create a new SVG drawing
    dwg = svgwrite.Drawing(save_to_path, size=('950px', '400px'), profile='tiny')  # Increased width to accommodate new blocks

    # Add a white background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

    # Add title
    dwg.add(dwg.text('Language Task: Block Structure', insert=(475, 30), 
                    text_anchor='middle', font_size=20, font_weight='bold', font_family='Arial'))

    # Define colors
    story_color = '#4682B4'  # Steel Blue
    math_color = '#CD5C5C'   # Indian Red
    response_color = '#66CDAA'  # Medium Aquamarine
    change_color = '#DDA0DD'  # Plum
    option_color = '#FFD700'  # Gold for options

    # Y positions for different task types
    story_y = 100
    math_y = 220
    timeline_y = 320

    # Define block widths (time proportions)
    presentation_width = 150
    question_width = 80
    option_width = 70  # Width for story options
    or_width = 2      # Width for the "OR" text
    response_width = 60
    change_width = 40
    gap_width = 0

    # Starting x position
    start_x = 50

    # Create timeline
    dwg.add(dwg.line(start=(start_x, timeline_y), 
                    end=(start_x + 2*(presentation_width + question_width + response_width + change_width + gap_width) + option_width + or_width, timeline_y), 
                    stroke='black', stroke_width=2))

    # Add time markers
    for i in range(8):  # Increased to 6 time markers
        x_pos = start_x + i * 100
        dwg.add(dwg.line(start=(x_pos, timeline_y-5), end=(x_pos, timeline_y+5), stroke='black', stroke_width=1))
    #    dwg.add(dwg.text(f'{i*10}s', insert=(x_pos, timeline_y+20), text_anchor='middle', font_size=10, font_family='Arial'))

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

    # Story 1 Option
    current_x += presentation_width
    add_block(current_x, story_y, option_width, 60, option_color, 'Story 1', 'Option')
    add_connector(current_x, story_y + 25, timeline_y)
    add_connector(current_x + option_width, story_y + 25, timeline_y)

    # Audio "OR" with speaker icon
    current_x += option_width
    
    # Create speaker/audio icon
    icon_size = 16
    icon_x = current_x + or_width/2 - icon_size/2
    icon_y = story_y - 70
    
    # Speaker base
    dwg.add(dwg.rect(insert=(icon_x, icon_y), 
                    size=(icon_size/2, icon_size), 
                    fill='black', 
                    rx=2, ry=2))
    
    # Speaker cone (triangle)
    speaker_cone = dwg.path(d=f"M{icon_x + icon_size/2},{icon_y} L{icon_x + icon_size},{icon_y - icon_size/4} L{icon_x + icon_size},{icon_y + icon_size + icon_size/4} L{icon_x + icon_size/2},{icon_y + icon_size} Z", 
                          fill='black')
    dwg.add(speaker_cone)
    
    # Sound waves (arcs)
    wave1 = dwg.path(d=f"M{icon_x + icon_size + 3},{icon_y + icon_size/2 - icon_size/4} a{icon_size/4},{icon_size/3} 0 0,1 0,{icon_size/2}", 
                    stroke='black', stroke_width=2, fill='none')
    dwg.add(wave1)
    
    wave2 = dwg.path(d=f"M{icon_x + icon_size + 7},{icon_y + icon_size/2 - icon_size/3} a{icon_size/3},{icon_size/2} 0 0,1 0,{icon_size/1.5}", 
                    stroke='black', stroke_width=2, fill='none')
    dwg.add(wave2)
    
    # Add the OR text below the icon
    dwg.add(dwg.text("'Or'", insert=(current_x + or_width/2, story_y - 35), 
            text_anchor='middle', font_size=14, font_family='Arial', font_weight='bold'))
    
    add_connector(current_x, story_y + 25, timeline_y)
    add_connector(current_x + or_width, story_y + 25, timeline_y)
    add_connector(current_x + or_width, story_y + 25, timeline_y)

    # Story 2 Option
    current_x += or_width
    add_block(current_x, story_y, option_width, 60, option_color, 'Story 2', 'Option')
    add_connector(current_x, story_y + 25, timeline_y)
    add_connector(current_x + option_width, story_y + 25, timeline_y)

    # Story Response
    current_x += option_width
    add_block(current_x, story_y, response_width, 60, response_color, 'Response')
    add_connector(current_x, story_y + 25, timeline_y)
    add_connector(current_x + response_width, story_y + 25, timeline_y)

    # Change Block
    current_x += response_width
    add_block(current_x, story_y, change_width, 60, change_color, 'Change')
    add_connector(current_x, story_y + 25, timeline_y)
    add_connector(current_x + change_width, story_y + 25, timeline_y)

    # Gap
    current_x += change_width + gap_width

    # Math Block - Starting at the adjusted position
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
    legend_x = 750  # Moved further right
    legend_y = 30
    legend_items = [
        ("Story Blocks", story_color),
        ("Math Blocks", math_color),
        ("Story Options", option_color),
        ("Response Window", response_color),
        ("Change Block", change_color)
    ]

    for i, (label, color) in enumerate(legend_items):
        y_offset = i * 25
        dwg.add(dwg.rect(insert=(legend_x, legend_y + y_offset), size=(20, 15), fill=color, stroke='black', stroke_width=1))
        dwg.add(dwg.text(label, insert=(legend_x + 30, legend_y + y_offset + 12), font_size=12, font_family='Arial'))

    # Add experiment notes
    notes = [
        "• Story: Aesop's fables followed by two alternative options",
        "• Math: Adaptive difficulty arithmetic problems"
    ]

    for i, note in enumerate(notes):
        dwg.add(dwg.text(note, insert=(50, 370 + i*20), font_size=11, font_family='Arial'))

    # Save the drawing
    dwg.save()


def create_motor_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_motor") / "motor_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)

    # Create a new SVG drawing
    dwg = svgwrite.Drawing(save_to_path, size=('800px', '375'), profile='full')

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
    # Save the drawing
    dwg.save()


def create_relational_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_relational") / "relational_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)

    # Create a new SVG drawing
    dwg = svgwrite.Drawing(save_to_path, size=('800px', '400px'), profile='full')

    # Add a white background with border
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white', stroke='black', stroke_width=1))

    # Add title
    dwg.add(dwg.text('Relational Task Diagram', insert=(400, 50), text_anchor='middle', font_family='Arial', font_size=24, font_weight='bold'))

    # Define colors
    colors = {
        'relational': '#4682B4',  # Blue
        'matching': '#FF6347',    # Red
        'fixation': '#E0E0E0',    # Light gray
        'prompt': '#8A2BE2'       # Purple for prompts
    }

    # Add legend
    legend_y = 90
    legend_x_start = 250
    legend_spacing = 100
    legend_rect_size = 15
    
    # Prompt legend item
    dwg.add(dwg.rect(insert=(legend_x_start, legend_y), size=(legend_rect_size, legend_rect_size), 
                     fill=colors['prompt'], stroke='black', stroke_width=1))
    dwg.add(dwg.text('Prompt', insert=(legend_x_start + legend_rect_size + 5, legend_y + legend_rect_size - 2), 
                     font_family='Arial', font_size=12))
    
    # Relational legend item
    dwg.add(dwg.rect(insert=(legend_x_start + legend_spacing, legend_y), size=(legend_rect_size, legend_rect_size), 
                     fill=colors['relational'], stroke='black', stroke_width=1))
    dwg.add(dwg.text('Relational (R)', insert=(legend_x_start + legend_spacing + legend_rect_size + 5, legend_y + legend_rect_size - 2), 
                     font_family='Arial', font_size=12))
    
    # Matching legend item
    dwg.add(dwg.rect(insert=(legend_x_start + 2*legend_spacing, legend_y), size=(legend_rect_size, legend_rect_size), 
                     fill=colors['matching'], stroke='black', stroke_width=1))
    dwg.add(dwg.text('Matching (M)', insert=(legend_x_start + 2*legend_spacing + legend_rect_size + 5, legend_y + legend_rect_size - 2), 
                     font_family='Arial', font_size=12))
    
    # Fixation legend item
    dwg.add(dwg.rect(insert=(legend_x_start + 3*legend_spacing, legend_y), size=(legend_rect_size, legend_rect_size), 
                     fill=colors['fixation'], stroke='black', stroke_width=1))
    dwg.add(dwg.text('Fixation (p)', insert=(legend_x_start + 3*legend_spacing + legend_rect_size + 5, legend_y + legend_rect_size - 2), 
                     font_family='Arial', font_size=12))

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
        #dwg.add(dwg.text(f"{time}s", insert=(x_pos, timeline_y + text_offset), text_anchor='middle', font_family='Arial', font_size=12))

    # Define blocks for a single run based on task description
    # Now each relational and matching block starts with a 2s prompt
    blocks = [
        {'type': 'prompt', 'label': ' ', 'duration': 2},  # Just use 'R' for relational prompt
        {'type': 'relational', 'label': 'R Block', 'duration': 16},  # Reduced to 16s
        {'type': 'prompt', 'label': ' ', 'duration': 2},  # Just use 'M' for matching prompt
        {'type': 'matching', 'label': 'M Block', 'duration': 16},  # Reduced to 16s
        {'type': 'fixation', 'label': 'F BLock', 'duration': 16},
        {'type': 'prompt', 'label': ' ', 'duration': 2},
        {'type': 'relational', 'label': 'R Block', 'duration': 16},
        {'type': 'prompt', 'label': ' ', 'duration': 2},
        {'type': 'matching', 'label': 'M Block', 'duration': 16},
        {'type': 'fixation', 'label': 'F Block', 'duration': 16},
        {'type': 'prompt', 'label': ' ', 'duration': 2},
        {'type': 'relational', 'label': 'R Block', 'duration': 16},
        {'type': 'prompt', 'label': ' ', 'duration': 2},
        {'type': 'matching', 'label': 'M Block', 'duration': 16},
        {'type': 'fixation', 'label': 'F Block', 'duration': 16},
    ]

    # Total duration is still 156 seconds per run (9 blocks × 16s + 6 prompts × 2s)

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
        
        # Add label inside the block - for prompt, only add a single letter
        if block['type'] == 'prompt':
            # For prompts, just add a letter because space is tight
            dwg.add(dwg.text(
                block['label'],
                insert=(x_pos + block_width/2, timeline_y - block_height/2),
                text_anchor='middle',
                font_family='Arial',
                font_size=10,
                font_weight='bold'
            ))
        else:
            # For other blocks, add the full label
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
            trial_info = "Trials/ITI"
            iti_info = "+ ITI"
            
            # Indicate 4 instances of trials (visual representation)
            trial_width = block_width / 4
            for i in range(4):
                dwg.add(dwg.line(
                    start=(x_pos + i * trial_width, timeline_y - 20),
                    end=(x_pos + i * trial_width, timeline_y - 10),
                    stroke='black', stroke_width=1
                ))
            
            # Add trial information text
            dwg.add(dwg.text(
                trial_info,
                insert=(x_pos + block_width/2, timeline_y - block_height/2 + 15),
                text_anchor='middle',
                font_family='Arial',
                font_size=8
            ))
            #dwg.add(dwg.text(
            #    iti_info,
            #    insert=(x_pos + block_width/2, timeline_y - block_height/2 + 30),
            #    text_anchor='middle',
            #    font_family='Arial',
            #    font_size=10
            #))
            
        elif block['type'] == 'matching':
            # 5 trials per block, 2800ms per trial, 400ms ITI
            trial_info = "Trial/ITI"
            iti_info = "+ ITI"
            
            # Indicate 5 instances of trials (visual representation)
            trial_width = block_width / 5
            for i in range(5):
                dwg.add(dwg.line(
                    start=(x_pos + i * trial_width, timeline_y - 20),
                    end=(x_pos + i * trial_width, timeline_y - 10),
                    stroke='black', stroke_width=1
                ))
            
            # Add trial information text
            dwg.add(dwg.text(
                trial_info,
                insert=(x_pos + block_width/2, timeline_y - block_height/2 + 15),
                text_anchor='middle',
                font_family='Arial',
                font_size=8
            ))
            #dwg.add(dwg.text(
            #    iti_info,
            #    insert=(x_pos + block_width/2, timeline_y - block_height/2 + 30),
            #    text_anchor='middle',
            #    font_family='Arial',
            #    font_size=10
            #))
        
        current_time += block['duration']

    # Add description text
    description_text = [
        "- Each run contains 3 Relational blocks, 3 Matching blocks, and 3 Fixation blocks",
        "- Each relational (R) and matching (M) block starts with a ~2s prompt specifying the block type",
        "- Relational blocks: 4 trials x 3500ms w/ ITI",
        "- Matching blocks: 5 trials x 2800ms w/ ITI"
    ]

    for i, line in enumerate(description_text):
        dwg.add(dwg.text(
            line,
            insert=(400, 300 + i * 20),
            text_anchor='middle',
            font_family='Arial',
            font_size=12
        ))

    # Save the drawing
    dwg.save()


def create_social_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_social") / "social_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)

    # Create a new SVG drawing
    # Remove the 'tiny' profile to avoid limitations
    dwg = svgwrite.Drawing(save_to_path, size=('800px', '400px'))

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


def create_gamble_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_gambling") / "gambling_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)

    # Create drawing with appropriate dimensions
    dwg = svgwrite.Drawing(save_to_path, size=(800, 300))

    # Background and title
    dwg.add(dwg.rect(insert=(0, 0), size=(800, 450), fill='#f8f9fa', rx=5, ry=5))
    dwg.add(dwg.text('Gambling Task Trial Structure', 
                    insert=(400, 30), 
                    font_family="Arial", 
                    font_size=20, 
                    text_anchor="middle", 
                    font_weight="bold"))

    # Legend
    dwg.add(dwg.rect(insert=(620, 60), size=(20, 20), fill='#4daf4a', rx=3, ry=3))
    dwg.add(dwg.text('Reward', insert=(650, 75), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 90), size=(20, 20), fill='#e41a1c', rx=3, ry=3))
    dwg.add(dwg.text('Loss', insert=(650, 105), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 120), size=(20, 20), fill='#999999', rx=3, ry=3))
    dwg.add(dwg.text('Neutral', insert=(650, 135), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 150), size=(20, 20), fill='#377eb8', rx=3, ry=3))
    dwg.add(dwg.text('Question Mark', insert=(650, 165), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 180), size=(20, 20), fill='#ff7f00', rx=3, ry=3))
    dwg.add(dwg.text('Feedback', insert=(650, 195), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 210), size=(20, 20), fill='#984ea3', rx=3, ry=3))
    dwg.add(dwg.text('ITI Fixation (+)', insert=(650, 225), font_family="Arial", font_size=14, text_anchor="start"))

    dwg.add(dwg.rect(insert=(620, 240), size=(20, 20), fill='#a6cee3', rx=3, ry=3))
    dwg.add(dwg.text('Fixation Block (15s)', insert=(650, 255), font_family="Arial", font_size=14, text_anchor="start"))

    # Run 1 Structure
    dwg.add(dwg.text('Run 1', insert=(50, 80), font_family="Arial", font_size=16, font_weight="bold"))

    # Timeline
    dwg.add(dwg.line(start=(50, 120), end=(550, 120), stroke="#333", stroke_width=2))


    # Create rewardBlock group
    reward_block = dwg.g(id="rewardBlock")

    # Trial 1: Reward
    reward_block.add(dwg.rect(insert=(100, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    reward_block.add(dwg.rect(insert=(110, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    reward_block.add(dwg.rect(insert=(115, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 2: Reward
    reward_block.add(dwg.rect(insert=(120, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    reward_block.add(dwg.rect(insert=(130, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    reward_block.add(dwg.rect(insert=(135, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 3: Reward
    reward_block.add(dwg.rect(insert=(140, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    reward_block.add(dwg.rect(insert=(150, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    reward_block.add(dwg.rect(insert=(155, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 4: Loss
    reward_block.add(dwg.rect(insert=(160, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    reward_block.add(dwg.rect(insert=(170, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    reward_block.add(dwg.rect(insert=(175, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 5-8 as a group
    reward_block.add(dwg.rect(insert=(180, 100), size=(40, 40), fill='#4daf4a', fill_opacity=0.5, rx=2, ry=2))
    reward_block.add(dwg.text('Mostly', insert=(200, 120), font_family="Arial", font_size=10, text_anchor="middle"))
    reward_block.add(dwg.text('Reward', insert=(200, 130), font_family="Arial", font_size=10, text_anchor="middle"))

    dwg.add(reward_block)

    # Fixation Block 2
    dwg.add(dwg.rect(insert=(220, 100), size=(50, 40), fill='#a6cee3', rx=3, ry=3))
    dwg.add(dwg.text('Fixation', insert=(245, 150), font_family="Arial", font_size=12, text_anchor="middle"))
    dwg.add(dwg.text('15s', insert=(245, 165), font_family="Arial", font_size=12, text_anchor="middle"))

    # Create lossBlock group
    loss_block = dwg.g(id="lossBlock")

    # Trial 1: Loss
    loss_block.add(dwg.rect(insert=(270, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    loss_block.add(dwg.rect(insert=(280, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    loss_block.add(dwg.rect(insert=(285, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 2: Loss
    loss_block.add(dwg.rect(insert=(290, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    loss_block.add(dwg.rect(insert=(300, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    loss_block.add(dwg.rect(insert=(305, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 3: Neutral
    loss_block.add(dwg.rect(insert=(310, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    loss_block.add(dwg.rect(insert=(320, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    loss_block.add(dwg.rect(insert=(325, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 4: Loss
    loss_block.add(dwg.rect(insert=(330, 100), size=(10, 40), fill='#377eb8', rx=2, ry=2))
    loss_block.add(dwg.rect(insert=(340, 100), size=(5, 40), fill='#ff7f00', rx=1, ry=1))
    loss_block.add(dwg.rect(insert=(345, 100), size=(5, 40), fill='#984ea3', rx=1, ry=1))

    # Trial 5-8 as a group
    loss_block.add(dwg.rect(insert=(350, 100), size=(40, 40), fill='#e41a1c', fill_opacity=0.5, rx=2, ry=2))
    loss_block.add(dwg.text('Mostly', insert=(370, 120), font_family="Arial", font_size=10, text_anchor="middle"))
    loss_block.add(dwg.text('Loss', insert=(370, 130), font_family="Arial", font_size=10, text_anchor="middle"))

    dwg.add(loss_block)

    # Continue with other blocks in Run 1
    dwg.add(dwg.text('...', insert=(410, 120), font_family="Arial", font_size=16, text_anchor="middle"))

    # Last fixation block
    dwg.add(dwg.rect(insert=(440, 100), size=(50, 40), fill='#a6cee3', rx=3, ry=3))
    dwg.add(dwg.text('Fixation', insert=(465, 150), font_family="Arial", font_size=12, text_anchor="middle"))
    dwg.add(dwg.text('15s', insert=(465, 165), font_family="Arial", font_size=12, text_anchor="middle"))

    # Run 2 Structure
    dwg.add(dwg.text('Run 2', insert=(50, 200), font_family="Arial", font_size=16, font_weight="bold"))

    # Timeline for Run 2
    dwg.add(dwg.line(start=(50, 240), end=(550, 240), stroke="#333", stroke_width=2))


    # Clone and move the loss block for Run 2
    loss_block_run2 = dwg.use(loss_block)
    loss_block_run2['transform'] = "translate(-170,120)"
    dwg.add(loss_block_run2)

    # Fixation Block 2
    dwg.add(dwg.rect(insert=(220, 220), size=(50, 40), fill='#a6cee3', rx=3, ry=3))
    dwg.add(dwg.text('Fixation', insert=(245, 270), font_family="Arial", font_size=12, text_anchor="middle"))
    dwg.add(dwg.text('15s', insert=(245, 285), font_family="Arial", font_size=12, text_anchor="middle"))


    # Clone and move the reward block for Run 2
    reward_block_run2 = dwg.use(reward_block)
    reward_block_run2['transform'] = "translate(170,120)"
    dwg.add(reward_block_run2)

    # Continue with other blocks in Run 2
    dwg.add(dwg.text('...', insert=(410, 240), font_family="Arial", font_size=16, text_anchor="middle"))

    # Last fixation block
    dwg.add(dwg.rect(insert=(440, 220), size=(50, 40), fill='#a6cee3', rx=3, ry=3))
    dwg.add(dwg.text('Fixation', insert=(465, 270), font_family="Arial", font_size=12, text_anchor="middle"))
    dwg.add(dwg.text('15s', insert=(465, 285), font_family="Arial", font_size=12, text_anchor="middle"))


    # Save the drawing
    dwg.save()


def create_emotion_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_emotion") / "emotion_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)
    # Create SVG document
    dwg = svgwrite.Drawing(save_to_path, size=('800px', '400px'), profile='full')
    
    # Add background and title
    dwg.add(dwg.rect(insert=(0, 0), size=('800px', '400px'), rx=5, ry=5, fill='#f8f9fa'))
    dwg.add(dwg.text('Emotion Task Trial Structure', insert=('400px', '30px'), 
                    font_family='Arial', font_size='20px', text_anchor='middle', font_weight='bold'))
    
    # Create legend
    legend_items = [
        {'color': '#4e79a7', 'text': 'Face Block'},
        {'color': '#f28e2b', 'text': 'Shape Block'},
        {'color': '#e15759', 'text': 'Cue'},
        {'color': '#76b7b2', 'text': 'Stimulus'},
        {'color': '#59a14f', 'text': 'Fixation (ITI)'}
    ]
    
    for i, item in enumerate(legend_items):
        y_pos = 60 + i * 30
        dwg.add(dwg.rect(insert=('620px', f'{y_pos}px'), size=('20px', '20px'), rx=3, ry=3, fill=item['color']))
        dwg.add(dwg.text(item['text'], insert=('650px', f'{y_pos+15}px'), 
                        font_family='Arial', font_size='14px', text_anchor='start'))
    
    # Diagonal hatch pattern for missing trials
    pattern = dwg.pattern(id='diagonalHatch', patternUnits='userSpaceOnUse', size=(4, 4))
    pattern.add(dwg.path(d='M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2', stroke='#e15759', stroke_width=1))
    dwg.defs.add(pattern)
    
    # Create both runs
    for run_index in range(2):
        y_offset = run_index * 155
        
        # Add run label
        dwg.add(dwg.text(f'Run {run_index + 1}', insert=('50px', f'{40 + y_offset}px'), 
                        font_family='Arial', font_size='16px', font_weight='bold'))
        
        # Add timeline
        dwg.add(dwg.line(start=('50px', f'{100 + y_offset}px'), end=('550px', f'{100 + y_offset}px'), 
                        stroke='#333', stroke_width=2))
        
        # Face Block 1
        dwg.add(dwg.rect(insert=('50px', f'{80 + y_offset}px'), size=('150px', '40px'), 
                        fill='#4e79a7', fill_opacity=0.3, rx=3, ry=3))
        dwg.add(dwg.text('Face Block 1', insert=('125px', f'{130 + y_offset}px'), 
                        font_family='Arial', font_size='12px', text_anchor='middle'))
        
        # Cue for Face Block 1
        dwg.add(dwg.rect(insert=('50px', f'{80 + y_offset}px'), size=('20px', '40px'), 
                        fill='#e15759', rx=3, ry=3))
        dwg.add(dwg.text('"face"', insert=('60px', f'{70 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
        dwg.add(dwg.text('3s', insert=('60px', f'{60 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
        
        # 6 Face Trials
        for trial in range(6):
            x_pos = 70 + trial * 20
            # Stimulus (2s)
            dwg.add(dwg.rect(insert=(f'{x_pos}px', f'{80 + y_offset}px'), size=('15px', '40px'), 
                            fill='#76b7b2', rx=2, ry=2))
            # ITI (1s)
            dwg.add(dwg.rect(insert=(f'{x_pos + 15}px', f'{80 + y_offset}px'), size=('5px', '40px'), 
                            fill='#59a14f', rx=1, ry=1))
        
        # Shape Block 1
        dwg.add(dwg.rect(insert=('200px', f'{80 + y_offset}px'), size=('150px', '40px'), 
                        fill='#f28e2b', fill_opacity=0.3, rx=3, ry=3))
        dwg.add(dwg.text('Shape Block 1', insert=('275px', f'{130 + y_offset}px'), 
                        font_family='Arial', font_size='12px', text_anchor='middle'))
        
        # Cue for Shape Block 1
        dwg.add(dwg.rect(insert=('200px', f'{80 + y_offset}px'), size=('20px', '40px'), 
                        fill='#e15759', rx=3, ry=3))
        dwg.add(dwg.text('"shape"', insert=('210px', f'{70 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
        dwg.add(dwg.text('3s', insert=('210px', f'{60 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
        
        # 6 Shape Trials
        for trial in range(6):
            x_pos = 220 + trial * 20
            # Stimulus (2s)
            dwg.add(dwg.rect(insert=(f'{x_pos}px', f'{80 + y_offset}px'), size=('15px', '40px'), 
                            fill='#76b7b2', rx=2, ry=2))
            # ITI (1s)
            dwg.add(dwg.rect(insert=(f'{x_pos + 15}px', f'{80 + y_offset}px'), size=('5px', '40px'), 
                            fill='#59a14f', rx=1, ry=1))
        
        # Continuation dots
        dwg.add(dwg.text('...', insert=('400px', f'{100 + y_offset}px'), 
                        font_family='Arial', font_size='16px', text_anchor='middle'))
        
        # Last Block (with Bug)
        block_color = '#4e79a7' if run_index == 0 else '#f28e2b'
        dwg.add(dwg.rect(insert=('450px', f'{80 + y_offset}px'), size=('100px', '40px'), 
                        fill=block_color, fill_opacity=0.3, rx=3, ry=3))
        dwg.add(dwg.text('Last Block (Incomplete)', insert=('500px', f'{130 + y_offset}px'), 
                        font_family='Arial', font_size='12px', text_anchor='middle'))
        
        # Cue for Last Block
        dwg.add(dwg.rect(insert=('450px', f'{80 + y_offset}px'), size=('20px', '40px'), 
                        fill='#e15759', rx=3, ry=3))
        
        # Only 3 trials completed in the last block due to bug
        for trial in range(3):
            x_pos = 470 + trial * 20
            # Stimulus (2s)
            dwg.add(dwg.rect(insert=(f'{x_pos}px', f'{80 + y_offset}px'), size=('15px', '40px'), 
                            fill='#76b7b2', rx=2, ry=2))
            # ITI (1s)
            dwg.add(dwg.rect(insert=(f'{x_pos + 15}px', f'{80 + y_offset}px'), size=('5px', '40px'), 
                            fill='#59a14f', rx=1, ry=1))
        
        # Missing trials area (bug)
        dwg.add(dwg.rect(insert=('525px', f'{80 + y_offset}px'), size=('25px', '40px'), 
                        fill='url(#diagonalHatch)', rx=2, ry=2))
        dwg.add(dwg.text('Bug', insert=('535px', f'{70 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
        dwg.add(dwg.text('Missing 3 trials', insert=('535px', f'{60 + y_offset}px'), 
                        font_family='Arial', font_size='10px', text_anchor='middle'))
    
    # Trial Details
    dwg.add(dwg.text('Trial Details', insert=('400px', '330px'), 
                    font_family='Arial', font_size='14px', text_anchor='middle', font_weight='bold'))
    
    details = [
        '• Each block starts with a 3s cue ("shape" or "face")',
        '• Each block contains 6 trials of the same task (3 blocks per type per run)',
        '• Each stimulus is presented for 2s, followed by a 1s inter-trial interval (ITI)'
    ]
    
    for i, detail in enumerate(details):
        y_pos = 355 + i * 20
        dwg.add(dwg.text(detail, insert=('50px', f'{y_pos}px'), 
                        font_family='Arial', font_size='12px', text_anchor='start'))
    
    # Save the SVG file
    dwg.save()


def create_wm_task_diagram(save_to_path: str = None):
    if save_to_path is None:
        save_to_path = Path("./info_wm") / "workingmemory_task_diagram.svg"
    else:
        save_to_path = Path(save_to_path)
        
    # Create a new SVG document
    dwg = svgwrite.Drawing(save_to_path, size=('800px', '250'), profile='tiny')

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
    # Save the SVG file
    dwg.save()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate HCP task schematics')
    parser.add_argument('--task_name', type=str, help='provide task name from: emotion, gamble, language, motor, relational, social, wm')
    parser.add_argument('--output_path', type=str, help='optional custom output path', default=None)
    args = parser.parse_args()
    
    # Configuration from command line args
    task_name = args.task_name
    output_path = args.output_path
    
    # Execute the appropriate function based on task_name
    if task_name == "emotion":
        create_emotion_task_diagram(save_to_path=output_path)
    elif task_name == "gambling":
        create_gamble_task_diagram(save_to_path=output_path)
    elif task_name == "language":
        create_language_task_diagram(save_to_path=output_path)
    elif task_name == "motor":
        create_motor_task_diagram(save_to_path=output_path)
    elif task_name == "relational":
        create_relational_task_diagram(save_to_path=output_path)
    elif task_name == "social":
        create_social_task_diagram(save_to_path=output_path)
    elif task_name == "wm":
        create_wm_task_diagram(save_to_path=output_path)
    else:
        print(f"Error: Unknown task name '{task_name}'")
        print("Available tasks: emotion, gambling, language, motor, relational, social, wm")
        parser.print_help()