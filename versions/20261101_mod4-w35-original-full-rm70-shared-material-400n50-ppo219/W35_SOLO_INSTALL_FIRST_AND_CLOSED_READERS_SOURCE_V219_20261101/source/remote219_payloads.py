"""Unexecuted root-only target code; original authority and worker own lifecycle."""
AUTH = '''from pathlib import Path
import hashlib,json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
assert c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),CNone=True,canonical_path=str(p),generation=c['authority_generation'],active_segment=c['active_segment'],total_authorized_seconds=c['authorized_training_seconds'],new_authority_budget_extensions=c['new_authority_budget_extensions'],remaining_snapshot=c['remaining_training_seconds'],reserve_required=3900,SHA=hashlib.sha256(raw).hexdigest(),account_write=False)))'''

CREATE = '''from pathlib import Path
import json,psutil,shutil
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve();J=Path(v['job']);O=Path(v['owner'])
assert J.resolve().is_relative_to(base) and O.resolve().is_relative_to(base) and not J.exists() and not O.exists()
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(base).free>25*1024**3
J.mkdir(parents=True);O.mkdir(parents=True);(J/'control219').mkdir()
print(json.dumps(dict(passed=True,new_job=str(J),new_owner=str(O),model_reads=0,account_write=False)))'''

POSTCOPY_AND_SOURCE_COPY = '''from pathlib import Path
import hashlib,json,os,time
B=Path(v['job']);rows=v['files']
for r in rows:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes'] and p.suffix!='.pt'
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==r['SHA'],str(p)
assetrows=[dict(relative=r['asset_relative'],bytes=r['bytes'],SHA=r['SHA']) for r in rows if 'asset_relative' in r]
assert len(assetrows)==2
(B/'RM70_BINARY_INSTALL_ACTUAL.json').write_text(json.dumps(dict(actual_postcopy_fullSHA_verified=True,files=assetrows),indent=2))
src=Path(v['source']['original_target_path']);before=src.stat();dest=B/v['source']['installed_relative'];dest.parent.mkdir()
assert before.st_size==17619013 and not dest.exists()
digest=hashlib.sha256();count=0
with src.open('rb') as f,dest.open('xb') as g:
 while True:
  raw=f.read(1024*1024)
  if not raw:break
  count+=len(raw);digest.update(raw);g.write(raw)
 g.flush();os.fsync(g.fileno())
assert count==v['source']['bytes'] and digest.hexdigest()==v['source']['SHA']
assert src.stat().st_mtime_ns==before.st_mtime_ns
receipt=dict(epoch=time.time(),passed=True,source_realpath=str(src.resolve()),new_copy=str(dest),bytes=count,SHA=digest.hexdigest(),old_input_byte_streams=1,decodes=0,old_source_unchanged=True)
(B/'W35_INPUT_ONE_STREAM_COPY_ACTUAL.json').write_text(json.dumps(receipt,indent=2))
generated=[]
for name in ['RM70_BINARY_INSTALL_ACTUAL.json','W35_INPUT_ONE_STREAM_COPY_ACTUAL.json']:
 raw=(B/name).read_bytes();generated.append(dict(relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
print(json.dumps(dict(passed=True,source_asset_postcopy_passes=1,files=len(rows),input=receipt,generated_metadata_rows=generated,no_GPU_or_model_decode_or_account_write=True)))'''

SPAWN = '''from pathlib import Path
import importlib.util,sys,os,json,psutil
B=Path(v['root']);sys.path.insert(0,str(B));p=B/v['module'];s=importlib.util.spec_from_file_location('owned219_launch',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not (B/v['console']).exists();pid=os.fork()
if pid:
 q=psutil.Process(pid);print(json.dumps(dict(pid=pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd(),root=str(B),role=v['role'])),flush=True)
else:
 os.setsid();fd=os.open(str(B/v['console']),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd)
 if v['role']=='owner':m.owner(v['config'])
 else:m.node(v['config'])
'''

FIRST = '''from pathlib import Path
import json,time,hashlib
B=Path(v['job']);C=B/'control219';f=B/'production/FIRST_ACTUAL_NEW_PPO_UPDATE.json';end=time.time()+850
while time.time()<end and not f.is_file() and not (C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
names=['NODE_IDENTITY.json','WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json','NODE_CURRENT.json','ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json']
paths=[C/n for n in names]+[B/'GO_PRODUCTION.json',B/'PREDELEGATE218_METADATA_GATE_ACTUAL.json']
paths += [B/'production'/n for n in ['ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json','NATIVE24_W35_RM70_V3_ACTUAL.json','FIRST_ACTUAL_NEW_PPO_UPDATE.json','latest_complete.json','LATEST_PROGRESS.json','ORIGINAL_W35_RM70_V3_ERROR.json','FINAL.json','SOURCE208_V3_FINAL_READ_COUNTS.json','APP_CLOSED.json']]
rows=[]
for p in paths:
 if p.is_file():
  raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
value=json.loads(f.read_bytes()) if f.is_file() else None
log=C/'production_WORKER.log';prefix=None;errors=[]
if log.is_file():
 size=log.stat().st_size
 with log.open('rb') as s:raw=s.read(size)
 text=raw.decode('utf8','replace');errors=[x for x in text.splitlines() if 'PxPhysics::createMaterial' in x and '64K' in x]
 prefix=dict(path=str(log),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=text,scope='Original owned stdout at ONE FIRST collection;not final or skill')
native=B/'production/NATIVE24_W35_RM70_V3_ACTUAL.json';n=json.loads(native.read_bytes()) if native.is_file() else None
passed=bool(value and value.get('passed') and value.get('actual_new_PPO_updates')==1 and value.get('new_environment_transitions')==480000 and value.get('source_SHA')==v['source_SHA'] and value.get('initial_Adam_step')==648360 and value.get('new_Adam_step')==648380 and value.get('first_complete',{}).get('saved_iteration')==32337 and value['first_complete']['Adam_min']==value['first_complete']['Adam_max']==648380 and n and n.get('passed') and n.get('controls')==24 and n.get('physics_callbacks')==192 and n.get('feedback_samples')==48 and not errors)
print(json.dumps(dict(epoch=time.time(),passed=passed,first=value,native24=n,actual_material_limit_error_count=len(errors),original_material_error_lines=errors,full_selected_UTF8=rows,original_stdout_prefix=prefix,single_first_wait850=True,snapshot_not_final_or_skill=True)))'''

OWNER_STATE = '''from pathlib import Path
import json,time
B=Path(v['owner']['root']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];files={}
for name in ['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json']:
 p=B/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
assert files['OWNER_IDENTITY.json']['pid']==v['owner']['pid'] and files['OWNER_IDENTITY.json']['creation']==v['owner']['creation']
if a is not None:assert a['owner_parent_pid']==v['owner']['pid']
current=files.get('OWNER_CURRENT.json',{})
print(json.dumps(dict(epoch=time.time(),current_owner_matched=a is not None and a['owner_parent_pid']==v['owner']['pid'],canonical_None=a is None,current=current,files=files,no_account_write=True)))'''
