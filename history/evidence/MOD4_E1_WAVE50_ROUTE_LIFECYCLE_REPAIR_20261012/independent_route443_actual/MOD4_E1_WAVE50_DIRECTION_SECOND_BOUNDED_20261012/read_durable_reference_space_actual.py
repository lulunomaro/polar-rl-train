from wave_direction_second_io import *

def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,shutil,subprocess,hashlib
base=Path('/home/egde/rl_candidates');refs={}
for name in ('MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012','MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012','MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012','MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'):
 p=base/name;refs[name]=dict(path=str(p),wholeoutput_bytes=sum(q.stat().st_size for q in p.rglob('*') if q.is_file()),durable_free_bytes=shutil.disk_usage(p).free,source_selected=json.loads((p/'reports/SOURCE_SELECTED.json').read_bytes()))
mounts=subprocess.run(['df','-T','-B1'],capture_output=True,text=True,check=True).stdout
print(json.dumps(dict(epoch=time.time(),references=refs,filesystems=mounts,resources_only_no_training_or_budget_write=True)))
''')
  save('DURABLE_COMPLETED_PIPELINE_RESOURCE_REFERENCE_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DURABLE_REFERENCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
