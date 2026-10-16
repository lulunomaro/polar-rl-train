from pathlib import Path
import sys,json,time,os,getpass,traceback
N=Path(__file__).resolve().parent;P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';R=N/'reports';sys.path.insert(0,str(P));from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import SNAP,CANON,code,H,connect72,t,PY
S='/mnt/mod4_linux_durable_20261013/N72_1710v2';T={k:'/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v2/'+k for k in ('e2','recovery')}
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('V2_ACTUAL_NATIVE_AND_CURB275_FINAL_READONLY_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));pw=getpass.getpass('Host72 exact new native status only (hidden): ');c=None;v={}
 try:
  c=t.connect();v['curb']=code(c,t.PY,SNAP,'/mnt/mod4_linux_durable_20261013/C275_1610v2','curb');v['next_owner']=code(c,t.PY,SNAP,S,'coordinator');v['canonical']=code(c,t.PY,CANON);row=next((r for r in v['curb']['models'] if r['kind']=='actual_final'),None);v['curb_final']=None
  if row:
   folder=N/'actual_CURB275_first_final';folder.mkdir();p=folder/Path(row['path']).name;q=p.with_suffix('.pt.partial');sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p)
   finally:sf.close()
   v['curb_final']=dict(row,local_path=str(p),twohost_complete_SHA=True)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in T:v[key]=code(c,PY,SNAP,T[key],key)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V2_ACTUAL_NEW_NATIVE_STAGES_CURB275_FINAL_COST_HANDOFF_READONLY.json',v)
 print(json.dumps(dict(curb_final=v['curb_final'],canonical=v['canonical'],new_nodes={k:dict(processes=[dict(pid=p['pid'],creation=p['create_time']) for p in v[k]['actual_own_processes']],current=next((r['value'] for r in v[k]['files'] if r['path'].endswith('/NODE_CURRENT.json')),{})) for k in T})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V2_NATIVE_HANDOFF_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
