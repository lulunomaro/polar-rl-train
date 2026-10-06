"""Forced-command, read-snapshot/write-result-only SSH bridge. Never launches learning."""
from pathlib import Path
import base64,hashlib,json,os,re,sys
ROOT=Path(__file__).resolve().parent
Q=ROOT/'eval_queue';RESULTS=ROOT/'eval_results'
MAX_CHUNK=262144
def key(value):
 if not isinstance(value,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{5,95}',value):raise ValueError('Invalid job identifier')
 return value
def safe_file(directory,name):
 if not isinstance(name,str) or not re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}',name) or name.startswith('.'):raise ValueError('Invalid artifact name')
 p=(directory/name).resolve()
 if not p.is_relative_to(directory.resolve()):raise ValueError('Path escape')
 return p
def atomic(p,d):
 t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(d));os.replace(t,p)
def manifest(job):
 p=Q/(key(job)+'.json');d=json.loads(p.read_text())
 if d['job_id']!=job or d['stage']!='S0E' or not d['immutable']:raise ValueError('Invalid published job')
 return d
def handle(req):
 op=req.get('op')
 if op=='list_jobs':return {'jobs':[p.stem for p in sorted(Q.glob('*.json')) if p.is_file()]}
 job=key(req.get('job_id'));d=manifest(job)
 if op=='manifest':return d
 if op=='artifact_part':
  alias=req.get('artifact');row=d['artifacts'].get(alias)
  if not row:raise ValueError('Not a published artifact')
  p=Path(row['path']).resolve()
  if not any(p.is_relative_to(r.resolve()) for r in [ROOT,Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs')]):raise ValueError('Source outside artifact allowlist')
  offset=req.get('offset',0);count=req.get('count',MAX_CHUNK)
  if type(offset)!=int or type(count)!=int or offset<0 or not 0<count<=MAX_CHUNK:raise ValueError('Invalid part')
  if p.stat().st_size!=row['bytes']:raise ValueError('Snapshot size changed')
  with p.open('rb') as f:f.seek(offset);raw=f.read(count)
  return {'offset':offset,'data':base64.b64encode(raw).decode(),'part_sha256':hashlib.sha256(raw).hexdigest(),'total_bytes':row['bytes'],'artifact_sha256':row['sha256']}
 directory=RESULTS/job;directory.mkdir(parents=True,exist_ok=True)
 if op=='result_status':
  p=safe_file(directory,req['name'])
  return {'bytes':p.stat().st_size if p.is_file() else 0,'finalized':safe_file(directory,req['name']+'.receipt.json').is_file()}
 if op=='result_part':
  p=safe_file(directory,req['name'])
  if p.suffix not in ['.json','.log','.txt','.npz']:raise ValueError('Unsupported result type')
  raw=base64.b64decode(req['data'],validate=True);offset=req['offset']
  if type(offset)!=int or offset<0 or len(raw)>MAX_CHUNK or offset+len(raw)>256*1024*1024:raise ValueError('Invalid result part')
  if hashlib.sha256(raw).hexdigest()!=req['part_sha256']:raise ValueError('Result part hash mismatch')
  size=p.stat().st_size if p.exists() else 0
  if offset<size:
   with p.open('rb') as f:f.seek(offset);existing=f.read(len(raw))
   if existing!=raw:raise ValueError('Result retry differs')
  elif offset==size:
   with p.open('ab') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  else:raise ValueError('Noncontiguous result')
  return {'bytes':p.stat().st_size}
 if op=='finalize_result':
  p=safe_file(directory,req['name'])
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if p.stat().st_size!=req['bytes'] or digest!=req['sha256']:raise ValueError('Final result hash mismatch')
  proof={'job_id':job,'name':p.name,'bytes':p.stat().st_size,'sha256':digest,'source_checkpoint_sha256':d['artifacts']['checkpoint']['sha256'],'plan_sha256':d['plan_sha256']}
  receipt=safe_file(directory,p.name+'.receipt.json')
  if receipt.is_file() and json.loads(receipt.read_text())!=proof:raise ValueError('Finalized receipt differs')
  atomic(receipt,proof);return proof
 raise ValueError('Operation not permitted')
def main():
 try:
  raw=sys.stdin.buffer.readline(600000)
  if len(raw)>=600000:raise ValueError('Request too large')
  response={'ok':True,'result':handle(json.loads(raw))}
 except Exception as e:response={'ok':False,'error':type(e).__name__+': '+str(e)}
 print(json.dumps(response));return 0 if response['ok'] else 1
if __name__=='__main__':sys.exit(main())
