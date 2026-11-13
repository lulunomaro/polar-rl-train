"""Launch one explicitly bounded native PPO contrast on its confirmed idle GPU."""
from pathlib import Path
import argparse
import json
import shlex
import sys

T=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--model',choices=['parent','teacher'],required=True);p.add_argument('--access-dir',required=True);a=p.parse_args()
sys.path.insert(0,a.access_dir)
from ssh72 import connect,execute
root='/home/lc01/Zonglin Li/zonglin2'
remote=root+'/tasks/MOD4V3_LOW_SPEED_RETRACTION_20261113_R1'
gpu=0 if a.model=='parent' else 1
uuid=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][gpu]
script='''from pathlib import Path
import json,os,subprocess,time
r=Path(REMOTE);model=MODEL;plan=json.loads((r/('PLAN_'+model+'.json')).read_text())
job=r/('train010m_'+model+'_r1');log=r/(job.name+'.log')
assert not job.exists() and not log.exists()
assert plan['training_round']['seconds']==600
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert UUID not in owners,'Selected GPU has another owner: '+owners
env=dict(os.environ,CUDA_VISIBLE_DEVICES=UUID,PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
cmd=[ROOT+'/run-python.sh','-u','-c',"import sys; sys.path.insert(0,"+repr(str(r/'support'))+"); from mod4v3_ppo_v1.continuous_stair_train import main; main()",'--plan',str(r/('PLAN_'+model+'.json')),'--profile','rough_scut_v1','--mode','train','--job',str(job),'--num-envs','2048','--seconds','600','--resume',plan['parent'],'--expected-parent-sha',plan['parent_sha256'],'--learning-rate','0.00003','--lr-schedule','fixed','--clip-param','0.1','--learning-epochs','3']
with log.open('xb',buffering=0) as f:child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,model=model,job=str(job),physical_gpu=GPU,uuid=UUID,target_training_seconds=600,checkpoint_every_seconds=300,aggregate_initial_target_seconds=1200,aggregate_user_ceiling_seconds=2400,cmd=cmd)
(r/('TRAIN_LAUNCH_'+model+'.json')).write_text(json.dumps(receipt,indent=2)+'\\n');print(json.dumps(receipt))
'''.replace('REMOTE',repr(remote)).replace('MODEL',repr(a.model)).replace('ROOT',repr(root)).replace('GPU',str(gpu)).replace('UUID',repr(uuid))
c=connect()
try:
    status,out,err=execute(c,'python3 -c '+shlex.quote(script),30)
    print(out,err)
    if status:raise RuntimeError('Training launch failed')
    receipt=json.loads(out)
    (T/'evidence'/('TRAIN_LAUNCH_'+a.model+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
finally:c.close()
