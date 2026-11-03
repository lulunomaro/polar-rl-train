"""Sole local postround receiver. Remote original owner performs save/eval itself."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,time,traceback
N=Path(__file__).resolve().parent;A=N/'env20000_1h';R=A/'reports'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
spec=importlib.util.spec_from_file_location('scut_serial_postround',N/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.R=R
put=m.put;read=lambda p:json.loads(Path(p).read_bytes())


def bind():
    assert not (R/'POSTROUND_BIND_ONCE.json').exists()
    first=read(R/'FIRST_ACTUAL_RETURNED.json')['files']
    assert first['production/FIRST_UPDATED.json']['actual_onpolicy_samples']==480000
    put('POSTROUND_BIND_ONCE.json',dict(epoch=time.time(),sole_receiver=True,remote_owner_controls_close_eval=True))
    with(R/'POSTROUND_STDOUT.log').open('xb')as out,(R/'POSTROUND_STDERR.log').open('xb')as err:
        p=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'collect'],cwd=N,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query="Get-CimInstance Win32_Process -Filter \"ProcessId = "+str(p.pid)+"\" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json"
    row=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put('POSTROUND_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(row.stdout),sole_receiver=True))
    print(json.dumps(dict(bound=True,PID=p.pid)))


def collect():
    assert not (R/'POSTROUND_ONCE.json').exists()
    binding=read(R/'FIRST_ACTUAL_RETURNED.json')['files'];go=binding['GO_PRODUCTION.json'];job=read(A/'PLAN.json')['remote_root']
    put('POSTROUND_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),sameprocess_finite_receiver=True))
    # No SSH during healthy production. Original owner saves/exits/evaluates.
    while time.time()<go['save_deadline']+45:time.sleep(min(10,go['save_deadline']+45-time.time()))
    started=time.time()
    while any(r['ProcessId']!=os.getpid() for r in m.local_rows()):
        if time.time()-started>10800:raise RuntimeError('Local serial controller still active after3h')
        time.sleep(10)
    with m.connection('POSTROUND_RETURN')as(client,d):
        put('POSTROUND_FINITE_READ_ONCE.json',dict(epoch=time.time(),root=job,source_or_budget_mutations=0))
        for tick in range(90):
            code='''from pathlib import Path
import json,time,psutil
j=Path(v['job']);files={}
for rel in ['OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT.json','OWNER_ERROR.json','TRAIN_CLOSED.json','EVAL_IDENTITY.json','EVAL_WAITED.json','ROOT_ADMISSION_ACTUAL.json','GO_PRODUCTION.json','production/STARTUP.json','production/RESIZED_LEARNING_RESTORE.json','production/FIRST_UPDATED.json','production/LATEST_PROGRESS.json','production/FINAL.json','production/ERROR.json','production/APP_CLOSE_INTENT.json','evaluation/NATIVE_STARTUP.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json']:
 p=j/rel
 if p.is_file():
  try:files[rel]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
for rel in ['WORKER.log','EVAL.log','OWNER.log']:
 p=j/rel
 if p.is_file():
  with p.open('rb')as q:q.seek(max(0,p.stat().st_size-16000));files[rel]=q.read().decode('utf8','replace')
print(json.dumps(dict(epoch=time.time(),files=files)))'''
            returned=d.code(client,d.PY72,code,dict(job=job),timeout=40)
            if 'OWNER_EXIT.json'in returned['files']:break
            time.sleep(10)
        else:
            put('POSTROUND_ORIGINAL_NOT_RELEASED.json',returned)
            raise RuntimeError('Exact original owner still not released; no second operations')
        put('POSTROUND_FULL_RETURNED.json',returned)
        files=returned['files'];final=files.get('production/FINAL.json');evaluation=files.get('evaluation/RESULT.json')
        transfers=[];sf=client.open_sftp()
        try:
            models=[]
            if final:models.append(final['checkpoint'])
            if evaluation:models += [evaluation['all80_manifold'],evaluation['actual_poses']]
            for row in models:
                relative='models'if row['path'].endswith('.pt')else'evaluation'
                directory=A/relative;directory.mkdir(exist_ok=True)
                path=directory/Path(row['path']).name
                assert not path.exists()
                sf.get(row['path'],str(path))
                with path.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
                assert path.stat().st_size==row['bytes']and sha==row['SHA']
                transfers.append(dict(row,local_path=str(path),transfer_once=True,SHA_verified=True))
        finally:sf.close()
        put('POSTROUND_FORMAL_TRANSFERS.json',dict(epoch=time.time(),files=transfers,model_decodes=0,new_physics=0))
    put('POSTROUND_COMPLETED.json',dict(epoch=time.time(),actual_result=evaluation,final=final,
        native_visual_review_pending=True,next='View actual saved enhancedMOD4v1 poses; inspectall80 strict400Hz traces and decide next'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['bind','collect']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        put('POSTROUND_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
