"""Launch one bounded local PPO window using the original RSL framework."""
from pathlib import Path
import sys,os,json,runpy
T=Path(__file__).resolve().parent;p=json.loads((T/'TRAIN_PLAN.json').read_text());f=p['flat_speed_repair']
os.environ.update(FLAT_SPEED_LEG_PD_DECIMATION=str(f['leg_pd_decimation']),FLAT_SPEED_WHEEL_PD_DECIMATION=str(f['wheel_pd_decimation']),PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
sys.path.insert(0,str(T/'support'));sys.argv=['flat_speed_repair_train.py','--plan',str(T/'TRAIN_PLAN.json'),'--profile','flat_remaining_mixed_dr','--mode','train','--job',str(T/'training_round'),'--num-envs','512','--seconds','2400','--resume',p['parent'],'--expected-parent-sha',p['parent_sha256'],'--learning-rate','0.0001','--lr-schedule','fixed','--clip-param','0.1','--learning-epochs','3']
runpy.run_module('mod4v3_ppo_v1.flat_speed_repair_train',run_name='__main__')
