from route_fixture_io import *

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import json,time,shutil,hashlib,subprocess
D=Path(ROOT_TOKEN);base=D.parent;h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();references={}
for name in (D.name,'MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012','MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012','MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'):
 p=base/name;files=[q for q in p.rglob('*') if q.is_file()];source=json.loads((p/'reports/SOURCE_FREEZE.json').read_bytes());passed=[]
 for q in (p/'reports').glob('*observation_PASSED.json'):
  a=json.loads(q.read_bytes());passed.append(dict(path=str(q),bytes=q.stat().st_size,sha256=h(q),source_count=a['source_count'],own_checkpoint=a['checkpoint'],actual_updates=a['actual_updates'],control_steps=a['health']['control_steps'],unique_segment=a['unique_completed_segment'],discarded_preflight=a['discarded_preflight']))
 references[name]=dict(path=str(p),wholeoutput_bytes=sum(q.stat().st_size for q in files),wholeoutput_file_count=len(files),actual_source_count=len(source['sha256']),durable_free_bytes=shutil.disk_usage(p).free,own_formal_passed_reports=passed)
mounts=subprocess.run(['df','-T','-B1'],capture_output=True,text=True,check=True).stdout
print(json.dumps(dict(epoch=time.time(),references=references,filesystems=mounts,resources_only_no_GPU_or_training_budget_write=True,no_evidence_cache_environment_deletion_or_tmpfs=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
        p=save('ROUTE443_COMPLETED_DURABLE_RESOURCES_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),references={k:dict(wholeoutput_bytes=a['wholeoutput_bytes'],durable_free_bytes=a['durable_free_bytes']) for k,a in v['references'].items()})))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_DURABLE_RESOURCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
