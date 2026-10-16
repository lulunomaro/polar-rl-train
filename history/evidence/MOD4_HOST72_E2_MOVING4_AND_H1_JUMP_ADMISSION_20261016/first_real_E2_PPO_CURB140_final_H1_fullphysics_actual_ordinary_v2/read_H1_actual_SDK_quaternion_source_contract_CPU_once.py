"""Read actual installed tree source, no AppLauncher or CUDA execution."""
from pathlib import Path
import importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
s=importlib.util.spec_from_file_location('prior_pure_transport',D/'deploy_H1_fullphysics_calibration_unused_scope_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert not (R/'H1_ACTUAL_SDK_POSE_QUATERNION_SOURCE_CONTRACT_CPU.json').exists();pw=m.getpass.getpass('Host72 SDK pose source read-only password (hidden): ');c=m.paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(m.paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert m.hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v=m.code(c,r'''
from pathlib import Path
import json,hashlib,time
L=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab');rows=[]
for p in (L/'assets/articulation/articulation_data.py',L/'assets/rigid_object/rigid_object_data.py',L/'utils/math.py'):
 text=p.read_text();rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),source=text if len(text)<20000 else '\n'.join(line for line in text.splitlines() if any(x in line for x in ('quat_apply','xyzw','wxyz','import','body_pos_w','body_quat_w')))))
print(json.dumps(dict(epoch=time.time(),files=rows,source_only_not_simulation=True)))
''')
  with (R/'H1_ACTUAL_SDK_POSE_QUATERNION_SOURCE_CONTRACT_CPU.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps(v),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_QUATERNION_SOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_GPU=True),f,indent=2)
  raise
