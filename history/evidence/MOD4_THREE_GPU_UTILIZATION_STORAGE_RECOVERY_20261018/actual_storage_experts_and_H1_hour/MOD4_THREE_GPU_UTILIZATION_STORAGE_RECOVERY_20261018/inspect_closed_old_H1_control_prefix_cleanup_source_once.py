"""Inspect exact old closed source and original raw index before choosing obsolete buffers."""
from inventory_current_owned210_storage_readonly_once import *
CODE=r'''
from pathlib import Path
import json,time,psutil
B=Path('/mnt/mod4_linux_durable_20261013/T3_1710v2/h1');F=B/'job0/production/control_prefix_raw';v={}
for n in ('NODE_EXIT_ACTUAL.json','NODE_TERMINAL_ACTUAL.json','NODE_ORIGINAL_ERROR.json','OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json','job0/production/FINAL.json','job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'):
 p=B/n
 if p.is_file():v[n]=json.loads(p.read_bytes())
current=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid==os.getpid():continue
  x=p.info
  if any(s.startswith(str(B)+'/') for s in (x.get('cmdline') or [])+[x.get('cwd') or '']):current.append(dict(pid=p.pid,creation=x['create_time']))
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),root=str(B),files=v,own_old_root_processes=current,index_exists=(F/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').is_file(),root_json_names=[p.name for p in B.glob('*.json')],no_mutation=True)))
'''.replace('import json,time,psutil','import json,time,psutil,os')
if __name__=='__main__':
 c=None
 try:
  save('OLD_CLOSED_H1_PREFIX_INSPECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM_alive_only_transport_owner=True));c=a.t.connect();v=a.code(c,a.t.PY,CODE,timeout=90);save('OLD_CLOSED_H1_PREFIX_SOURCE_INDEX_READONLY_ACTUAL.json',v)
  print(json.dumps(dict(root=v['root'],files_present=list(v['files']),old_processes=v['own_old_root_processes'],summary={k:(dict(index_rows=len(x.get('index',[])),controls=x.get('controls')) if 'INDEX' in k else x) for k,x in v['files'].items() if 'TERMINAL' not in k},root_json=v['root_json_names'])),flush=True)
 except BaseException:save('OLD_PREFIX_INSPECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_delete=True));raise
 finally:a.t.close(c)
