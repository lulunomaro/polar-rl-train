"""New213 source/schema and new E2 fields CPU purpose, no old fixture replay."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,sys,time,traceback

HERE=Path(__file__).resolve().parent;SRC=HERE/'source';R=HERE/'reports';T=HERE.parent
ID='NEW213_E2_CYCLE_FIELDS_AND_SAVED_EXPERT_SCHEMA_CPU_V1'
sys.path.insert(0,str(SRC))


def main():
    frozen=json.loads((R/'CPU213_PURPOSE_FROZEN.json').read_bytes())
    assert frozen['ID']==ID and frozen['envs']==5 and frozen['controls']==240
    for row in frozen['source_rows']:
        raw=Path(row['path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
    with (R/'CPU213_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(ID=ID,epoch=time.time()),f)
    groups=[]
    for path in SRC.glob('*.py'):compile(ast.parse(path.read_bytes(),filename=str(path)),str(path),'exec')
    groups.append('new_source_graph_syntax_without_SDK_or_old_fixture_import')
    checks=[]
    for expert,row in frozen['saved_CPU_proofs'].items():
        raw=Path(row['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
        p=json.loads(raw)
        for key in ('passed','whole_model_all_tensors_finite','actor9_critic8_STD6_original35_38',
                    'all17_Adam_and_original_nonLR_optimizer_settings',row['critical_D0_D7_key']):
            assert p[key] is True,(expert,key);checks.append(expert+':'+key)
        assert p['Adam_step']==row['Adam_step'] and p['stored_iteration']==row['stored_iteration']
        assert p['adaptive_LR']==row['LR'] and p['model']['SHA']==row['model_SHA']
        assert p['new_branch_skill_qualified'] is False and p['WM_transition_data_collection_executed'] is False
        checks.append(expert+':literal_model_Adam_iteration_LR_and_ungraduated_scope')
    groups.append('12_saved_CPU_proof_metadata_joins_no_model_read')
    import torch as t
    t.set_num_threads(1);assert not t.cuda.is_initialized()
    import e2_cycles213 as module
    class MemoryRows:
        def __init__(self,*args,**kwargs):self.rows=[]
        def append(self,row):self.rows.append(row)
        def finish(self):return dict(rows=len(self.rows),retention_limited=False,synthetic_memory_only=True)
    module.Rows213=MemoryRows
    book=module.E2Cycles213(t,5,'cpu',HERE)
    xy=t.zeros(5,2);heading=t.zeros(5)
    profile=t.tensor([8,9,9,9,9]);episode=t.zeros(5,dtype=t.long);uid=t.zeros(5,dtype=t.long)
    cmd_yaw=t.tensor([-4.,4.,4.,4.,4.]);actual_yaw=t.tensor([-4.,4.,4.,4.,2.])
    for control in range(240):
        if control==40:uid[1]+=1
        before=xy.clone();before_heading=heading.clone()
        command=t.stack((t.cos(heading),t.zeros(5),cmd_yaw),1)
        c=dict(key=profile.clone(),phase=0 if control<100 else 1,episode=episode.clone(),
            command_uid=uid.clone(),before_xy=before,heading=before_heading,direction=t.zeros(5),
            command=command,signed_yaw=cmd_yaw,reference_projection=t.cos(heading).square())
        book.begin(control,c,8*control)
        xy[:,0]+=.01;xy[2,1]+=.0016;heading+=actual_yaw*.02
        terminated=t.zeros(5,dtype=t.bool);timeout=t.zeros(5,dtype=t.bool)
        if control==78:terminated[3]=True
        after=dict(xy=xy.clone(),heading_delta=t.atan2(t.sin(heading-before_heading),t.cos(heading-before_heading)))
        book.observe(c,after,terminated,timeout,dict(closure=terminated.clone(),time_out=timeout),8*(control+1))
        if control==78:episode[3]+=1;uid[3]+=1
    report=book.finish();rows=book.writer.rows
    complete=[r for r in rows if r['complete_sampled_span']]
    get=lambda env:next(r for r in complete if r['env_id']==env)
    assert get(0)['original_complete_cycle_fact'] and get(0)['actual_signed_yaw_rad']<0
    assert get(2)['cross_speed_m_s']>.05 and not get(2)['original_complete_cycle_fact']
    assert get(3)['non_timeout_before_reset'] and not get(3)['valid_original_complete_skill_sample']
    assert get(4)['signed_yaw_error_rad_s']<-.2 and not get(4)['original_complete_cycle_fact']
    assert any(r['env_id']==1 and r['command_uid']==1 and r['first_control']==40 for r in complete)
    assert any(r['crossed_warmup_steady_boundary'] for r in complete)
    assert any(not r['complete_sampled_span'] and r['end_reason']=='window_end_partial' for r in rows)
    groups.append('new_E2_signed_cross_yaw_UID_terminal_phase_and_partial_fields_240x5_synthetic')
    negatives=[]
    for name in ('wrong_UID_dtype','clock_gap','wrong_end_clock','nonfinite_terminal'):
        b=module.E2Cycles213(t,5,'cpu',HERE);ctx={k:v.clone() if t.is_tensor(v) else v for k,v in c.items()}
        try:
            if name=='wrong_UID_dtype':ctx['command_uid']=ctx['command_uid'].float();b.begin(0,ctx,0)
            elif name=='clock_gap':b.last_physics_tick=8;b.begin(1,ctx,16)
            else:
                b.begin(0,ctx,0);a=dict(after)
                if name=='nonfinite_terminal':a['xy']=after['xy'].clone();a['xy'][0,0]=float('nan')
                b.observe(ctx,a,t.zeros(5,dtype=t.bool),t.zeros(5,dtype=t.bool),{},4 if name=='wrong_end_clock' else 8)
        except ValueError:negatives.append(name)
        else:raise AssertionError('Expected schema refusal '+name)
    assert not t.cuda.is_initialized()
    value=dict(ID=ID,passed=True,groups=groups,saved_proof_checks=checks,negative_refusals=negatives,
        synthetic_envs=5,synthetic_controls=240,synthetic_population_controls=1200,
        synthetic_complete_events=len(complete),synthetic_counts=report,
        original_model_raw_NPZ_USD_SDK_GPU_remote_reads=0,neural_updates=0,
        old189_190_208_V5_V14_fixtures_rerun=0,actual_E2_E3_skill_or_runtime_admitted=False,
        complete_SuperMimic_conversion=False,Git_pending_root=True)
    with (R/'CPU213_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(ID=ID,passed=True,groups=len(groups),metadata_checks=len(checks),negative_refusals=negatives,synthetic_complete_events=len(complete))))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('CPU213_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(ID=ID,error=traceback.format_exc(),robot_failure=False),f,indent=2)
        raise
