from pathlib import Path
import json,sys,hashlib,shlex,time,errno
ROOT=Path(r'D:\claude2\fangzhen')
sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
TRIAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112'
PLAN=json.loads((TRIAL/'PLAN.json').read_text(encoding='utf-8'))
REMOTE=PLAN['support'].rsplit('/support',1)[0]
def write(name,value):(TRIAL/'evidence'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(c,cmd):
    i,o,e=c.exec_command(cmd,timeout=60)
    out=o.read().decode('utf-8',errors='replace');err=e.read().decode('utf-8',errors='replace');status=o.channel.recv_exit_status()
    if out:print(out,flush=True)
    if err:print(err,flush=True)
    if status:raise RuntimeError('Remote command exit '+str(status))
    return out
act=sys.argv[1]
c=connect()
try:
    if act=='upload':
        s=c.open_sftp();created=set()
        def mkdir(path):
            if path in created:return
            try:s.stat(path)
            except FileNotFoundError:
                parent=path.rsplit('/',1)[0]
                if parent:mkdir(parent)
                s.mkdir(path)
            created.add(path)
        mkdir(REMOTE)
        manifest={}
        paths=[TRIAL/'PLAN.json',TRIAL/'launch.py']+sorted(p for p in (TRIAL/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.partial'))
        for p in paths:
            rel=p.relative_to(TRIAL).as_posix();dest=REMOTE+'/'+rel;mkdir(dest.rsplit('/',1)[0]);s.put(str(p),dest);manifest[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
        for name in ('tmp','cache/warp'):
            mkdir(PLAN['root']+'/'+name)
        write('UPLOADED_MANIFEST.json',manifest)
        code='import hashlib,json,pathlib; base=pathlib.Path('+repr(REMOTE)+'); expected='+repr(manifest)+'; actual={k:hashlib.sha256((base/k).read_bytes()).hexdigest() for k in expected}; assert actual==expected; p=pathlib.Path('+repr(PLAN['parent'])+'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(PLAN['parent_sha256'])+'; print(json.dumps(dict(upload_files=len(actual),all_source_hashes_match=True,parent_sha256=hashlib.sha256(p.read_bytes()).hexdigest())))'
        verify=json.loads(run(c,shlex.quote(PLAN['python'])+' -c '+shlex.quote(code)).strip())
        write('UPLOAD_VERIFIED.json',verify);s.close()
    elif act in ('smoke','train'):
        name='probe4096_stair_lift_r1' if act=='smoke' else PLAN['training_round']['job']
        args=[PLAN['python'],REMOTE+'/launch.py',name,'--kind','probe' if act=='smoke' else 'train','--num-envs','4096','--seconds','10' if act=='smoke' else '1200']
        receipt=json.loads(run(c,' '.join(shlex.quote(x) for x in args)).strip())
        write(act.upper()+'_LAUNCH.json',receipt)
    elif act=='status':
        s=c.open_sftp();name=sys.argv[2] if len(sys.argv)>2 else PLAN['training_round']['job'];job=REMOTE+'/'+name;out={}
        for filename in ('STARTUP.json','RESTORE.json','PPO_EFFECTIVE.json','TERRAIN_STARTUP.json','TERRAIN_RESTORED.json','LATEST_PROGRESS.json','FIRST_UPDATE.json','FINAL.json','ERROR.json','SAFE_CLOSED.json'):
            try:
                with s.open(job+'/'+filename,'rb') as f:value=json.loads(f.read().decode('utf-8'))
                write(name+'_'+filename,value)
                if filename in ('STARTUP.json','RESTORE.json','PPO_EFFECTIVE.json','LATEST_PROGRESS.json','FINAL.json','ERROR.json','SAFE_CLOSED.json'):out[filename]=value
            except FileNotFoundError:pass
        preview={}
        for name,value in out.items():
            if name=='STARTUP.json':
                preview[name]={k:value.get(k) for k in ('epoch','profile','num_envs','backend','physics_dt_s','control_dt_s','feedback_dt_s','DR','command_vx','command_wz','velocity_square_effective_coefficient','airborne_state_machine','air_reset_fraction')}
            elif name=='PPO_EFFECTIVE.json':
                preview[name]={k:value.get(k) for k in ('learning_rate','schedule','clip_param','num_learning_epochs','optimizer_lrs')}
            elif name=='LATEST_PROGRESS.json':
                preview[name]={k:value.get(k) for k in ('iteration','training_elapsed_seconds','mean_reward','losses','done_totals','numeric_peaks','forward_tracking','actor_drift_l2')}
            elif name=='FINAL.json':
                preview[name]={k:value.get(k) for k in ('epoch','elapsed_seconds','checkpoint','safe_close_requested')}
            else:preview[name]=value
        print(json.dumps(preview,ensure_ascii=False),flush=True);s.close()
        if not out:run(c,'tail -n 30 '+shlex.quote(REMOTE+'/'+name+'.log'))
    elif act=='gpu':run(c,'nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader')
finally:c.close()
