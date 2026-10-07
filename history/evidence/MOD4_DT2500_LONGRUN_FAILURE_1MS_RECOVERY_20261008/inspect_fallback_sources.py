from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,hashlib
A=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fa=read(A/'reports/SOURCE_FREEZE.json')['sha256'];ft=read(T/'reports/SOURCE_FREEZE.json')['sha256']
for d,f in ((A,fa),(T,ft)):
 for n,h in f.items():assert sha(d/n)==h,n
diff={n:{'repaired':fa[n],'original1ms':h} for n,h in ft.items() if n in fa and fa[n]!=h}
print(json.dumps(dict(repair_count=len(fa),original1ms_count=len(ft),common_differences=diff,original1ms_env=read(T/'isaac/mod4/env.json'),repaired_env=read(A/'isaac/mod4/env.json'),original1ms_reports=[p.name for p in (T/'reports').glob('*.json')],all_sources_exact=True)))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'EXACT_1MS_REUSE_COMPARISON.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(repair_count=v['repair_count'],original1ms_count=v['original1ms_count'],common_differences=v['common_differences'],original1ms_reports=v['original1ms_reports'])))
 with c.open_sftp() as sf:
  for n in ('supervision_sdk_probe.py','isaac/mod4/clock_training_health.py'):
   target=R/Path(n).name;sf.get('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007/'+n,str(target))
finally:c.close()
