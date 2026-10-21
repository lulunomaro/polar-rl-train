from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
code=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);read=lambda name:json.loads((B/name).read_bytes()) if (B/name).is_file() else None
worker=v['child_started']['worker'];p=psutil.Process(worker['pid']);assert p.create_time()==worker['creation']
cfg=read('out/ACTUAL_CONFIG.json');gpu=read('out/ACTUAL_SHARED_GPU_COMPUTE.json');assert cfg['source_SHA']==v['source_SHA'] and cfg['policy_hz']==50 and cfg['decimation']==8 and gpu['own_compute_rows'] and all('GPU-16828f91-2b45-b646-8dc0-9481138e2842' in x for x in gpu['own_compute_rows'])
assert any(x==str(B/'worker.py') for x in p.cmdline())
print(json.dumps(dict(epoch=time.time(),worker_actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()),actual_config=cfg,actual_GPU=gpu,parent_exit=read('PARENT_EXIT_ACTUAL.json'),complete=read('PARENT_COMPLETE_ACTUAL.json'),original_error=read('out/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'),no_intermediate_raw_or_new_GPU=True)))
'''
try:
 v=json.loads((R/'E3_FULL750_DETACHED_ACTUAL_STARTED.json').read_bytes());v['root']=v['parent']['root'];secret=m.recover();c=d.connect72(secret);secret=None
 try:result=d.code(c,d.PY72,code,v,timeout=30)
 finally:c.close()
 (R/'E3_FULL750_FIRST_ACTUAL_GPU_EXE_ARGV_CREATE_METADATA_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(result,indent=2));print(json.dumps(result))
except BaseException:
 (R/'E3_FULL750_FIRST_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc(),no_replay=True),indent=2));raise
