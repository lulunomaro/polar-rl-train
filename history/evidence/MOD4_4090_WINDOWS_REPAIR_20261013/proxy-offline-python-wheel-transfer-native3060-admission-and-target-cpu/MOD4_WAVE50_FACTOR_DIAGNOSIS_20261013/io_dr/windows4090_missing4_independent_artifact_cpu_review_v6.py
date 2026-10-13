"""Independent artifact pass; original download parent/exit is never relabeled."""
from pathlib import Path
import json,sys,time,hashlib,zipfile,email,subprocess
from packaging.tags import sys_tags,parse_tag
R=Path(__file__).resolve().parent;out=R/'install_reports/MISSING4_INDEPENDENT_ARTIFACT_CPU_ACTUAL.json';assert not out.exists()
started=json.loads((R/'install_reports/02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD_STARTED.json').read_bytes());assert started['pid']==18416
proc=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"$p=Get-Process -Id 18416 -ErrorAction SilentlyContinue;if($p){'PRESENT'}else{'ABSENT'}"],capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
assert proc.returncode==0 and proc.stdout.decode('utf8','replace').strip()=='ABSENT','original pip process actualexit required, no kill'
rootproof=json.loads((R/'install_reports/AUTHORIZED_PROXY_VERIFIED_ENDPOINTS_CPU_ACTUAL.json').read_bytes());assert rootproof['all_endpoints_verified_success']
dest=R/'official_missing_nvidia_wheels_v4';files=list(dest.glob('*.whl'));assert len(files)==4
names={'isaacsim-kernel','isaacsim-extscache-kit','isaacsim-asset','isaacsim-robot-motion'};seen=set();tags=set(sys_tags())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
report=dict(epoch=time.time(),python=sys.executable,original_download_child_actual_absent=True,original_parent_wait_receipt_incomplete_preserved=True,original_download_exit_code_unknown_not_claimed=True,original_parent_not_killed_or_restarted=True,only_independent_artifact_CPU_pass=True,no_GPU_Kit_PPO_or_budget=True,files=[])
for p in sorted(files):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None,'complete archive CRC required'
  mn=[n for n in z.namelist() if n.endswith('.dist-info/METADATA') and n.count('/')==1];wn=[n for n in z.namelist() if n.endswith('.dist-info/WHEEL') and n.count('/')==1];assert len(mn)==len(wn)==1
  m=email.message_from_bytes(z.read(mn[0]));wm=email.message_from_bytes(z.read(wn[0]));name=m['Name'].lower().replace('_','-');assert name in names and name not in seen and m['Version']=='5.1.0.0';seen.add(name)
  tg=set().union(*(parse_tag(t) for t in wm.get_all('Tag',[])));assert tg&tags
 report['files'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),name=name,version='5.1.0.0',whole_ZIP_CRC_passed=True,native311_tags_compatible=True,verified_official_index_source='https://pypi.nvidia.com/'+name+'/'))
assert seen==names;report['passed']=True;out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),files=report['files'])))
