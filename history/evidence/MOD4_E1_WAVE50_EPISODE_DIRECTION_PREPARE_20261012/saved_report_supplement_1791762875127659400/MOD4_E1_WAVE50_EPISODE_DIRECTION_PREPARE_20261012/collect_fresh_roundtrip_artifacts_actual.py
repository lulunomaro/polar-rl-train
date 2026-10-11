"""Index authentic completed fresh0PPO CUDA roundtrip artifacts; no restore calls."""
from wave_direction_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT_TOKEN);p=D/'reports/WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json';proof=json.loads(p.read_bytes());assert proof['passed'] and proof['actual_control_steps']==proof['actual_additional_PPO_updates']==0 and proof['direction']['predecessor_direction_state_restored_exact'] and not proof['direction']['explicit_new_episode_direction_scope']
files=[];names=[]
for p in sorted((D/'fresh_process_resume').glob('*')):
 if not p.is_file():continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 row=dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),original_retained=True)
 if p.suffix=='.pt':row['large_index_only']=True
 else:names.append(row)
 files.append(row)
print(json.dumps(dict(epoch=time.time(),passed=True,completed_fresh_zero_control_zero_PPO_actual_roundtrip_files=files,small_receipt_files=names,no_GPU_RNG_restore_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  folder=D/'fresh_completed_receipts'/str(time.time_ns());folder.mkdir(parents=True)
  with n.open_sftp() as f:
   for row in v['small_receipt_files']:
    raw=f.open(row['path'],'rb').read();assert H(raw)==row['sha256'];p=folder/Path(row['path']).name;p.write_bytes(raw);row['local_actual_saved_receipt']=str(p.resolve())
  report=save('FRESH_COMPLETED_ROUNDTRIP_ARTIFACTS_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(report),completed_roundtrip_artifacts=len(v['completed_fresh_zero_control_zero_PPO_actual_roundtrip_files']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FRESH_ARTIFACT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_restore_replay=True));raise
