"""StageONLY preparedpair source/assets/metadata; neverlaunchesowner,readsmodels,C,SDKorlocks. Canrunwhileforeignauthorityowneractive."""
from pathlib import Path
import argparse,json,sys,shlex,hashlib,ast,time
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
args=argparse.ArgumentParser();args.add_argument('--pair',required=True,type=int,choices=(2,3,4));a=args.parse_args();index=json.loads((D/('parent_source/GENERIC_PAIR4_LOCAL_PAYLOAD_INDEX_V2.json'if a.pair==4 else'parent_source/GENERIC_PAIR2_PAIR3_LOCAL_PAYLOAD_INDEX_V2.json')).read_bytes());g=next(x for x in index['groups']if x['pair']==a.pair);root=g['root'];payload=Path(g['local_payload']);assert root.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR');marker=D/('PAIR'+str(a.pair)+'_GENERIC_V2_NONPT_STAGE_ONCE.json');result=D/'reports'/('PAIR'+str(a.pair)+'_GENERIC_V2_NONPT_STAGE_RESULT.json');assert not marker.exists()and not result.exists();files=[]
for p in payload.rglob('*'):
 assert p.suffix.lower()not in{'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.partial'}
 if p.is_file():
  raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
  files.append(dict(path=str(p),relative=p.relative_to(payload).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
marker.write_text(json.dumps(dict(root=root,pair=a.pair,owner_must_not_be_launched=True,sourcefiles=files),indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();report=dict(kind='GENERIC_PAIR_NONPT_STAGE_ONLY_NO_OWNER_NO_MODELS',root=root,pair=a.pair,roles=g['roles'],owner_launched=False,selected_model_stat_hash_decode=0,SDK_GPU_GO_C_or_lock_operations=0)
def mkdir(p):
 try:s.stat(p)
 except FileNotFoundError:
  parent=p.rsplit('/',1)[0]
  if parent and parent!=p:mkdir(parent)
  s.mkdir(p)
try:
 try:s.stat(root);raise RuntimeError('UnusedremoteROOTrequired, do notoverwritepartialorconsumedroot')
 except FileNotFoundError:pass
 mkdir(root)
 for f in files:
  dest=root+'/'+f['relative'];mkdir(dest.rsplit('/',1)[0]);raw=Path(f['path']).read_bytes();assert len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA']
  with s.open(dest,'wx')as z:z.write(raw)
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/stage_generic_nonpt_roles_v2.py')+' '+shlex.quote(root);i,o,e=c.exec_command(cmd,timeout=300);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stdout=stdout,stderr=stderr,actual_stage_passed=rc==0);assert rc==0,(rc,stderr);report['actual_nonPT_stage']=json.loads(stdout)
 for name in('OWNER_PLAN.json','STAGE_COMPLETE.json'):
  with s.open(root+'/'+name,'rb')as z:raw=z.read()
  p=D/'reports'/('PAIR'+str(a.pair)+'_GENERIC_V2_'+name);assert not p.exists();p.write_bytes(raw)
finally:
 s.close();c.close();result.write_text(json.dumps(report,indent=2),encoding='utf-8');print(result);print(json.dumps(report,indent=2))
