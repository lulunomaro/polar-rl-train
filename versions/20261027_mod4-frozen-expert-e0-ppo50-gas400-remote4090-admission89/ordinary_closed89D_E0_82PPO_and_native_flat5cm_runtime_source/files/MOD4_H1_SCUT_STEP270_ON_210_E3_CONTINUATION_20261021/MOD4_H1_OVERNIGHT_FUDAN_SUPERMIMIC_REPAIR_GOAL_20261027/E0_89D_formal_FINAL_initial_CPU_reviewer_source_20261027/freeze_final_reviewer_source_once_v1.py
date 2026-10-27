"""Small immutable source index; no PT, SDK, torch, remote, GPU or ledger access."""
from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not (HERE/'INDEX.json').exists()
 p=HERE/'review_NEW_E0_89D_formal_FINAL_initial_CPU_once_v1.py';current=p.read_text('utf8')
 new=""" parameter_shapes=[x.shape for name in ('actor_state_dict','critic_state_dict') for x in ck[name].values()]
 for key,shape in zip(group['params'],parameter_shapes):
  state=opt['state'][key]
  assert set(state)=={'step','exp_avg','exp_avg_sq'} and state['exp_avg'].shape==state['exp_avg_sq'].shape==shape
 for key in meta:
  if key.endswith('_resume_contract'):assert ck[key]==meta[key],key"""
 old=""" for state in opt['state'].values():
  assert set(state)=={'step','exp_avg','exp_avg_sq'} and state['exp_avg'].shape==state['exp_avg_sq'].shape"""
 extra=""" assert ck['sensor_recipe']['raw_pre_scale_uniform_bounds']==dict(base_ang_vel=.125,projected_gravity=.025,leg_pos=.005,leg_vel=.25,wheel_vel=.5)
 assert ck['sensor_recipe']['raw_units']==dict(base_ang_vel='rad/s',projected_gravity='dimensionless',leg_pos='rad',leg_vel='rad/s',wheel_vel='rad/s')
 assert ck['sensor_recipe']['noise_draw_counts']==s['draw_counts'] and ck['sensor_recipe']['max_abs_actual_bias_rad']==float(s['bias'].abs().max())
 assert ck['feedback_delay_recipe']['actor_feedback_channels']==list(channels)
"""
 assert current.count(new)==current.count(extra)==1;tested=current.replace(new,old,1).replace(extra,'',1)
 assert hashlib.sha256(tested.encode()).hexdigest()=='0b83761e9fb41b57c572c3aa75d462002b20a7565847352cd786b243bda4b855'
 snapshot=HERE/'TINY_SCHEMA_TESTED_REVIEWER_SOURCE_V1.py.txt';snapshot.write_bytes(tested.encode())
 def gate(s):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='closure_gate'),include_attributes=False)
 assert gate(tested)==gate(current)
 for src in HERE.glob('*.py'):ast.parse(src.read_bytes())
 emit('FINAL_SOURCE_STRENGTHENING_AST_ONLY_PROOF_ACTUAL.json',dict(epoch=time.time(),passed=True,
  tested_reviewer_SHA=H(snapshot),final_reviewer_SHA=H(p),inverse_exact_tested_bytes=True,closure_gate_AST_unchanged=True,
  scope='Adam state shape and saved complete sensor recipe/save facts, no extra physical gate',all_Python_AST_passed=True,
  no_fixture_rerun_no_PT_or_torch_or_Actor_SDK_GPU_remote_or_ledger_access=True,actual_NEW_model_initial_CPU_review_pending=True))
 files=[dict(relative=x.relative_to(HERE).as_posix(),bytes=x.stat().st_size,SHA=H(x)) for x in sorted(HERE.rglob('*')) if x.is_file()]
 emit('INDEX.json',dict(schema='mod4.E0.89D.new_formal_FINAL.initialCPU.reviewer.frozen_source.v1',epoch=time.time(),files=files,
  reviewer=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),source_frozen=True,actual_NEW_model_review_pending=True,
  no_PT_input_or_final_normal86_Actor_SDK_GPU_remote_or_ledger_read=True,Git_status='ordinary_supplement_existing89trial_pending_root'))
 print(json.dumps(dict(index=str(HERE/'INDEX.json'),index_SHA=H(HERE/'INDEX.json'),reviewer_SHA=H(p),files=len(files),source_only=True)))
if __name__=='__main__':main()
