"""Actual current17b parent/child/raw collection. No starts/signals/GPU/210."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
t.ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014'
P=Path(__file__).resolve().parent;R=P/'reports';W=P.parent
CASE='native3060_joint_interior_bodypos_worldpos1500_v1'
spec=importlib.util.spec_from_file_location('old_collector_cpu_reference',W/'MOD4_3060_DIRECT_FACTOR_20261013/collect_direct3060_newcase_actual_readonly.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
code=g.CODE
code=code.replace("names=[CASE+'_DEMAND_LAUNCH_ENTERED.json',CASE+'_DEMAND_PARENT_LAUNCH_PID.json',CASE+'_DEMAND_LAUNCH_EXIT.json']", "names=['DEMAND_LAUNCH_ENTERED.json','DEMAND_PARENT_LAUNCH_PID.json','DEMAND_LAUNCH_EXIT.json']")
code=code.replace("top[CASE+'_DEMAND_LAUNCH_ENTERED.json']", "top['DEMAND_LAUNCH_ENTERED.json']").replace("top[CASE+'_DEMAND_PARENT_LAUNCH_PID.json']", "top['DEMAND_PARENT_LAUNCH_PID.json']")
code=code.replace("states['DISPATCH_RECEIPT.json']]:", "states['DISPATCH_RECEIPT.json'],outputs['STARTED.json']]:")
code=code.replace("['STARTED.json','QUERY_ACTUAL.json','COMPLETE_ACTUAL.json','SUBSTEP_HARDWARE_COM_ACTUAL.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json']", "['STARTED.json','QUERY_ACTUAL.json','COMPLETE_ACTUAL.json','SUBSTEP_HARDWARE_COM_ACTUAL.json','FROZEN_POLICY_SOURCE107_ACTUAL.json','CANDIDATE_NATIVE_ACTION_API_WITNESS.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json']")
code=code.replace("p.name not in ['SOURCE_PACKAGE_5585cc8d.zip']", "p.suffix != '.zip'")
code=code.replace("root/(CASE+'_DEMAND_PARENT_CONSOLE.log')", "root/'DEMAND_PARENT_CONSOLE.log'")
code=code.replace('ROOT',repr(t.ROOT)).replace('CASE',repr(CASE));compile(code,'<new readonly17b collection>','exec')
c=None;sf=None;stamp=str(time.time_ns())
try:
 c=t.connect();a=t.py(c,code);sf=c.open_sftp();copied=[];complete=a['states']['PARENT_EXIT_RECEIPT.json'] is not None
 folder=P/'actual_collections'/stamp;folder.mkdir(parents=True)
 for row in a['files']:
  if row['mutable_pending'] and not complete:continue
  if row['bytes']>30_000_000 and not complete:continue
  with sf.open(row['path'].replace('\\','/'),'rb') as f:data=f.read()
  assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
  p=folder/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  copied.append(dict(**row,local_path=str(p),remote_local_byteSHA_exact=True))
 a['local_collected_files']=copied;q=R/('JOINT_CANDIDATE_CURRENT_ACTUAL_'+stamp+'.json');q.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(q),attempt_exists=a['attempt_exists'],PID=a['actual_PID_identities'],lock_free=a['shared_actual_OS_lock_free'],parent_exit=a['states']['PARENT_EXIT_RECEIPT.json'],outputs={k:v is not None for k,v in a['outputs'].items()},logs=a['logs'])),flush=True)
except Exception:
 q=R/('JOINT_CANDIDATE_READER_ORIGINAL_ERROR_'+stamp+'.json');q.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),read_only=True),indent=2),encoding='utf8');raise
finally:
 if sf:sf.close()
 t.close(c)
