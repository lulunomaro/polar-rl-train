"""Read final reports and actual indices only; preserve remote originals."""
from second50_io import *

def main():
 p=max(R.glob('SECOND50_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));v=json.loads(p.read_bytes());assert v['passed'] and v['closeout_ready'] and v['actual_source_count']==386
 n,w=io.connect_both()
 try:
  folder=D/('own_final_actual_'+str(time.time_ns()));folder.mkdir();indices=[]
  with n.open_sftp() as f:
   for remote,local in ((ROOT+'/reports',folder/'root_reports'),(v['own']['run'],folder/'own_run')):
    local.mkdir()
    for a in f.listdir_attr(remote):
     if not a.filename.endswith(('.json','.log','.md')):continue
     source=remote+'/'+a.filename;raw=f.open(source,'rb').read();target=local/a.filename;target.write_bytes(raw);indices.append(dict(path=source,bytes=len(raw),sha256=H(raw),local_path=str(target)))
   manifest=json.loads((folder/'own_run/run_manifest.json').read_bytes());freeze=json.loads((folder/'own_run/rolling_source_freeze.json').read_bytes())['sha256']
   assert manifest['source_map']==freeze and len(freeze)==386 and manifest['init_checkpoint_sha256']==SOURCE_SHA
   for name,sha in manifest['src_sha256'].items():
    remote=v['own']['run']+'/src_snapshot/'+name;raw=f.open(remote,'rb').read();assert H(raw)==sha;target=folder/'actual_src_snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);indices.append(dict(path=remote,bytes=len(raw),sha256=sha,local_path=str(target)))
   ck=v['own_checkpoint'];indices.append(dict(path=ck['path'],bytes=f.stat(ck['path']).st_size,sha256=ck['sha256'],large_original_index_only=True,original_retained=True))
   for name in ('controller.log','guardian.log'):
    source=ROOT+'/'+name;raw=f.open(source,'rb').read();(folder/name).write_bytes(raw);indices.append(dict(path=source,bytes=len(raw),sha256=H(raw),local_path=str(folder/name)))
  p=save('SECOND50_OWN_FINAL_ACTUAL_COLLECTION_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=True,own_CPU_proof=str(p),own_checkpoint=ck,actual_source_count=386,actual_snapshot_file_count=v['actual_snapshot_file_count'],indices=indices,all_actual_own_snapshot_and_reports_preserved=True,large_weights_only_actual_path_size_SHA=True,no_GPU_queue_budget_write=True))
  print(json.dumps(dict(report=str(p),files=len(indices),snapshot_count=v['actual_snapshot_file_count'],checkpoint_SHA=ck['sha256'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN_FINAL_COLLECTION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_budget_replay=True));raise
