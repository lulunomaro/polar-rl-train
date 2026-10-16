from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_threeway_V4_actual_saved_sources_and_native_reuse_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
def main():
 with (R/'V3_TERMINAL_ERROR_READER_V2_STARTED_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True),f)
 pw=getpass.getpass('Host72 actual recovery CPU gate error (hidden): ');c=None;v={}
 try:c=t.connect();v['source']=code(c,t.PY,READ,ROOTS['curb'],'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['native']=code(c,PY,"from pathlib import Path;import json,time,sys;B=Path(sys.argv[1]);files=[]\nfor p in list(B.glob('*.json'))+list((B/'job0/native').glob('*.json')):\n if p.name in ('SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json','GEOMETRY_AND_RESET_ACTUAL.json'):continue\n raw=p.read_bytes();v=json.loads(raw)\n if p.name=='NATIVE336_COMPLETE.json':v={k:v[k] for k in ('epoch','controls','callbacks','optimizer_updates','SHA','path') if k in v}\n files.append(dict(path=str(p),value=v))\nprint(json.dumps(dict(epoch=time.time(),files=files)))",'/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3');v['e2']=code(c,PY,READ,ROOTS['e2'],'e2');v['recovery']=code(c,PY,READ,ROOTS['recovery'],'recovery')
 finally:
  pw=None
  if c:c.close()
 with (R/'V3_ACTUAL_NATIVE_CPU_TERMINAL_ERROR_V4_OTHER_EXPERTS_CURRENT_V2.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(native=[r for r in v['native']['files'] if any(n in r['path'] for n in ('CPU_ACTUAL_EXIT','PARENT_FINAL','ORIGINAL_ERROR','NATIVE336_COMPLETE','CURRENT_ACTUAL'))],source_current=next((x['value'] for x in v['source']['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{}))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('V3_ERROR_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),f,indent=2)
  raise
