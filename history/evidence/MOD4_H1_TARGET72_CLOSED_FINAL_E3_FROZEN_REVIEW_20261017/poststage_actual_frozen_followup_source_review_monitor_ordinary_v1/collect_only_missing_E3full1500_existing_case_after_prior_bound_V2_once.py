"""Single bounded249 connection to existing own case only; never re-dispatch or signal."""
from pathlib import Path
import ast,json,sys,time,os,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';E=N/'curb275_final87_frozen3060_v1'
sys.path[:0]=[str(D),str(W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'),str(E),str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')]
import transport_249_E3_current_exact_desktop_2145_v1 as t
ROOT='D:/MOD4_async_eval/MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/E3_CLOSED85_FROZEN_V3';CASE='e3closed85_public03_full1500_v3';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=R/'E3_CLOSED85_FULL1500_V3_MISSING_ONLY_COMPLETION_BOUND_V2_ACTUAL.json';assert not P.exists()
tree=ast.parse((E/'collect_curb113_own_case_actual_readonly.py').read_text('utf8'));CODE=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='CODE' for y in x.targets))
CODE=CODE.replace("original_error=read(A/'output/ORIGINAL_ERROR.json')","original_error=read(A/'output/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json')")
START=R/'E3_CLOSED85_FULL1500_V3_MISSING_ONLY_COLLECTOR_V2_STARTED_ACTUAL.json';assert not START.exists();START.write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,only_actual_CIM_creation_argv_alive_exclusive_all_host_transport=True,one_connection_metadata_wait_max600seconds_not_total_download_bound=True),indent=2),encoding='utf8')
c=sf=None
try:
 c=t.connect();deadline=time.monotonic()+600
 while True:
  v=t.py(c,'ROOT='+repr(ROOT)+'\nCASE='+repr(CASE)+'\n'+CODE,90)
  if v['parent_child_launcher_actual_absent'] or time.monotonic()>=deadline:break
  current=R/'E3_CLOSED85_FULL1500_V3_MISSING_ONLY_CURRENT_V2_ACTUAL.json';tmp=current.with_suffix('.partial');tmp.write_text(json.dumps(v,indent=2),encoding='utf8');os.replace(tmp,current);time.sleep(min(15,max(0,deadline-time.monotonic())))
 if v['parent_child_launcher_actual_absent']:
  out=D/'actual_E3closed85_full1500_V3_missing_collection_V2';assert not out.exists();out.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(90)
  for row in v['files']:
   if '/source_snapshot/' in row['relative']:row['actual_source_snapshot_index_only_original_retained']=True;continue
   p=out/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);partial=p.with_suffix(p.suffix+'.partial');sf.get(ROOT+'/'+row['relative'],str(partial));assert partial.stat().st_size==row['bytes'] and H(partial)==row['SHA'];partial.replace(p);row['local_path']=str(p.resolve());row['twohost_complete_SHA']=True
 v.update(no_GPU_Task_or_budget_mutation=True,root=ROOT,existing_consumed_native_not_replayed=True)
except BaseException:v=dict(epoch=time.time(),original_transport_error=traceback.format_exc(),no_replay_or_runtime_mutation=True)
finally:
 if sf:sf.close()
 t.close(c)
 with P.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(P),closed=v.get('parent_child_launcher_actual_absent'),free=v.get('shared_OS_lock_free'),complete=v.get('complete'),error=v.get('original_error'),transport_error=v.get('original_transport_error'),tail=v.get('worker_tail','')[-2200:])),flush=True)
