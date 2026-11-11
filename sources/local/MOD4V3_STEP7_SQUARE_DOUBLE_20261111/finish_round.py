"""Finish this authorized round with one frozen-weight paired PhysX evaluation."""
from pathlib import Path
import base64,hashlib,json,sys,time,traceback
ROOT=Path(r'D:\claude2\fangzhen')
sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
TRIAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111'
PLAN=json.loads((TRIAL/'PLAN.json').read_text(encoding='utf-8'))
REMOTE=PLAN['support'].rsplit('/support',1)[0]
EVIDENCE=TRIAL/'evidence'

def remote_exec(code):
    client=connect()
    try:
        command="python3 -c \"import base64;exec(base64.b64decode('"+base64.b64encode(code.encode()).decode()+"'))\""
        _,out,err=client.exec_command(command,timeout=45)
        text=out.read().decode('utf-8');error=err.read().decode('utf-8')
        status=out.channel.recv_exit_status()
        if status:raise RuntimeError('Remote final evaluation operation: '+error[-2500:])
        return json.loads(text)
    finally:client.close()

def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

while not (EVIDENCE/'training_round/MONITOR_COMPLETE.json').exists():
    if (EVIDENCE/'training_round/ERROR.json').exists():
        raise RuntimeError('Training reported ERROR; no paired evaluation launched')
    time.sleep(20)
final=json.loads((EVIDENCE/'training_round/FINAL.json').read_text(encoding='utf-8'))
closed=json.loads((EVIDENCE/'training_round/SAFE_CLOSED.json').read_text(encoding='utf-8'))
assert closed.get('scene_closed') and final['elapsed_seconds']>=2400
for minutes in range(5,41,5):
    check=json.loads((EVIDENCE/f'training_round/model_{minutes:03d}m_CHECK.json').read_text(encoding='utf-8'))
    assert check['checkpoint_sha_verified']
code=r"""from pathlib import Path
import json,subprocess,hashlib,time,os
base=Path(BASE);plan=json.loads((base/'PLAN.json').read_text());name='paired_final_r1'
assert not (base/name).exists() and not (base/(name+'.log')).exists(),'Evaluation output already exists'
for _ in range(12):
 r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
 if not r.stdout.strip():break
 time.sleep(5)
else:raise RuntimeError('GPU still occupied after normal training close')
models=json.loads((base/'FINAL_MODELS_TEMPLATE.json').read_text());raw_models=dict(models)
final=base/'train040m_square_double_r1/model_final.pt';last=base/'train040m_square_double_r1/model_040m.pt'
final_sha=hashlib.sha256(final.read_bytes()).hexdigest();last_sha=hashlib.sha256(last.read_bytes()).hexdigest()
if final_sha!=last_sha:models['remaining_final']=str(final)
raw_models['remaining_final']=str(final)
(base/'FINAL_PAIRED_MODELS.json').write_text(json.dumps(models,indent=2))
(base/'FINAL_PAIRED_MODELS_RAW.json').write_text(json.dumps(raw_models,indent=2))
assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
readback={label:{'path':path,'bytes':Path(path).stat().st_size,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()} for label,path in models.items()}
cmd=[plan['python'],'-B','-u',str(base/'checkpoint_remaining_replay.py'),'--plan',str(base/'PLAN.json'),'--out',str(base/name),'--support',plan['support'],'--version','step7_remaining_final_r1','--models',str(base/'FINAL_PAIRED_MODELS.json')]
env=dict(os.environ);root=Path(plan['root']);env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
with (base/(name+'.log')).open('xb',buffering=0) as log:
 child=subprocess.Popen(cmd,cwd=base/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
receipt={'epoch':time.time(),'pid':child.pid,'cmd':cmd,'models':readback,'final_alias':'remaining_040' if final_sha==last_sha else 'remaining_final','final_sha256':final_sha,'script_sha256':hashlib.sha256((base/'checkpoint_remaining_replay.py').read_bytes()).hexdigest()}
(base/(name+'_LAUNCH.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
""".replace('BASE',repr(REMOTE),1)
receipt=remote_exec(code);write(EVIDENCE/'paired_final_r1_LAUNCH.json',receipt)
print('PAIRED_EVAL_LAUNCHED '+json.dumps(receipt),flush=True)
seen=set()
while True:
    client=connect()
    try:
        sftp=client.open_sftp()
        for name in ['PROGRESS.json','RESULT.json','ERROR.json','SAFE_CLOSED.json','INITIAL_DR.json']:
            path=REMOTE+'/paired_final_r1/'+name
            try:sftp.stat(path)
            except FileNotFoundError:continue
            sftp.get(path,str(EVIDENCE/('paired_final_r1_'+name)));seen.add(name)
        for name in ['FINAL_PAIRED_MODELS.json','FINAL_PAIRED_MODELS_RAW.json','paired_final_r1.log','train040m_square_double_r1.log']:
            path=REMOTE+'/'+name
            try:sftp.stat(path)
            except FileNotFoundError:continue
            sftp.get(path,str(EVIDENCE/name))
        sftp.close()
    finally:client.close()
    if 'SAFE_CLOSED.json' in seen:
        if 'ERROR.json' in seen:raise RuntimeError((EVIDENCE/'paired_final_r1_ERROR.json').read_text(encoding='utf-8'))
        assert 'RESULT.json' in seen
        break
    time.sleep(15)
index=remote_exec(r"""from pathlib import Path
import json,hashlib
base=Path(BASE);paths=[base/'paired_final_r1/trajectory.npz',base/'train040m_square_double_r1/model_final.pt',base/'train040m_square_double_r1/model_040m.pt']
print(json.dumps({str(p.relative_to(base)):{'remote_path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'storage':('raw trajectory retained remotely with SHA index' if p.suffix=='.npz' else 'full PT downloaded and included in this round Git weight archive; alias exact duplicate bytes')} for p in paths}))
""".replace('BASE',repr(REMOTE),1))
write(EVIDENCE/'LARGE_ARTIFACTS_FINAL.json',index)
result=json.loads((EVIDENCE/'paired_final_r1_RESULT.json').read_text(encoding='utf-8'))
print('PAIRED_EVAL_COMPLETE '+json.dumps({'models':len(result['input_sha256']),'envs':result['num_envs'],'resets':sum(x['resets'] for x in result['rows']),'numerical':sum(x['reasons']['numerical'] for x in result['rows']),'rows':[{k:v for k,v in x.items() if k in ('model','variant','task','mean','passed','resets')} for x in result['rows'] if x['model'] in ('parent','remaining_040','remaining_final')]}),flush=True)
