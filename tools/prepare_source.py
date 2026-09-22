"""Prepare the approved design without changing its colors or drawing new anatomy."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'source/approved.png').convert('RGBA')
assert im.size[0]==im.size[1], 'This approved design must be square'
ref=im.resize((1280,1280),Image.Resampling.LANCZOS)
ref.save(ROOT/'source/reference.png')
white=Image.new('RGBA',ref.size,'white');white.alpha_composite(ref)
white.convert('RGB').save(ROOT/'source/inference-input.png')
grid=white.convert('RGB'); draw=ImageDraw.Draw(grid)
for n in range(0,1280,100):
    draw.line((n,0,n,1279),fill=(170,180,200),width=1)
    draw.line((0,n,1279,n),fill=(170,180,200),width=1)
    draw.text((n+3,5),str(n),fill=(200,30,30))
    draw.text((3,n+3),str(n),fill=(200,30,30))
grid.save(ROOT/'validation/design-grid.png')
print('Prepared 1280px reference, white inference input and coordinate grid.')
