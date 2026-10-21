from pathlib import Path
import json,sys,time,shlex,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
REMOTE=r'''
from pathlib import Path
import ast,fcntl,hashlib,importlib.metadata,json,os,psutil,shutil,subprocess,time,zipfile
root=Path(v['root']);owned=Path('/mnt/mod4_linux_durable_20261013');assert root.resolve().is_relative_to(owned.resolve()) and owned.is_mount() and not root.exists()
old=owned/'T2policy50_2010v52/e2';ne=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());tr=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and tr['returncode']==0 and tr['final']['passed'] and not tr['errors']
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:assert p.pid==os.getpid() or not any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);assert v['GPU_UUID'] not in compute;line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if v['GPU_UUID'] in x);assert int(line.split(',')[-1])>15669 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=C.read_bytes();c=json.loads(before);assert c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8;active=c['active_segment'];assert active is None or set(active['experts'])=={'recovery'}
lease=(owned/'H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 old_source=Path(v['old_source']);assert hashlib.sha256((old_source/'SOURCE_MANIFEST.json').read_bytes()).hexdigest()==v['old_manifest_SHA'];assert not any(p.pid!=os.getpid() and any(a.startswith(str(old_source)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));assert json.loads((old_source/'PARENT_EXIT_ACTUAL.json').read_bytes())['all_own_children_waited'];shutil.copytree(old_source,root,ignore=shutil.ignore_patterns('out','PARENT*','CHILD_STARTED_ACTUAL.json','WORKER_FULL.log','SOURCE_ACTUAL_INSTALLED_CPU.json'),copy_function=os.link)
 import base64
 for name,data in v['replacement_texts'].items():
  p=root/name;assert p.resolve().is_relative_to(root.resolve()) and p.suffix in ('.py','.json');p.unlink();p.write_bytes(base64.b64decode(data))
 manifest=json.loads((root/'SOURCE_MANIFEST.json').read_bytes());assert manifest['source_SHA']==v['source_SHA']
 for row in manifest['files']:
  p=root/row['relative'];assert p.resolve().is_relative_to(root.resolve()) and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 import torch
 torch.set_num_threads(2);s=torch.load(root/'job0/source.pt',map_location='cpu',weights_only=False);assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={674740};assert all(torch.isfinite(t).all() for k in ('actor_state_dict','critic_state_dict') for t in s[k].values()) and not torch.cuda.is_initialized()
 q=dict(epoch=time.time(),source_SHA=v['source_SHA'],source_Adam=674740,all_manifest_source_bytes_SHA_and_AST=True,actor9_critic8_STD17Adam_finite_CPU=True,actual_previous52_allout=True,original_private_fcntl_checked=True,strict_GPU_empty_free15669_RAM8_disk25=True,GPU_line=line,active_only_E3_snapshot=active,physics_CPU_only_no_actual_native_pass=True,versions={n:importlib.metadata.version(n) for n in ('torch','isaaclab','isaacsim','rsl-rl-lib')})
 (root/'SOURCE_ACTUAL_INSTALLED_CPU.json').write_text(json.dumps(q,indent=2));print(json.dumps(q))
finally:lease.close()
'''
try:
 q=json.loads((R/'STEP270_COOKED_QUERY_V5_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes());assert q['passed_source_AST_only']
 (R/'STEP270_COOKED_QUERY_V5_DEPLOY_STARTED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),source_SHA=q['source_SHA'],no_learning_GO=True),indent=2))
 c=d.t.connect();root='/mnt/mod4_linux_durable_20261013/H1step270_cookedquery_2110v5';remote='/mnt/mod4_linux_durable_20261013/H1step270_native32_2110v2_INSTALL_SOURCE.zip'
 try:
  ready=d.code(c,d.t.PY,REMOTE,dict(root=root,zip_remote=remote,zip_SHA=q['zip']['SHA'],source_SHA=q['source_SHA'],old_source='/mnt/mod4_linux_durable_20261013/H1step270_native32_2110v4',old_manifest_SHA=__import__('hashlib').sha256((B/'H1_step270_native32_V4_payload/SOURCE_MANIFEST.json').read_bytes()).hexdigest(),replacement_texts={name:__import__('base64').b64encode((Path(q['payload'])/name).read_bytes()).decode() for name in ('worker.py','FROZEN_CONFIG.json','SOURCE_MANIFEST.json')},GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'),timeout=120)
  i,o,e=c.exec_command(shlex.quote(d.t.PY)+' -u -B '+shlex.quote(root+'/parent.py')+' --detach',timeout=30);raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,(raw,err);parent=json.loads(raw)
  started=d.code(c,d.t.PY,"from pathlib import Path;import psutil,json,time;B=Path(v['root']);p=psutil.Process(v['parent']['pid']);assert p.create_time()==v['parent']['creation'];until=time.monotonic()+20\nwhile not (B/'CHILD_STARTED_ACTUAL.json').exists() and not (B/'PARENT_ORIGINAL_ERROR.json').exists() and time.monotonic()<until:time.sleep(.25)\ns=json.loads((B/'CHILD_STARTED_ACTUAL.json').read_bytes());w=psutil.Process(s['worker']['pid']);assert w.create_time()==s['worker']['creation'];print(json.dumps(dict(epoch=time.time(),parent=v['parent'],child_started=s,actual_worker_exe=w.exe(),actual_worker_argv=w.cmdline(),no_actual_final_or_learning_claim=True)))",dict(root=root,parent=parent),timeout=30)
 finally:c.close()
 (R/'STEP270_COOKED_QUERY_V5_DETACHED_ACTUAL_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(installed_CPU=ready,**started),indent=2));print(json.dumps(started))
except BaseException:
 (R/'STEP270_COOKED_QUERY_V5_DEPLOY_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay_or_refund=True),indent=2));raise
