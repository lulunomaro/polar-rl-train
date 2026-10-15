from pathlib import Path
import hashlib,json,sys,time,traceback,shutil
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
def main():
 assert not (R/'ORIGINAL_ROBOT_CONFIG_ASSET_SUPPLEMENT_ACTUAL.json').exists()
 v=json.loads((R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').read_bytes());c=sf=None;rows=[]
 try:
  c=t.connect();sf=c.open_sftp();sf.get_channel().settimeout(60)
  for i,x in enumerate(v['original_snapshots']):
   q=D/'payload'/('job'+str(i))/'runtime/isaac/mod4'
   for name in ('import_contract.json','robot_cfg.py'):
    remote=str(Path(x['path']).parent).replace('\\','/')+'/src_snapshot/'+name
    expected=x['src_sha256'][name]
    with sf.open(remote,'rb') as f:b=f.read()
    assert hashlib.sha256(b).hexdigest()==expected
    p=q/name;assert not p.exists()
    with p.open('xb') as f:f.write(b)
    rows.append(dict(source=remote,target=str(p),bytes=len(b),sha256=expected))
   usd=D/'payload'/('job'+str(i))/'assets/robot.usd';p=q/'robot.usd';assert not p.exists();shutil.copyfile(usd,p)
   assert hashlib.sha256(p.read_bytes()).hexdigest()==x['metadata']['robot_usd_sha256']
  with (R/'ORIGINAL_ROBOT_CONFIG_ASSET_SUPPLEMENT_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),rows=rows,existing_USD_local_exact_reused=True,no_GPU_PPO_budget_or_source_mutation=True),f,indent=2)
  print(json.dumps(dict(exact_missing_original_config_files=len(rows),no_training=True)))
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ROBOT_CONFIG_ASSET_SUPPLEMENT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_blind_replay=True),f,indent=2)
  raise
