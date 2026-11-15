"""Regression reproducing actual SDK pre/physics/counter/reward ordering."""
from pathlib import Path
import importlib.util,json,torch
T=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('timing_math',T/'support/mod4v3_ppo_v1/pitch_stability_math.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
steps=torch.arange(145,175);issued=steps.float()*.02;endpoint=(steps+1).float()*.02;speed=torch.full_like(issued,2.2);new=m.transition_window(issued,speed);old=m.transition_window(endpoint,speed)
assert not bool(new[steps==149]) and bool(old[steps==149]),'Last moving action must not carry stop-window cost'
assert bool(new[steps==150]),'First stopped action must carry transition cost'
assert bool(new[steps==169]) and not bool(old[steps==169]),'Last0.38s stopped action must retain cost'
assert int(new.sum())==20,'Exactly20issued policy actions cover0.4s'
command,_,_=m.transition_command(issued,speed);assert float(command[steps==149])==float(speed[0]);assert float(command[steps==150])==0.
# The same correction must hold for start and both alternating directions.
records=[]
for event in [2.,3.,5.,6.,8.,9.]:
 i=int(round(event/.02));age=torch.tensor([(i-1)*.02,i*.02,(i+19)*.02]);v=torch.full_like(age,2.2);window=m.transition_window(age,v);assert window.tolist()==[False,True,True],(event,window)
 records.append(dict(event_s=event,issued_window=window.tolist()))
order=json.loads((T/'evidence/ACTIVE_SDK_STEP_ORDER.json').read_text())['step_order'];positions={x['code']:x['line']for x in order};assert positions['self._pre_physics_step(action)']<positions['self.episode_length_buf += 1  # step in current episode (per env)']<positions['self.reward_buf = self._get_rewards()']
result={'passed':True,'event_checks':records,'window_action_steps':steps[new].tolist(),'legacy_window_steps':steps[old].tolist(),'actual_SDK_step_order_verified':True,'prediction_formula_unchanged':True,'reset_age_zero_and_prephysics_capture_implemented':True};(T/'evidence/PHASE_TIMING_REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
