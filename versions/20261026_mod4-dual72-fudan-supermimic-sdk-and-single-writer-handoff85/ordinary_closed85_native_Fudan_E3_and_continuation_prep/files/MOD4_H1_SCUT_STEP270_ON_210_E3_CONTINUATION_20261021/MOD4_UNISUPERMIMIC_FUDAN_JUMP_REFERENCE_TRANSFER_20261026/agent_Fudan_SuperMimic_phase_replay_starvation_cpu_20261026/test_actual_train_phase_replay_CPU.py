"""Real train/replay AST with tensor-only fake collect/update callbacks; no model."""
from pathlib import Path
import ast
import csv
import hashlib
import importlib.util
import json
import math
import sys
import time
import traceback
import types
from dataclasses import dataclass
from types import SimpleNamespace

import torch

P=Path(__file__).resolve().parent;J=P.parent
N=J.parent/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
B=N/'payloads/e2/source'


def pin(path):
    raw=path.read_bytes()
    return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def create(path,value):
    with path.open('x',encoding='utf8') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def main():
    attempt=P/('attempt_'+str(time.time_ns()));attempt.mkdir()
    snapshots=attempt/'source_at_attempt';snapshots.mkdir()
    paths=[Path(__file__),B/'learner_unused_not_read']
    for path in (Path(__file__),B/'supermimic_vendor_v2/learner.py',B/'supermimic_vendor_v2/replay.py',B/'h1_supermimic_bridge_v1.py'):
        (snapshots/path.name).write_bytes(path.read_bytes())
    tree=ast.parse((B/'supermimic_vendor_v2/learner.py').read_text('utf8'))
    config=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='SuperMimicConfig')
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='SuperMimicLearner')
    methods=[x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in ('train','lr_at','_mean')]
    tick=[1000.]
    def clock():tick[0]+=.001;return tick[0]
    class Logger:
        def __init__(self,*a,**kw):pass
        def __getattr__(self,name):return lambda *a,**kw:None
    fields=ast.literal_eval(next(x.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='_LOG_FIELDS' for y in x.targets)))
    scope=dict(dataclass=dataclass,torch=torch,Path=Path,time=SimpleNamespace(time=clock),math=math,SuperMimicLogger=Logger,_LOG_FIELDS=fields,_empty_stats=lambda:dict(r=[],ep_len=[],ep_ret=[],term=[],done=[]))
    exec(compile(ast.Module(body=[config,*methods],type_ignores=[]),'<actual_train_AST_callbacks_no_model>', 'exec'),scope)
    bridge=ast.parse((B/'h1_supermimic_bridge_v1.py').read_text('utf8'))
    cfgassign=next(x for func in bridge.body if isinstance(func,ast.FunctionDef) and func.name=='run' for x in func.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='cfg' for y in x.targets))
    exec(compile(ast.Module(body=[cfgassign],type_ignores=[]),'<actual_installed_cfg_only>','exec'),scope)
    actual_cfg=scope['cfg']
    spec=importlib.util.spec_from_file_location('actual_ring_replay_no_model',B/'supermimic_vendor_v2/replay.py')
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)

    def run_case(start,iterations):
        # Only iteration stopping bound/log backend are fixture-local. Schedule,
        #64-row ring,48 warmup,24rows/iter and10wm-only match exact source cfg.
        cfg=scope['SuperMimicConfig'](**vars(actual_cfg));cfg.iterations=start+iterations
        learner=SimpleNamespace(cfg=cfg,iteration=start,wall_time=0.,sim_steps=0,device=torch.device('cpu'),backend='SYNTHETIC_SOURCE_CONTROL_FLOW',env=SimpleNamespace(num_envs=2),buffer=replay.ReplayBuffer(cfg.buffer_steps,2,'cpu',num_joints=30,context_dim=49,action_dim=6),total_rows=0,collect_calls=[],Pi_records=[])
        learner.log_dir=attempt/('fresh' if start==0 else 'continuation68');learner.log_dir.mkdir()
        for name in ('opt_wm','opt_pi','opt_v'):setattr(learner,name,SimpleNamespace(param_groups=[dict(lr=cfg.lr)]))
        learner.lr_at=types.MethodType(scope['lr_at'],learner);learner._mean=scope['_mean']
        learner.train=types.MethodType(scope['train'],learner)
        def collect(count):
            learner.collect_calls.append(count)
            for _ in range(count):
                t=learner.total_rows
                ages=torch.tensor([t,t if t<200 else t-200],dtype=torch.long)
                row={name:torch.zeros_like(value[0]) for name,value in learner.buffer.data.items()}
                row['f']=ages;row['ep_step']=ages.to(torch.int32)
                if t==199:row['done'][1]=True
                learner.buffer.add(row);learner.total_rows+=1;learner.sim_steps+=2
        def wm():return torch.tensor(0.),torch.tensor(0.)
        def pi():
            ages=learner.buffer.data['f'][learner.buffer._row(torch.arange(learner.buffer.size))]
            request=(ages>=100)&(ages<180)
            learner.Pi_records.append(dict(native_iteration_after_update=learner.iteration+1,completed_control_rows=learner.total_rows,ring_ptr=learner.buffer.ptr,ring_size=learner.buffer.size,no_reset_env_min_f=int(ages[:,0].min()),no_reset_env_max_f=int(ages[:,0].max()),no_reset_jump_rows=int(request[:,0].sum()),reset_at200_env_min_f=int(ages[:,1].min()),reset_at200_env_max_f=int(ages[:,1].max()),reset_env_jump_rows=int(request[:,1].sum())))
            return tuple(torch.tensor(0.) for _ in range(5))
        learner.collect=collect;learner.wm_update=wm;learner.policy_update=pi
        learner.save=lambda *a,**kw:Path('SYNTHETIC_NO_PT')
        learner.train()
        return dict(start_native_iteration=start,collect_calls=learner.collect_calls,Pi_records=learner.Pi_records)

    fresh=run_case(0,11);continuation=run_case(68,9)
    first=fresh['Pi_records'][0]
    assert first['completed_control_rows']==312 and (first['no_reset_env_min_f'],first['no_reset_env_max_f'])==(248,311) and first['no_reset_jump_rows']==0
    assert first['reset_env_jump_rows']==12  # demonstrates limitation to no-reset path
    assert continuation['Pi_records'][0]['completed_control_rows']==72
    assert any(x['no_reset_jump_rows']>0 for x in continuation['Pi_records'])
    covered=[x for x in continuation['Pi_records'] if x['no_reset_jump_rows']>0]
    assert covered[0]['completed_control_rows']==120 and max(x['no_reset_jump_rows'] for x in covered)==64
    csv_path=N/'current_three_closed_text/e2/job0/production/native_supermimic/train_log.csv'
    actual=list(csv.DictReader(csv_path.open()))
    first_actual=next(x for x in actual if float(x['pi_gradnorm'])>0)
    assert int(first_actual['iteration'])==11 and int(first_actual['sim_steps'])==312*20000
    wm_path=J/'root_Fudan_SuperMimic_actual_WM_sensitivity_20261026/ACTUAL_SAVED_NATIVE85_WM_SENSITIVITY_AND_PHASE_CPU.json'
    actual_wm=json.loads(wm_path.read_bytes());age=actual_wm['actual_final_snapshot']
    assert age['age_after_request']==19722 and age['age']['median']==633
    report=dict(epoch=time.time(),passed=True,classification='REPRODUCED_POLICY_START_REPLAY_PHASE_MISALIGNMENT_FOR_NO_RESET_TRAJECTORIES',fresh85_schedule=fresh,continuation68_schedule=continuation,actual_first_Pi_csv=first_actual,actual_final_snapshot=dict(age=age['age'],age_before_request=age['age_before_request'],age_in_request=age['age_in_public_request_100_to179'],age_after_request=age['age_after_request'],after_request_fraction=19722/20000,scope=age['scope']),
        confirmed='initial no-reset jump age100..179 is overwritten before firstPi;64row uniform ring contains248..311 at actualfirst312controls',
        scope_limits=['Not all20000 trajectories are proven no-reset beforefirstPi. The reset-at200 fixture intentionally retains12requestrows.','Final98.61%age>=180 is a single snapshot, not whole-windowPi request-start exposure.','Median633 proves at least half final episodes have their most recent64rows afterrequest, but no historical replay was saved.','Real WMJ/taskJ nonzero from root diagnostic rules out blanket zero-J claim; local single-step task/reg comparison is not full policy-gradient ratio.'],
        minimal_fix='already prepared cumulative68 continuation with freshreplay48 yields firstPi72 and request-containing rings at120,144,168,... without repeating10wm-only; still uninstalled/noGO and requires explicit currentdiagnostic/sourceadmission',
        later_fix='phase-aware retained jump replay or phase-aligned initialpolicy schedule; test coverage/history/done semantics and effective sampling ratios before changingbuffer/reward/physics',
        source_pins=[pin(x) for x in (B/'supermimic_vendor_v2/learner.py',B/'supermimic_vendor_v2/replay.py',B/'h1_supermimic_bridge_v1.py',csv_path,wm_path)],
        no_PT_raw_NPZ_real_model_optimizer_training_environment_GPU_remote_Git_budget_or_GO=True)
    path=attempt/'ACTUAL_SOURCE_PHASE_REPLAY_STARVATION_CPU.json';create(path,report)
    print(json.dumps(dict(passed=True,report=str(path),fresh_first=first,continuation_coverage=covered)))


if __name__=='__main__':
    try:main()
    except BaseException:
        create(P/('ORIGINAL_CPU_FIXTURE_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),passed=False,error=traceback.format_exc(),source_only_toy_no_model=True))
        raise
