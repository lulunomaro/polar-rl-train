from pathlib import Path
import subprocess,os,json,time
root=Path('/home/egde/rl_candidates/mod4v3_moe_route2_precheck_20261117_r1');plan=json.loads((root/'PLAN.json').read_text());assert not plan['PPO_training_authorized'] and plan['authorized_PPO_seconds']==0
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>16000,free
owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip().splitlines()
job=root/'route2_native_probe_r3';assert not job.exists();env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for d in ['cache/warp','tmp']:(root/d).mkdir(parents=True,exist_ok=True)
cmd=[plan['python'],'-B','-u','-m','mod4v3_ppo_v1.route2_native_probe','--plan',str(root/'PLAN.json'),'--mode','probe','--profile','rough_scut_v1','--num-envs','2048','--seconds','0','--job',str(job)]
with(root/'route2_native_probe_r3.log').open('xb',buffering=0)as out:child=subprocess.Popen(cmd,cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=out,start_new_session=True)
r=dict(epoch=time.time(),pid=child.pid,job=str(job),PPO_updates=0,optimizer_updates=0,training_authorized=False,other_GPU_owners_preserved=owners);(root/'PROBE_LAUNCH.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
