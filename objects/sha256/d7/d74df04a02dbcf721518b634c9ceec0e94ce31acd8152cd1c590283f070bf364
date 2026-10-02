import numpy as np,imageio
from PIL import Image
V=r"D:\claude2\fangzhen\docs\videos\model_showcase_fixed.mp4"
fr=[]
for im in imageio.get_reader(V):
    fr.append(np.asarray(im))
    if len(fr)>400: break
n=len(fr); print("frames",n,fr[0].shape)
idx=[int(n*f) for f in (0.10,0.36,0.55,0.80,0.95)]
ims=[fr[i][:700,:1244] for i in idx]
g=np.vstack([np.hstack(ims[:3]),np.hstack([ims[3],ims[4],np.full_like(ims[0],10)])])
Image.fromarray(g).save(r"D:\claude2\fangzhen\docs\audit\fig_M_showcase_frames.png")
print("wrote fig_M_showcase_frames.png",g.shape)