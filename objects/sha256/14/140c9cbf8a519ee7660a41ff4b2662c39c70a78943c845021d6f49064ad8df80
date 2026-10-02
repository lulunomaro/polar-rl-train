import json, os, shutil
idx=json.load(open(r"D:/claude2/fangzhen/robot/out/mesh_index.json"))
dst=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/assets/meshes"
for f in os.listdir(dst): os.remove(os.path.join(dst,f))
n=0
for k,v in idx.items():
    for f in v["files"]:
        shutil.copy2(os.path.join(r"D:/claude2/fangzhen/robot/out/meshes",f), os.path.join(dst,f)); n+=1
print("copied",n,"meshes for",len(idx),"links")
