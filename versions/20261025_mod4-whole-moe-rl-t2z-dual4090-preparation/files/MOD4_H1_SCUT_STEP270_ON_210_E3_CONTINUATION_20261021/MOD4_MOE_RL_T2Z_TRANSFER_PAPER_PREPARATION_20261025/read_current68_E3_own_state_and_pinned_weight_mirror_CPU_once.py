"""Exact own E3 saved-state snapshot after210 connection loss; pinned tiny cache check."""
from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import base64,hashlib,json,os,psutil,subprocess,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025');P=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_reward_sagtuck6a_2510v68/recovery')
texts=[]
for rel in ['NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','NODE_ORIGINAL_ERROR.json','job0/production/FINAL.json','job0/production/latest_complete.json','job0/production/CLOCK_TRAINING_HEALTH.json']:
 p=P/rel
 if p.is_file():
  raw=p.read_bytes();texts.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode(),value=json.loads(raw)))
known=v['worker'];identity=None
try:
 p=psutil.Process(known['pid'])
 if p.create_time()==known['creation'] and p.cmdline()==known['argv']:identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline())
except psutil.Error:pass
probe=r"""import hashlib,json,urllib.request,urllib.error
url='https://hf-mirror.com/Wan-AI/Wan2.2-TI2V-5B/resolve/921dbaf3f1674a56f47e83fb80a34bac8a8f203e/config.json'
try:
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url,timeout=12) as r:raw=r.read(1024);status=r.status
 manifest=json.loads(open('engineering_bundle/WEIGHTS_MANIFEST.json').read());item=next(x for x in manifest['files'] if x['repo_id']=='Wan-AI/Wan2.2-TI2V-5B' and x['file']=='config.json')
 sha=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
 print(json.dumps(dict(host='hf-mirror.com',HTTP_status=status,bytes=len(raw),git_blob_SHA1=sha,expected_bytes=item['bytes'],expected_git_blob_SHA1=item['git_blob_sha1'],pinned_small_source_exact=len(raw)==item['bytes'] and sha==item['git_blob_sha1'],no_model_load=True)))
except urllib.error.URLError as e:print(json.dumps(dict(host='hf-mirror.com',error_type=type(e).__name__,reason_type=type(getattr(e,'reason',None)).__name__,HTTP_status=getattr(e,'code',None))))
"""
proc=subprocess.run([str(B/'run-t2z-python.sh'),'-B','-c',probe],cwd=B,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=35)
assert proc.returncode==0,'Own tiny pinned cache diagnostic failed; no model execution'
print(json.dumps(dict(epoch=time.time(),exact_own_E3_worker_identity=identity,texts=texts,mirror_probe=json.loads(proc.stdout),no_model_raw_GPU_budget_or_training_write=True)))
'''
try:
 put('CURRENT68_E3_AND_PINNED_SMALL_CACHE_DIAGNOSTIC_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 N=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
 metadata=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,dict(worker=metadata['source72']['worker']),timeout=60)
 finally:c.close()
 dest=Z/'actual_host72_preparation_texts/current68_network_boundary';dest.mkdir()
 for row in value['texts']:
  raw=base64.b64decode(row.pop('base64'));assert hashlib.sha256(raw).hexdigest()==row['SHA'];p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(raw)
  row['local_path']=str(p)
 put('CURRENT68_E3_AND_PINNED_SMALL_CACHE_DIAGNOSTIC_RETURNED_ACTUAL.json',value)
 print(json.dumps(value))
except BaseException:
 put('CURRENT68_E3_CACHE_DIAGNOSTIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
