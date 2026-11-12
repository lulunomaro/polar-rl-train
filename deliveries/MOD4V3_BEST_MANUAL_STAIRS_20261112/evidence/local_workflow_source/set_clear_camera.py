from pathlib import Path
b=Path(r'D:/claude2/fangzhen/tmp/rough_v1_local_showcase_20261112');p=b/'showcase.py';s=p.read_text(encoding='utf8').replace('self.viewer.cam.azimuth=150.','self.viewer.cam.azimuth=30.')
s=s.replace("state['stage']+=1;k=state['stage']\n    if k==1:","state['stage']+=1;k=state['stage']%(len(CN)+2)\n    if k==0:family.set(CN[0]);load('up')\n    elif k==1:")
p.write_text(s,encoding='utf8');p=b/'capture_clips.py';s=p.read_text(encoding='utf8').replace('cam.azimuth=150.','cam.azimuth=30.');p.write_text(s,encoding='utf8')
