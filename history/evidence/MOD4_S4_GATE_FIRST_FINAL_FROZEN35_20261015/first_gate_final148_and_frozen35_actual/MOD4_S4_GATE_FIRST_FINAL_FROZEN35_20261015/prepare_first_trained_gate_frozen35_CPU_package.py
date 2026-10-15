"""New frozen namespace only; original physics and cached-feedback loop reused."""
from pathlib import Path
import ast, copy, hashlib, json, os, shutil, sys, time, zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports'
OLD=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015/payload'
L=W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015'
ROOT='D:/MOD4_async_eval/'+D.name
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    final=json.loads((L/'reports/S4_FIRST_GATE_OWN_FINAL_WHOLE_LOCAL_CPU_VERIFIED.json').read_bytes())
    trace=json.loads((L/'reports/S4_FIRST_GATE_CLOSED_ALL_RAW_CPU_VERIFIED.json').read_bytes())
    assert final['passed'] and trace['passed'] and final['updates']==trace['updates']==148
    R.mkdir(exist_ok=True);assert not Q.exists();shutil.copytree(OLD,Q)
    pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes())
    for row in pair['sources']:row['local_path']=ROOT+'/payload/source/'+Path(row['local_path']).name
    pair.update(mode='gate_eval',no_gate_learning=True,trained_gate_source_explicit=True,no_rule_command_override=True,
        no_new_training_or_scope_expansion=True)
    (Q/'S4_PAIR_SOURCE_MANIFEST.json').write_text(json.dumps(pair,indent=2),encoding='utf8')
    src=Path(final['own_save']['local_path']);assert H(src)==trace['own_final_SHA']
    shutil.copy2(src,Q/'source/S4_gate_first_final.pt')
    gate=dict(local_path=ROOT+'/payload/source/S4_gate_first_final.pt',sha256=H(src),bytes=src.stat().st_size,
        training_updates=148,training_controls=3552,independent_final_CPU_SHA=H(L/'reports/S4_FIRST_GATE_OWN_FINAL_WHOLE_LOCAL_CPU_VERIFIED.json'),
        independent_all_raw_CPU_SHA=H(L/'reports/S4_FIRST_GATE_CLOSED_ALL_RAW_CPU_VERIFIED.json'))
    (Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').write_text(json.dumps(gate,indent=2),encoding='utf8')
    shutil.copy2(D/'s4_eval_trained_gate_source_v1.py',Q/'s4_eval_trained_gate_source_v1.py')
    adapter=(Q/'s4_transition_rule_adapter_v1.py').read_text(encoding='utf8')
    adapter=adapter.replace('from s4_shared_feedback_hardtop1_v1 import PairRouter,sha','from s4_shared_feedback_hardtop1_v1 import PairRouter,sha\nfrom s4_eval_trained_gate_source_v1 import load_trained_gate')
    adapter=adapter.replace('router=PairRouter(refs,vec.num_envs,device)',"router=PairRouter(refs,vec.num_envs,device)\n gate_manifest=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())\n gate_proof=load_trained_gate(router,gate_manifest)")
    adapter=adapter.replace("'rule_eval'","'gate_eval'")
    adapter=adapter.replace('new_gate_critic_optimizer_fixture_present_untrained_unused_for_rule=True','trained_gate6_loaded_critic_fixture_unused_for_frozen_eval=True,gate_source=gate_manifest,gate_proof=gate_proof')
    adapter=adapter.replace("checkpoint_sha256=refs[1]['sha256']","checkpoint_sha256=gate_manifest['sha256']")
    adapter=adapter.replace('rule_only_command_from_shared35=True','rule_only_command_from_shared35=False,deterministic_trained_gate=True,gate_source=gate_manifest,gate_proof=gate_proof')
    adapter=adapter.replace('new_fixture_not_trained_gate=True','new_fixture_not_trained_gate=False')
    adapter=adapter.replace('full_training_DR_CPUCUDA_restore_pending=True','full_training_DR_restore_not_claimed_by_frozen_actor_eval=True')
    compile(adapter,'s4_transition_learned_adapter_v1.py','exec');(Q/'s4_transition_learned_adapter_v1.py').write_text(adapter,encoding='utf8')
    runtime=(Q/'full80_runtime_native_v1.py').read_text(encoding='utf8')
    new=runtime.replace('from s4_transition_rule_adapter_v1 import build_route_pair','from s4_transition_learned_adapter_v1 import build_route_pair')
    new=new.replace('new_gate_critic_fixture_unused_for_rule=True','trained_gate6_source_exact_critic_fixture_unused=True')
    assert ast.dump(ast.parse(new.replace('from s4_transition_learned_adapter_v1 import build_route_pair','from s4_transition_rule_adapter_v1 import build_route_pair').replace('trained_gate6_source_exact_critic_fixture_unused=True','new_gate_critic_fixture_unused_for_rule=True')))==ast.dump(ast.parse(runtime))
    (Q/'full80_runtime_native_v1.py').write_text(new,encoding='utf8')
    worker=(Q/'paired_full80_parameter_bound_v2.py').read_text(encoding='utf8')
    worker=worker.replace('MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015',D.name)
    (Q/'paired_full80_parameter_bound_v2.py').write_text(worker,encoding='utf8')
    # Actual whole final and common saved observations, zero optimizer steps.
    sys.path[:0]=[str(Q),str(D)]
    from s4_shared_feedback_hardtop1_v1 import PairRouter
    from s4_eval_trained_gate_source_v1 import load_trained_gate,validate_state
    local_refs=copy.deepcopy(pair['sources'])
    for row in local_refs:row['local_path']=str(Q/'source'/Path(row['local_path']).name)
    cpu=torch.get_rng_state().clone();router=PairRouter(local_refs,40,'cpu')
    local_gate=dict(gate,local_path=str(Q/'source/S4_gate_first_final.pt'));proof=load_trained_gate(router,local_gate)
    ck=torch.load(src,map_location='cpu',weights_only=False)
    x=ck['S4_shared_control_state']['cache']['policy'][:40].clone();router.last_action=x[:,22:28].clone()
    decision=router.decide(0,lambda:x,'gate_eval');s=ck['actor_state_dict']
    logits=F.linear(F.elu(F.linear(F.elu(F.linear(x,s['gate.w1'],s['gate.b1'])),s['gate.w2'],s['gate.b2'])),s['gate.w3'],s['gate.b3'])
    assert torch.equal(logits,decision['logits']) and torch.equal(logits.argmax(-1),decision['z'])
    assert torch.equal(decision['raw_action'],decision['expert_means'][torch.arange(40),decision['z']])
    assert torch.equal(decision['raw_action'].clamp(-6,6),decision['clipped_action'])
    negatives=[]
    for name,modify in [('wrong_first_source',lambda c:c.update(S4_first_formal_source_SHA='0'*64)),
        ('untrained_flag',lambda c:c.update(S4_GPU_learning_admitted=False)),
        ('wrong_controls',lambda c:c.update(S4_shared_control_state=dict(c['S4_shared_control_state'],completed_controls=0))),
        ('changed_expert',lambda c:c.update(actor_state_dict=dict(c['actor_state_dict'],**{'experts.0.frozen_1':c['actor_state_dict']['experts.0.frozen_1']+1}))),
        ('changed_STD',lambda c:c.update(actor_state_dict=dict(c['actor_state_dict'],frozen_std=c['actor_state_dict']['frozen_std']+1)))]:
        bad=dict(ck);modify(bad)
        try:validate_state(bad,router)
        except AssertionError:negatives.append(name)
        else:raise AssertionError(name)
    assert torch.equal(cpu,torch.get_rng_state()) and not torch.cuda.is_initialized() and not router.optimizer.state
    m=dict(epoch=time.time(),source_SHA=pair['sources'][1]['sha256'],source_checkpoint_field_W35_scene_anchor_not_single_actor_policy=True,
        source_pair=pair['sources'],trained_gate=gate,no_PPO=True,training_DR_fullstate_restore_not_claimed=True,
        gate_fixture_untrained_and_critic_new_optimizer_unused_for_rule=False,
        S4_transition_scope=dict(only_source_pair=pair['sources'],geometry='original g3 35mm tenwaves and original flat supports',
            entry_approach_m=.4,after_margin_m=.2,seed=20260928,num_envs=80,route_steps_admitted=[120,1500],
            policy_rule_only=False,trained_deterministic_gate=True,new_eval_optimizer_steps=0,no_newgeometry_tensor_setter=True,
            no_RNG_or_extra_control_added=True),
        actual_linux_first_window_completed=True,independent_all_raw_CPU_SHA=gate['independent_all_raw_CPU_SHA'],
        original_rule_manifest_provenance=dict(path=str(OLD/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(OLD/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')))
    m['file_rows']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json']
    (Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
    z=D/'S4_FIRST_TRAINED_GATE_FROZEN35_V1.zip';assert not z.exists()
    with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for p in sorted(Q.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:archive.write(p,p.relative_to(Q).as_posix())
    report=dict(epoch=time.time(),prepared_CPU_only=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),
        manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),
        worker=dict(path=str(Q/'paired_full80_parameter_bound_v2.py'),sha256=H(Q/'paired_full80_parameter_bound_v2.py')),
        runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),
        source_pair=pair['sources'],trained_gate=gate,source_files=len(m['file_rows']),
        actual40_saved35_CPU_gate_logits_and_whole6_exact=True,negative_source_controls_expert_STD_cases=negatives,
        CPU_RNG_unchanged=True,no_CUDA_or_optimizer_steps=True,physical_main_AST_unchanged_after_declared_import_and_metadata=True,
        target_CPU_upload_native_and_full1500_not_yet_admitted=True,new_namespace=ROOT,
        old_native_and_full_rule_cases_not_replayed=True)
    (R/'FIRST_TRAINED_GATE_FROZEN35_PACKAGE_AND_CPU_MATH_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(prepared=True,packageSHA=H(z),source_files=len(m['file_rows']),new_GPU=False)))

if __name__=='__main__':main()
