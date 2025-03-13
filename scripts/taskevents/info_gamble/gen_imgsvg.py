import svgwrite
from svgwrite import cm, mm

# Create drawing with appropriate dimensions
dwg = svgwrite.Drawing('gambling_task.svg', size=(800, 300))

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