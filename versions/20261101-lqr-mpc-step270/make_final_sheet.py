from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent/'results'
items=[('LQR fullDR 5047 - airborne',root/'FINAL_LQR_DR_VIDEO/frame_0047.png'),('MPC fullDR 5063 - touchdown',root/'FINAL_MPC_DR_VIDEO/frame_0054.png'),('LQR fullDR 5047 - stable on top',root/'FINAL_LQR_DR_VIDEO/frame_0239.png'),('MPC fullDR 5063 - stable on top',root/'FINAL_MPC_DR_VIDEO/frame_0239.png')]
canvas=Image.new('RGB',(1920,1260),'#111820');draw=ImageDraw.Draw(canvas)
for i,(title,path) in enumerate(items):
    im=Image.open(path);x=(i%2)*960;y=(i//2)*630;canvas.paste(im,(x,y+30));draw.text((x+15,y+10),title,fill='white')
out=root/'FINAL_CONTROL_CONTACT_SHEET.png';canvas.save(out);print(str(out))
