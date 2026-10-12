"""Collect actual completed reference bytes, retaining initial/ineligible and reviewed scopes."""
from scut_wave_command_io import *

SCOPES=['scut_wave50_gate_compare_20261012','scut_wave50_gate_compare_detached_reviewed_20261012','scut_wave50_gate_compare_schema_reviewed_20261012','scut_wave50_gate_compare_ray_command_reviewed_20261012','scut_wave50_gate_compare_command_hook_reviewed_20261012']

def main():
    w=connect();indices=[];complete={};pending=[]
    try:
        with w.open_sftp() as f:
            for name in SCOPES:
                remote='D:/MOD4_async_eval/'+name;dest=D/'actual'/name;dest.mkdir(parents=True,exist_ok=True)
                try:rows=f.listdir_attr(remote)
                except FileNotFoundError:continue
                for x in rows:
                    if not x.filename.endswith(('.json','.log','.txt','.py')):continue
                    raw=f.open(remote+'/'+x.filename,'rb').read();p=dest/x.filename
                    if p.exists() and p.read_bytes()!=raw:p=dest/(p.stem+'_'+str(time.time_ns())+p.suffix)
                    if not p.exists():p.write_bytes(raw)
                    indices.append(dict(remote_path=remote+'/'+x.filename,local_path=str(p.resolve()),bytes=len(raw),sha256=H(raw),actual_byte_SHA_exact=True))
                try:models=f.listdir(remote+'/runs')
                except FileNotFoundError:models=[]
                for model in models:
                    folder=remote+'/runs/'+model;local=dest/'runs'/model;local.mkdir(parents=True,exist_ok=True)
                    try:result=json.loads(f.open(folder+'/RESULT.json','rb').read())
                    except FileNotFoundError:pending.append(dict(scope=name,model=model,actual_result_pending=True));continue
                    for x in f.listdir_attr(folder):
                        if not x.filename.endswith(('.json','.log','.txt','.npz')):continue
                        p=local/x.filename
                        if x.filename.endswith('.npz'):
                            row=next(a for a in result['all_saved_files'] if Path(a['path']).name==x.filename)
                            if not p.exists():
                                part=p.with_suffix(p.suffix+'.partial');f.get(folder+'/'+x.filename,str(part));assert part.stat().st_size==row['bytes'] and H(part.read_bytes())==row['sha256'];part.rename(p)
                            assert p.stat().st_size==row['bytes'] and H(p.read_bytes())==row['sha256'];digest=row['sha256'];size=row['bytes']
                        else:
                            raw=f.open(folder+'/'+x.filename,'rb').read()
                            if p.exists() and p.read_bytes()!=raw:p=local/(p.stem+'_'+str(time.time_ns())+p.suffix)
                            if not p.exists():p.write_bytes(raw)
                            digest=H(raw);size=len(raw)
                        indices.append(dict(remote_path=folder+'/'+x.filename,local_path=str(p.resolve()),bytes=size,sha256=digest,actual_byte_SHA_exact=True,large_original_index_only=x.filename.endswith('.npz')))
                    complete[name+'/'+model]=dict(result=result,local_folder=str(local),probe=json.loads((local/'probe.json').read_bytes()) if (local/'probe.json').exists() else None)
        p=save('SCUT_REFERENCE_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),all_saved_indices=indices,completed_cases=complete,pending=pending,latest_eligible_scope=SCOPES[-1],old_ineligible_scopes_not_relabelled=True,no_GPU_task_worker_or_budget_replay=True))
        print(json.dumps(dict(path=str(p),cases={k:dict(phase=x['result']['phase'],counts=(x['probe'] or {}).get('behavior_completion')) for k,x in complete.items()},pending=pending,files=len(indices))))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_COLLECTION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),partial_evidence_retained=True,no_GPU_replay=True));raise
