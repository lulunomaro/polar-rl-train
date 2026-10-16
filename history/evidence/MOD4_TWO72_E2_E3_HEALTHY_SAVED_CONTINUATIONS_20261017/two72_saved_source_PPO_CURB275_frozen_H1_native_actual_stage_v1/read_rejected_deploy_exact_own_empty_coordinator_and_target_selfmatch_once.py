from pathlib import Path
import sys,os,time,json,getpass,traceback
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N));import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('REJECTED_DEPLOY_READONLY_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));pw=getpass.getpass('Host72 rejected preflight actual diagnosis only (hidden): ');c=None;v={}
 try:
  c=a.t.connect();v['source']=a.code(c,a.t.PY,"from pathlib import Path;import sys,json,time,psutil;B=Path(sys.argv[1]);v={p.name:json.loads(p.read_bytes()) for p in B.glob('*.json')};c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());ident=v.get('OWNER_IDENTITY.json');p=psutil.Process(ident['pid']) if ident and psutil.pid_exists(ident['pid']) else None;print(json.dumps(dict(epoch=time.time(),files=v,current_canonical_owner=(c['active_segment'] or {}).get('owner_parent_pid'),actual_process=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),children=[dict(pid=q.pid,argv=q.cmdline()) for q in p.children(recursive=True)]) if p else None)))",a.SOURCE)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;spec=json.loads((R/'TWO72_FINAL_PROTOCOL_CPU_NEGATIVES_FROZEN_SOURCES_ACTUAL.json').read_bytes())['specs'][0];v['target']=a.code(c,a.PY,"from pathlib import Path;import sys,json,time,psutil,os;A=Path(sys.argv[1]);B=Path(sys.argv[2]);rows=[]\nfor p in psutil.process_iter(['pid','cmdline','create_time']):\n try:\n  if any(str(A)+'/' in x for x in p.info['cmdline'] or []):rows.append(dict(p.info,is_this_observer=p.pid==os.getpid()))\n except psutil.Error:pass\nprint(json.dumps(dict(epoch=time.time(),self_pid=os.getpid(),matched=rows,newroot_exists=B.exists(),old_EXIT=json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes()))))",a.PREV['e2'],a.ROOTS['e2'],spec['prior_exact_final'])
 finally:
  pw=None
  if c:c.close()
 put('REJECTED_DEPLOY_ACTUAL_EMPTY_OWNER_AND_TARGET_SELF_ARG_MATCH_READONLY.json',v);print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('REJECTED_DEPLOY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
