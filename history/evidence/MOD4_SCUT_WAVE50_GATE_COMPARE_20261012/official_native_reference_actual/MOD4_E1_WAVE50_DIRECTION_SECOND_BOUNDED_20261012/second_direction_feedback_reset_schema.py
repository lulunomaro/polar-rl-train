import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012'))
"""Original final feedback contract: ready rows delayed, final-reset rows warm up at age0."""
from wave_direction_io import *
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p

import numpy as np,zipfile
ARCHIVE=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011/wave50_worldmesh_scope/e1-g4-derived50mm-worldmesh-query-fullroute-frozen-v2.zip'
EXPECTED_ARCHIVE_SHA='cef44c0a8e48cd6c4a0ed63e3e93620a7cccba94d37431c0763525abc8ec65cb'

def inspect_probe(p):
 assert H(ARCHIVE.read_bytes())==EXPECTED_ARCHIVE_SHA
 with zipfile.ZipFile(ARCHIVE) as z:
  delay=z.read('runtime/isaac/mod4/feedback_delay_mild.py')
  runtime=z.read('runtime/isaac/mod4/feedback_delay_runtime.py')
  assert b"c['ready'][due]=~initial" in delay and b"c['ready'][ids]=False" in delay
  assert b'prev[initial]=x[due][initial]' in delay and b'warmup_uses_current_new_episode_sample=True' in delay
 paths=list((R/'cases').glob('*/'+p['full_route_raw']['name']));assert len(paths)==1
 raw=paths[0];assert H(raw.read_bytes())==p['full_route_raw']['sha256'] and raw.stat().st_size==p['full_route_raw']['bytes']
 with np.load(raw,allow_pickle=False) as z:
  last_reset=z['terminated'][-1]|z['truncated'][-1]
  resets=np.flatnonzero(last_reset).tolist()
  last_reasons={p['reason_names'][i]:np.flatnonzero(z['reasons'][-1,:,i]).tolist() for i in range(len(p['reason_names']))}
  assert np.array_equal(last_reset,z['reasons'][-1].any(-1))
 a=p['frozen_actor'];s=p['sensor_manager']
 assert a['variant']=='A0' and a['current_actor_dimension']==35 and a['actual_command_error']==0
 assert a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
 assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']<=2e-6
 assert s['tick']==p['steps']==1500 and p['feedback_recipe']['reset_warmup_actual_age_us']==0
 channels=s['actual_feedback_sample_apply'];assert set(channels)=={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'}
 audits={}
 for name,row in channels.items():
  assert row['control_period_us']==10000 and row['apply_tick']==1500 and row['warmup_uses_current_new_episode_sample']
  age=np.asarray(row['actual_age_us']);request=np.asarray(row['requested_delay_us']);sample=np.asarray(row['actual_sample_tick']);ready=np.asarray(row['warmup_valid'])
  assert age.shape==request.shape==sample.shape==ready.shape==(80,)
  assert np.array_equal(age,(1500-sample)*10000) and np.isin(age,[0,10000]).all() and np.isin(request,[0,10000]).all()
  assert np.array_equal(~ready,last_reset),('final_reset_only_warmup',name)
  assert np.array_equal(age[ready],request[ready])
  assert np.array_equal(age[~ready],np.zeros(len(resets))) and (sample[~ready]==1500).all()
  audits[name]=dict(warmup_false_envs=np.flatnonzero(~ready).tolist(),ready_age_equals_requested_exact=True,reset_warmup_age0_sample1500_exact=True)
 return dict(passed=True,actual_final_reset_envs=resets,actual_final_reset_reasons=last_reasons,channels=audits,source_archive_SHA=EXPECTED_ARCHIVE_SHA,
  original_feedback_delay_member_SHA=H(delay),original_feedback_runtime_member_SHA=H(runtime),raw_path=str(raw.resolve()),raw_bytes=raw.stat().st_size,raw_SHA=p['full_route_raw']['sha256'],
  original_feedback_manager_formula2e6_and_clock100Hz_tolerances_preserved=True,no_physics_health_ground_contact_COM_or_hardware_tolerance_change=True,
  old_all_warmup_true_reader_assertion_not_relabelled_pass=True,CPU_only_no_GPU_PPO_budget_or_evaluation_replay=True)

def recipe_manager(p):
 inspect_probe(p)

def main():
 path=max(R.glob('SECOND_DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));c=json.loads(path.read_bytes());assert not c['pending']
 p=next(x['probe'] for x in c['cases'].values() if 'full_route_raw' in x['probe']);result=inspect_probe(p);result['collection']=str(path)
 out=save('SECOND_DIRECTION_FINAL_FEEDBACK_RESET_SCHEMA_ACTUAL_REVIEW.json',result)
 print(json.dumps(dict(report=str(out),passed=True,final_reset_warmup_envs=result['actual_final_reset_envs'])))

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FINAL_FEEDBACK_SCHEMA_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_replay=True));raise
