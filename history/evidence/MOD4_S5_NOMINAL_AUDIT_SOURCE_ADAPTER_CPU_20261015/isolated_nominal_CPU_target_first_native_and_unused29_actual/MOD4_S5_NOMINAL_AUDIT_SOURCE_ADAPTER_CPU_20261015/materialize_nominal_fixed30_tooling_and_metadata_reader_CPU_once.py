"""New-unused nominal scope tooling, with explicit profile and metadata binding."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent
R=D/'reports'
M=D.parent/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v


def write(name,text):
    p=D/name;assert not p.exists();ast.parse(text,filename=str(p))
    with p.open('x',encoding='utf8') as f:f.write(text)


def convert(text):
    return text.replace(M.name,D.name).replace('whitev2','nominal').replace('WHITEV2','NOMINAL').replace('WhiteV2ABC','NominalIsolatedABC').replace('s5_wv2_s','s5_nominal_s').replace('white_v2','nominal')


def main():
    assert json.loads((R/'NOMINAL_COMPLETE_ABC_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
    outputs=[]
    names=['dispatch_whitev2_ABC_new_case_actual.py','collect_whitev2_ABC_actual_boundary.py',
           'review_whitev2_original_physical_and_metrics_CPU.py','review_whitev2_single_source_history_CPU.py',
           'review_whitev2_pair_routing_CPU.py','run_whitev2_ABC_fixed30_case_batch_once.py','launch_whitev2_ABC_fixed30_hidden_once.py']
    for oldname in names:
        newname=convert(oldname);old=(M/oldname).read_text(encoding='utf8');new=convert(old)
        new=new.replace('NOMINAL_ABC_CPU_PREPARED_ACTUAL.json','NOMINAL_COMPLETE_ISOLATED_ABC_CPU_PREPARED_ACTUAL.json')
        new=new.replace('NOMINAL_ABC_UPLOAD_TARGET_CPU_ACTUAL.json','NOMINAL_COMPLETE_ABC_UPLOAD_TARGET_CPU_ACTUAL.json')
        new=new.replace('nominal_not_dispatched=True','no_other_profile_or_oldcase_dispatched=True')
        if oldname.startswith('dispatch'):
            new=new.replace('checkpoint_argument_is_scene_anchor_not_single_actor=True',"checkpoint_argument_is_W35_scene_anchor=True,single_actor_source_when_modeA=a.mode=='single_eval'")
            marker="m=json.loads((P/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())"
            assert marker in new
            new=new.replace(marker,marker+"\nassert m['DR_profile']=='nominal' and m['isolated_runtime_root']=='frozen_shared/runtime'")
        if oldname.startswith('review_whitev2_original'):
            marker='def read(path):return json.loads(Path(path).read_bytes())'
            assert marker in new
            new=new.replace(marker,marker+'\nfrom audit_nominal_D0_and_retained_pressure_metadata_CPU import audit as audit_nominal_metadata')
            marker=' if S==1500:\n'
            assert marker in new
            new=new.replace(marker," out['nominal_D0_and_retained_pressure_metadata']=audit_nominal_metadata(p)\n"+marker,1)
        write(newname,new);outputs.append(dict(path=str(D/newname),sha256=H(D/newname),original=str(M/oldname),original_SHA=H(M/oldname)))
    # Test the extra read-only metadata gate on real audit-method CPU fixtures.
    v=load('nominal_fixture_source',D/'review_isolated_nominal_audit_source_and_negatives_CPU_actual.py')
    validator=load('nominal_independent_saved_metadata',D/'audit_nominal_D0_and_retained_pressure_metadata_CPU.py')
    rng=torch.get_rng_state().clone();fixtures=[]
    saved={k:os.environ.get(k) for k in ('RM_MILD_DR_PROFILE','RM_DR_OFF')}
    os.environ['RM_MILD_DR_PROFILE']='nominal';os.environ['RM_DR_OFF']='1'
    for n in (80,88):
        for seed in (20261002,20261003):
            env,_=v.fixture(n,seed,False);v.helper.capture_nominal_d0_reference(env)
            env._gas_damping.install_expected_value_auditors()
            rows=v.helper.parameter_audit(env)
            methods=v.methods(D/'isolated/factor_runtime_3060_reference17b_v1.py',['private_rng','json_tree','full_initial_queue_states','params'])
            params=methods['params'](env)
            p=dict(mild_initial_parameters=copy.deepcopy(rows),mild_final_parameters=copy.deepcopy(rows),native_readonly_witness=dict(
                DR_profile='nominal',fixture_envs=n,kind='flat',first_physics_initial=dict(physical_parameters=copy.deepcopy(params)),final_physical_parameters=copy.deepcopy(params)))
            assert validator.audit(p)['D0_nominal_initial_final_readback_exact']
            negatives=[]
            for name in ('wrong_profile','missing_D7','fake_MildDR','fake_RNG','mass_changed','inertia_nonfinite','motor_gain','D6_overlay_missing'):
                bad=copy.deepcopy(p);w=bad['native_readonly_witness'];last=w['final_physical_parameters']
                if name=='wrong_profile':w['DR_profile']='white_v2'
                elif name=='missing_D7':bad['mild_final_parameters']['independent_pressure_audits'].pop('D7_PD')
                elif name=='fake_MildDR':last['mild_factor']=[1.]*n
                elif name=='fake_RNG':last['actual_captured_RNG_bytes']['_mild_dr/generator']={}
                elif name=='mass_changed':last['mass'][0][0]+=.01
                elif name=='inertia_nonfinite':last['inertia'][0][0][0]=float('nan')
                elif name=='motor_gain':last['motors']['legs']['episode_scale'][0][0]=.99
                else:bad['mild_final_parameters']['independent_pressure_audits']['D5_spring']['D6_gas_damping_varies_separately']=False
                negatives.append(dict(case=name,**v.rejection(lambda:validator.audit(bad))))
            fixtures.append(dict(n=n,seed=seed,pass_original_actual_CPU_method_metadata=True,negative_cases=negatives,not_GPU=True))
    for key,value in saved.items():
        if value is None:os.environ.pop(key,None)
        else:os.environ[key]=value
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    value=dict(epoch=time.time(),CPU_only_no_GPU_transport=True,new_fixed30_scope_tooling_materialized=True,
               seed_profile_kind_source_backend_native_full_binding_kept=True,
               original_physical_numerical_gates_unchanged=True,extra_nominal_D0_vs_D7_saved_metadata_gate=True,
               files=outputs,actual_CPU_metadata_fixtures=fixtures,strict_metadata_negatives=32,
               global_CPU_RNG_unchanged=True,no_CUDA_optimizer_PPO_budget=True,
               no_dispatch_or_future_native_pass_claimed=True)
    with (R/'NOMINAL_FIXED30_TOOLING_AND_METADATA_READER_CPU_MATERIALIZED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(materialized=True,strict_metadata_negatives=32,new_GPU=False)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NOMINAL_TOOLING_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),no_GPU_network_PPO_budget=True,partial_new_local_tooling_preserved=True),f,indent=2)
        raise
