"""Run isolated CPU counterfactuals against copied actual admission/stop code."""
from pathlib import Path
from types import SimpleNamespace
import ast,copy,json,math,sys,tempfile
import torch

D=Path(__file__).resolve().parent;R=D/'evidence';SRC=R/'current/source'
sys.path.insert(0,str(SRC/'isaac/mod4'));sys.path.insert(0,str(SRC))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
from clock_training_health import ClockTrainingHealth

tree=ast.parse((SRC/'supervise_sensor_parallel_continuation.py').read_text())
func=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='inspect_result')
cases=[]
def inspect(kind,raw):
    with tempfile.TemporaryDirectory(prefix='mod4_gate_audit_') as t:
        root=Path(t);job='isolated';folder=root/'eval_results'/job;folder.mkdir(parents=True)
        (folder/'probe.json').write_text(json.dumps(raw));result=json.loads((R/'returned'/kind/'result.json').read_text())
        (folder/'result.json').write_text(json.dumps(result));queue=root/'eval_queue';queue.mkdir()
        (queue/(job+'.json')).write_text((R/'returned'/kind/'job.json').read_text())
        s=SimpleNamespace(ER=root/'reports',q=SimpleNamespace(w=SimpleNamespace(read=lambda p:json.loads(p.read_text()))))
        ns=dict(s=s,evidence=evidence,target=target,math=math)
        exec(compile(ast.Module(body=[func],type_ignores=[]),'actual_current_inspect_result','exec'),ns)
        row=ns['inspect_result'](job)
        return {k:row[k] for k in ('status','kind','attention','reason','target_count','max_abs_cross','v4') if k in row}
def add(name,row):cases.append(dict(case=name,actual_code_outcome=row))
original={k:json.loads((R/'returned'/k/'probe.json').read_text()) for k in ('flat','spin','world')}
for kind in original:
    row=inspect(kind,original[kind]);assert row['v4']['pass_'] and not row['attention'];add('actual24827_'+kind,row)

r=copy.deepcopy(original['world']);r['world_cycle_metrics'][0]['complete_prefix_cross_m_s']=.050001
row=inspect('world',r);assert row['target_count']==63 and not row['attention'] and row['v4']['pass_'];add('one_finite_cross_boundary_residual_keeps_training',row)
r=copy.deepcopy(original['world'])
for x in r['world_cycle_metrics']:
    if abs(x['command_yaw_rad_s'])==2:x['complete_prefix_cross_m_s']=.2
row=inspect('world',r);assert row['attention'] and row['target_count']==16 and row['v4']['pass_'];add('all48_fast_direction_samples_lost_strict_target_requires_review',row)
r=copy.deepcopy(original['flat'])
for x in r['groups']:
    if x.get('profile')=='constant' and x['command_vx']==1.5:x['speed']=-1.
row=inspect('flat',r);assert row['attention'] and row['v4']['pass_'];add('whole_group_wrong_direction_requires_review',row)
r=copy.deepcopy(original['flat'])
for group_index,x in enumerate(r['groups']):
    if x.get('profile')=='constant' and x['command_vx']==1.5:
        x['speed']=1.15;x['vel_error']=.35
        for i,gid in enumerate(r['per_environment']['group_ids']):
            if gid==group_index:
                r['per_environment']['speed'][i]=1.15;r['per_environment']['vel_error'][i]=.35
row=inspect('flat',r);assert row['v4']['pass_'] and not row['attention'];add('positive_direction_but_systemic_straight_speed_loss_not_flagged',row)
r=copy.deepcopy(original['spin']);r['per_environment']['tilt']=[25.]*len(r['alive']);r['per_environment']['yaw_error']=[3.]*len(r['alive'])
row=inspect('spin',r);assert row['v4']['pass_'] and not row['attention'];add('finite_quality_diagnostics_do_not_veto',row)
r=copy.deepcopy(original['spin']);r['alive'][0]=False;r['first_failure_step'][0]=700
row=inspect('spin',r);assert row['attention'] and not row['v4']['pass_'];add('one_actual_task_failure_in_frozen_replay_blocks_admission',row)
r=copy.deepcopy(original['spin']);r['nonfinite']=True
row=inspect('spin',r);assert row['attention'] and not row['v4']['pass_'];add('nonfinite_still_refused',row)
r=copy.deepcopy(original['spin']);r['max_mimic_rad']=.02
row=inspect('spin',r);assert row['attention'] and not row['v4']['pass_'];add('mimic0p02_refused_by_review_even_though_task_threshold0p05',row)
r=copy.deepcopy(original['spin']);cp=r['substep_contact_readback']['per_environment'];cp['mean_normal_force_N'][0][0]+=1.
row=inspect('spin',r);assert row['attention'] and not row['v4']['pass_'];add('force_integrity_disagreement_refused',row)

class FakeEnv:
    def __init__(self,event):
        self.num_envs=20000;self.device='cpu';self.physics_dt=.001;self.step_dt=.01;self.event=event;self.counter=0
        self._integrated_contact=SimpleNamespace(tick=0);self.termination_manager=SimpleNamespace(terminated=torch.zeros(20000,dtype=torch.bool))
        self._mod4_max_closure=.0009;self._mod4_max_mimic=.0019
    def step(self,action):
        self.counter+=1;self._integrated_contact.tick+=10;self.termination_manager.terminated.zero_()
        if self.event and self.counter==9:self.termination_manager.terminated[0]=True
        return None
for name,event in (('timeout_only_not_in_task_terminated_mask',False),('one_ordinary_orientation_or_contact_task_event',True)):
    with tempfile.TemporaryDirectory(prefix='mod4_health_audit_') as t:
        env=FakeEnv(event);hook=ClockTrainingHealth(env,t)
        for _ in range(24):env.step(None)
        h=hook.write();stop=(Path(t)/'STOP_AFTER_SAVE').exists()
        assert stop==event and h['actual_task_reset_events']==int(event)
        add(name,dict(STOP_AFTER_SAVE_requested=stop,health=h,synthetic_CPU_counter_only=True,no_physical_health_test=True))

v=dict(passed=True,test_count=len(cases),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),copied_production_code_SHA_verified_by_COLLECTION=True,counterfactuals_only_no_actual_probe_or_training=True,cases=cases)
(R/'SHADOW_GATE_AUDIT.json').write_text(json.dumps(v,indent=2));print(json.dumps(dict(passed=True,test_count=len(cases),CUDA_initialized=v['CUDA_initialized'],summary=[dict(case=x['case'],attention=x['actual_code_outcome'].get('attention'),STOP_AFTER_SAVE=x['actual_code_outcome'].get('STOP_AFTER_SAVE_requested')) for x in cases])))
