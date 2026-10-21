from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
READ=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);read=lambda n:json.loads((B/n).read_bytes()) if (B/n).exists() else None;p=v['parent'];identity=read('PARENT_IDENTITY.json');assert identity['pid']==p['pid'] and identity['creation']==p['creation'] and identity['argv']==p['argv'];complete=read('PARENT_COMPLETE_ACTUAL.json');exit=read('PARENT_EXIT_ACTUAL.json');live=None
try:
 a=psutil.Process(p['pid']);live=dict(pid=a.pid,creation=a.create_time(),argv=a.cmdline(),status=a.status());assert live['creation']==p['creation'] and live['argv']==p['argv']
except psutil.NoSuchProcess:pass
gpu=read('out/ACTUAL_SHARED_GPU_COMPUTE.json');cfg=read('out/ACTUAL_CONFIG.json');health=read('out/CLOCK_TRAINING_HEALTH.json');errors=[str(x) for x in (B/'out').glob('*ORIGINAL_ERROR*.json')]
print(json.dumps(dict(epoch=time.time(),root=str(B),parent_actual=live,matching_parent_identity=True,own_GPU_actual=gpu,actual_config=cfg,health_snapshot=health,complete=complete,parent_exit=exit,original_errors=errors,source_GPU_clock_admitted=bool(gpu and cfg and cfg['source_SHA']==v['source_SHA'] and cfg['policy_hz']==50 and cfg['decimation']==8),only_once_first_metadata_not_permanent_alive=True,no_model_or_raw_download_or_account_mutation=True)))
'''
try:
 start=json.loads((R/'SHARED_H1_FULL13_DETACHED_ACTUAL_STARTED.json').read_bytes());secret=memory.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,READ,dict(root=start['parent']['root'],parent=start['parent'],source_SHA=start['child_started']['source_SHA']),timeout=90)
 finally:c.close()
 with (R/'SHARED_H1_FULL13_FIRST_ACTUAL_GPU_CLOCK_METADATA.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(epoch=v['epoch'],source_GPU_clock_admitted=v['source_GPU_clock_admitted'],own_GPU=v['own_GPU_actual'],controls=(v['health_snapshot'] or {}).get('control_steps'),complete=v['complete'],errors=v['original_errors'])))
except BaseException:
 with (R/'SHARED_H1_FULL13_FIRST_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
