"""Before/after sheet for the mesh-identity fix (what the user was looking at)."""
import os, numpy as np
from PIL import Image, ImageDraw
ROOT=r"D:\claude2\fangzhen"; A=os.path.join(ROOT,"docs","audit")
H=620
def fit(p):
    im=Image.open(p).convert("RGB")
    return im.resize((max(1,int(im.width*H/im.height)),H),Image.LANCZOS)
def cap(im,lines,bg=(16,18,22)):
    h=26*len(lines)+12
    out=Image.new("RGB",(im.width,im.height+h),bg); out.paste(im,(0,h))
    d=ImageDraw.Draw(out)
    for i,l in enumerate(lines): d.text((10,8+i*24),l,fill=(238,241,245))
    return out
before=fit(os.path.join(ROOT,"docs","crops","fig_K_v11_mjlab_flat.png"))
after =fit(os.path.join(A,"hero_C_side_right.png"))
b=cap(before,["BEFORE  705 of 733 CAD parts were drawn as some OTHER part",
              "16 armour plates, 4x DM-J8009 hip motors, both slip rings: never rendered",
              "-> the 'parts flying around / gutted body' symptom"])
a=cap(after,["AFTER  733/733 CAD solids rendered, 2.79 M triangles, 20.00 kg",
             "armour + hip motors + slip rings + nitrogen springs + guide wheels present",
             "physics XML byte-identical -> all v3..v12 RL numbers still valid"])
w=min(b.width,a.width,1000)
bb=np.asarray(b.crop((0,0,w,b.height))); aa=np.asarray(a.crop((0,0,w,a.height)))
g=np.concatenate([bb,np.full((bb.shape[0],12,3),8,dtype=np.uint8),aa],1)
out=os.path.join(A,"fig_before_after.png"); Image.fromarray(g).save(out)
print("wrote",out,g.shape)