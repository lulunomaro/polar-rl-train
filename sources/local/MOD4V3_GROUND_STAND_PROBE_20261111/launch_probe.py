from pathlib import Path
import json,sys,time,shlex
ROOT=Path('D:/claude2/fangzhen');OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tmp'));from step7_remote_access import connect
plan=json.loads((ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/PLAN.json').read_text(encoding='utf-8'))
remote=plan['root']+'/ground_stand_probe_20261111_r1';checkpoint=plan['support'].rsplit('/support',1)[0]+'/train040m_rough_r1_round2_r1/model_005m.pt'
c=connect();s=c.open_sftp()
try:s.mkdir(remote)
except IOError:raise RuntimeError('Remote probe directory exists; keep its evidence')
for name in ['physx_ground_stand.py','INITIAL_POSES.json']:s.put(str(OUT/name),remote+'/'+name)
with s.open(remote+'/PLAN.json','w') as f:f.write(json.dumps(plan))
# Launch only this finite evaluation and preserve the exit code. No training.
cmd=[plan['python'],'-B','-u',remote+'/physx_ground_stand.py','--plan',remote+'/PLAN.json','--poses',remote+'/INITIAL_POSES.json','--out',remote+'/test01','--checkpoint',checkpoint]
root=plan['root'];exports=dict(CUDA_VISIBLE_DEVICES='0',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=root+'/cache/warp',XDG_CACHE_HOME=root+'/cache',TMPDIR=root+'/tmp',TMP=root+'/tmp',TEMP=root+'/tmp')
wrapper='import subprocess,os,json,pathlib; e=dict(os.environ); e.update('+repr(exports)+'); p=subprocess.Popen('+repr(cmd)+',cwd='+repr(remote)+',env=e,stdin=subprocess.DEVNULL,stdout=open('+repr(remote+'/probe.log')+',"xb"),stderr=subprocess.STDOUT,start_new_session=True); print(json.dumps({"pid":p.pid}))'
_,stdout,stderr=c.exec_command(' '.join(map(shlex.quote,[plan['python'],'-B','-c',wrapper])),timeout=30);reply=stdout.read().decode();err=stderr.read().decode();print(reply,err)
receipt=dict(remote=remote,checkpoint=checkpoint,command=cmd,response=reply,launch_epoch=time.time());(OUT/'LAUNCH.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');s.close();c.close()
