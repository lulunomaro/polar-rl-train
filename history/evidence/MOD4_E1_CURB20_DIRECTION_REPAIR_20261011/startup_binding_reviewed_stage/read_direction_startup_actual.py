from direction_io import *
def main():
 root=json.loads((R/'DIRECTION_STARTUP_ACTIVE_ROOT.json').read_bytes())['root'];n,w=io.connect_both()
 try:
  v=io.linux_json(n,'''from pathlib import Path
import json,time
D=Path(ROOT);R=D/'reports';j=lambda p:json.loads(p.read_bytes())
def proc(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 a=(p/'stat').read_text().split(') ',1)[1].split()
 return dict(pid=pid,state=a[0],start_ticks=int(a[19]),argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\\0') if x],cwd=str((p/'cwd').resolve()))
st=j(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else None
names=['E1_ATTENTION.json','ENTRY_ORIGIN_BOUND_SDK10_PASSED.json','DIRECTION_NATIVE20K_PASSED.json','direction_discard128_PASSED.json','direction_discard20k_PASSED.json','ENTRY_FRESH_SAME_SCOPE_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','e1_CURB20_direction_repair_observation_PASSED.json','E1_REVIEW_READY.json','E1_CURB_DIRECTION_ASYNC_PUBLISHED.json']
reports={name:j(R/name) for name in names if (R/name).exists()}
locs=[st.get(k) for k in ('owner','child')] if st else []
active=j(Path(BUDGET))['active_segment']
paths=[D/'controller.log']
if st and st.get('active_log'):paths.append(Path(st['active_log']))
logs={str(p):p.read_text(errors='replace')[-6000:] for p in paths if p.exists()}
print(json.dumps(dict(epoch=time.time(),root=str(D),state=st,actual_processes=[proc(x['pid']) for x in locs if x],reports=reports,canonical_active=active,logs=logs)))
'''.replace('ROOT',repr(root)).replace('BUDGET',repr(io.B)))
  save('DIRECTION_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(epoch=v['epoch'],state=v['state'],actual_processes=v['actual_processes'],report_names=list(v['reports']),attention=v['reports'].get('E1_ATTENTION.json'),active=v['canonical_active'],logs=v['logs']),ensure_ascii=False))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
