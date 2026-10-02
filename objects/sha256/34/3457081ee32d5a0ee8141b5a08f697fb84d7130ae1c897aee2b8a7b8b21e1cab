import os,shutil
SRC=r"D:/claude2/fangzhen/robot/out_cc"
DST=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/assets"
os.makedirs(os.path.join(DST,"meshes_cc"),exist_ok=True)
for f in os.listdir(os.path.join(DST,"meshes_cc")): os.remove(os.path.join(DST,"meshes_cc",f))
xml=open(os.path.join(SRC,"rm_vehicle_cc.xml"),encoding="utf-8").read()
assert 'meshdir="meshes/"' in xml
xml=xml.replace('meshdir="meshes/"','meshdir="meshes_cc/"')
open(os.path.join(DST,"rm_vehicle_cc.xml"),"w",encoding="utf-8",newline="\n").write(xml)
n=0
for f in sorted(os.listdir(os.path.join(SRC,"meshes"))):
    if f.lower().endswith(".stl"):
        shutil.copy2(os.path.join(SRC,"meshes",f),os.path.join(DST,"meshes_cc",f)); n+=1
print("mjlab assets refreshed: rm_vehicle_cc.xml + %d meshes (no GPU smoke test while v12 trains)"%n)