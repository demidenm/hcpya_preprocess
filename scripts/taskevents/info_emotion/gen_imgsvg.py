# WRITTEN BY claudi.ai based on provided instruction / details
import svgwrite
from svgwrite import cm, mm

def create_emotion_task_diagram(filename="emotion_task_diagram.svg"):
    # Create SVG document
    dwg = svgwrite.Drawing(filename, size=('800px', '400px'), profile='full')
    
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
    return filename

if __name__ == "__main__":
    output_file = create_emotion_task_diagram()
    print(f"SVG diagram created: {output_file}")