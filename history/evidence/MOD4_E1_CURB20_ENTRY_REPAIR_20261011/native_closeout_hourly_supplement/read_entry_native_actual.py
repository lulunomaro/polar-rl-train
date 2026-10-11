from repair_io import *
def main():
 n,w=connect_both()
 try:
  value=linux_json(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());rows={}
for p in (D/'reports').glob('ENTRY*.json'):rows[p.name]=j(p)
state=rows.get('ENTRY_NATIVE_STATE.json');actual=[]
for loc in ([state['owner'],state['child']] if state and state['child'] else [state['owner']] if state else []):
 p=Path('/proc')/str(loc['pid']);v=None
 if p.exists():
  f=(p/'stat').read_text().split(') ',1)[1].split();v=dict(pid=loc['pid'],state=f[0],start_ticks=int(f[19]),cwd=str((p/'cwd').resolve()),argv=[a.decode(errors='replace') for a in (p/'cmdline').read_bytes().split(b'\0') if a])
 actual.append(dict(locator=loc,actual=v))
b=j(B);outputs={}
for p in D.glob('ENTRY*.json'):outputs[p.name]=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
print(json.dumps(dict(epoch=time.time(),reports=rows,actual_processes=actual,output_indices=outputs,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=b['authorized_training_seconds'],remaining_seconds=b['remaining_training_seconds'],active_segment=b['active_segment'],controller_log_tail=(D/'controller.log').read_text(errors='replace')[-6000:],no_PPO_controller=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B)))
  p=save('ENTRY_NATIVE_ACTUAL_'+str(time.time_ns())+'.json',value)
  print(json.dumps(dict(report=str(p),state=value['reports'].get('ENTRY_NATIVE_STATE.json'),attention=value['reports'].get('ENTRY_NATIVE_ATTENTION.json'),native_passed='ENTRY_NATIVE_SCOPE_PASSED.json' in value['reports'],outputs=value['output_indices'],active_segment=value['active_segment'])))
 finally:cleanup(n,w)
if __name__=='__main__':main()
