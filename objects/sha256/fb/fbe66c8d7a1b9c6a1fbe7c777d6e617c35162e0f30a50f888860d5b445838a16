import os,numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=r"D:\claude2\fangzhen"; A=os.path.join(ROOT,"docs","audit"); S=os.path.join(ROOT,"docs","sjtu")
def load(p,w=None):
    im=Image.open(p).convert("RGB")
    if w and im.width!=w:
        im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
    return im
def crop_frac(p,box,w):
    im=Image.open(p).convert("RGB"); b=box
    return im.crop((int(im.width*b[0]),int(im.height*b[1]),int(im.width*b[2]),int(im.height*b[3]))).resize(
        (w,int(im.height*(b[3]-b[1])*w/(im.width*(b[2]-b[0])))),Image.LANCZOS)
def label(im,txt,h=34,fg=(240,243,246),bg=(20,23,28)):
    out=Image.new("RGB",(im.width,im.height+h),bg); out.paste(im,(0,h))
    d=ImageDraw.Draw(out); d.text((10,9),txt,fill=fg)
    return out
W=900
rows=[
 (crop_frac(os.path.join(S,"pg09.png"),(0.50,0.03,1.00,0.42),W),
  "SJTU RM2025 open-source doc, p.9  串联腿平衡底盘腿部整体结构示意图",
  load(os.path.join(A,"hero_F_leg_closeup.png"),W),
  "OUR SIM (fixed): same linkage - crank + similar-link four-bar + thigh/shank + chain sprockets"),
 (crop_frac(os.path.join(S,"pg14.png"),(0.06,0.40,0.98,0.80),W),
  "SJTU doc p.14  车体框架 (hip machined parts on both sides of the frame, gimbal above)",
  load(os.path.join(A,"hero_A_side_left.png"),W),
  "OUR SIM (fixed): 733/733 CAD solids rendered - armour, hip motors, slip rings, gas springs"),
]
tiles=[]
for l,r in rows:
    tiles.append(np.hstack([np.asarray(label(l,"REF  |  "+r[1].split("  ")[0])),
                            np.asarray(label(r[0],r[1]))]))
# rebuild properly: left = reference caption, right = ours
tiles=[]
for ref,refcap,ours,ourcap in rows:
    a=np.asarray(label(ref,"REFERENCE  |  "+refcap))
    b=np.asarray(label(ours,"OURS  |  "+ourcap))
    h=min(a.shape[0],b.shape[0]); a=a[:h]; b=b[:h]
    sep=np.full((h,10,3),18,dtype=np.uint8)
    tiles.append(np.hstack([a,sep,b]))
w=min(t.shape[1] for t in tiles); tiles=[t[:min(t.shape[0],900),:w] for t in tiles]
pad=np.full((10,w,3),18,dtype=np.uint8)
grid=np.vstack([np.hstack([t,]) for t in tiles[:-1]]+[tiles[-1]]) if False else np.vstack(list(tiles[:-1])+[tiles[-1]])
Image.fromarray(grid).save(os.path.join(A,"compare_sjtu.png"))
print("wrote",os.path.join(A,"compare_sjtu.png"),grid.shape)