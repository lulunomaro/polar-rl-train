import json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent/'results/rendered_strict_success_v1'
files=[('Approach / t=0.65s','frame_0032.png'),('Flight / t=0.95s','frame_0047.png'),('Landing / t=1.09s','frame_0054.png'),('Recovery / t=2.81s','frame_0140.png')]
canvas=Image.new('RGB',(1920,1260),'#111820');draw=ImageDraw.Draw(canvas)
for i,(title,fn) in enumerate(files):
    im=Image.open(R/fn);x=(i%2)*960;y=(i//2)*630;canvas.paste(im,(x,y+30));draw.text((x+15,y+10),title,fill='white')
canvas.save(R/'contact_sheet.png')
print(str(R/'contact_sheet.png'))
