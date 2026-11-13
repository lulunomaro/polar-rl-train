"""Use an idle GPU1 for one no-optimizer teacher-data collection."""
import argparse
import json
from pathlib import Path
import shlex
import sys

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
args = parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan = json.loads((T/'PLAN_R3.json').read_bytes())
source = T/'support_r3/mod4v3_ppo_v1/collect_jump_demos.py'
script = '''
import json,os,subprocess,time
from pathlib import Path
r=Path(REMOTE);uuid='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
owners=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert uuid not in owners,'GPU1 has an active evaluation owner'
job=r/'teacher_demos_r2';log=r/'teacher_demos_r2.log'
assert not job.exists() and not log.exists()
env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
cmd=[PYTHON,'-u','-c','import sys;sys.path.insert(0,'+repr(str(r/'support_r3'))+');from mod4v3_ppo_v1.collect_jump_demos import main;main()','--plan',str(r/'PLAN_R3.json'),'--job',str(job),'--num-envs','128']
with log.open('xb',buffering=0) as stream:
    child=subprocess.Popen(cmd,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,start_new_session=True)
receipt=dict(epoch=time.time(),pid=child.pid,job=str(job),physical_gpu=1,optimizer_updates=0,cmd=cmd)
(r/'LAUNCH_teacher_demos_r2.json').write_text(json.dumps(receipt,indent=2)+'\\n')
print(json.dumps(receipt))
'''.replace('REMOTE',repr(plan['root'])).replace('PYTHON,',repr(plan['python'])+',')
client = connect()
try:
    sftp = client.open_sftp()
    remote_source = plan['support']+'/mod4v3_ppo_v1/collect_jump_demos.py'
    try:
        sftp.stat(remote_source)
    except FileNotFoundError:
        sftp.put(str(source),remote_source)
    sftp.close()
    status,out,err = execute(client,'python3 -c '+shlex.quote(script),30)
    print(out,err)
    assert status == 0
    (T/'evidence/LAUNCH_teacher_demos_r2.json').write_text(json.dumps(json.loads(out),indent=2)+'\n')
finally:
    client.close()
