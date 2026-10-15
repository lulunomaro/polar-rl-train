"""Fresh limited S4 pair scopes; physical loops remain the original V8 bytes."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports'
OLD=W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/payload_v2'
GATE=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015'
ROOT='D:/MOD4_async_eval/'+D.name
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    R.mkdir(exist_ok=True)
    diagnostic=json.loads((R/'FIRST_GATE_FIXED_SOURCE_EXISTING_RAW35_RETENTION_RESPONSE_CPU_ACTUAL.json').read_bytes())
    assert diagnostic['passed_saved_input_CPU_math']
    direct=json.loads((GATE/'reports/S4_FIRST_TRAINED_GATE35_COMPLETE_DIRECT_RULE_PAIR_CPU_REVIEW.json').read_bytes())
    assert direct['passed_complete_pair_CPU_review'] and not Q.exists()
    shutil.copytree(OLD,Q)
    for name in ('s4_shared_feedback_hardtop1_v1.py','hard_top1_frozen_expert_CPU_component_v1.py','s4_eval_trained_gate_source_v1.py'):
        shutil.copy2(GATE/'payload'/name,Q/name)
    shutil.copy2(GATE/'payload/source/S4_gate_first_final.pt',Q/'source/S4_gate_first_final.pt')
    pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes())
    for row in pair['sources']:row['local_path']=ROOT+'/payload/source/'+Path(row['local_path']).name
    pair.update(mode='lease_bound_rule_eval_or_gate_eval',allowed_modes=['rule_eval','gate_eval'],no_gate_learning=True,
        first_stateless_native_flat120_only=False,full35_transition_route_and_gate_PPO_pending=False,
        full_supported_retention_pair_results_pending=True)
    (Q/'S4_PAIR_SOURCE_MANIFEST.json').write_text(json.dumps(pair,indent=2),encoding='utf8')
    gate=json.loads((GATE/'payload/S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
    gate['local_path']=ROOT+'/payload/source/S4_gate_first_final.pt'
    (Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').write_text(json.dumps(gate,indent=2),encoding='utf8')
    adapter=(OLD/'s4_native_pair_adapter_v3_metadata_explicit.py').read_text(encoding='utf8')
    adapter=adapter.replace('from s4_shared_feedback_hardtop1_v1 import PairRouter,sha',
        'from s4_shared_feedback_hardtop1_v1 import PairRouter,sha\nfrom s4_eval_trained_gate_source_v1 import load_trained_gate')
    adapter=adapter.replace(" assert manifest['mode']=='rule_eval' and manifest['no_gate_learning'] and Path(refs[1]['local_path']).resolve()==Path(anchor_path).resolve()",
        " mode=CONTEXT['router_mode'];assert mode in ('rule_eval','gate_eval') and manifest['mode']=='lease_bound_rule_eval_or_gate_eval' and manifest['no_gate_learning'] and Path(refs[1]['local_path']).resolve()==Path(anchor_path).resolve()")
    adapter=adapter.replace(' router=PairRouter(refs,vec.num_envs,device)',
        " router=PairRouter(refs,vec.num_envs,device)\n gate_manifest=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())\n gate_proof=load_trained_gate(router,gate_manifest)\n gate_exact={k:v.detach().cpu().clone() for k,v in router.gate.state_dict().items()}")
    adapter=adapter.replace("lambda:original_get()['policy'],'rule_eval'", "lambda:original_get()['policy'],mode")
    adapter=adapter.replace('gate_fixture_deterministic_untrained=True,rule_baseline_normal_command_only=True',
        "gate_fixture_deterministic_untrained=False,rule_baseline_normal_command_only=mode=='rule_eval',router_mode=mode,gate_source=gate_manifest,gate_proof=gate_proof")
    adapter=adapter.replace('new_gate_and_E0_initialized_critic_fixture_constructed_but_unused_for_rule_selection=True',
        "trained_gate6_loaded_in_both_modes_critic_fixture_unused=True")
    adapter=adapter.replace('   report=dict(profile=',
        "   assert all(torch.equal(v.detach().cpu(),gate_exact[k]) for k,v in router.gate.state_dict().items())\n   CONTEXT['save']('S4_GATE_INITIAL_FINAL_TENSORS_EXACT.json',dict(source_SHA=gate_manifest['sha256'],all6_initial_final_source_exact=True,router_mode=mode,no_PPO=True))\n   report=dict(profile=")
    adapter=adapter.replace('rule_reads_only_normal_commands_from_shared35=True', "rule_reads_only_normal_commands_from_shared35=mode=='rule_eval',router_mode=mode,gate_source=gate_manifest,all6_gate_initial_final_source_exact=True")
    adapter=adapter.replace('rule_is_not_trained_gate=True', "rule_is_not_trained_gate=mode=='rule_eval'")
    adapter=adapter.replace('training_env_full_CPUCUDA_restore_and_gate_learning_not_admitted=True',
        'frozen_eval_not_training_environment_DR_restore=True,source_first_training148_complete=True')
    adapter=adapter.replace("profile='S4_two_frozen_actor_shared35_rule_eval_v1'", "profile='S4_two_frozen_actor_shared35_source148_lease_mode_pair_v1'")
    compile(adapter,'s4_retention_pair_adapter_v1.py','exec');(Q/'s4_retention_pair_adapter_v1.py').write_text(adapter,encoding='utf8')
    witness=(OLD/'retention_native_witness_v8.py').read_text(encoding='utf8')
    witness=witness.replace('from s4_native_pair_adapter_v3_metadata_explicit import build_native_rule_pair',
        'from s4_retention_pair_adapter_v1 import build_native_rule_pair')
    witness=witness.replace('only_actor_loaded=True',"only_actor_loaded=False,pair18_and_trained_gate6_loaded=True,checkpoint_field_W35_scene_anchor=True,router_mode=CONTEXT['router_mode']")
    (Q/'retention_native_witness_v8.py').write_text(witness,encoding='utf8')
    worker=(OLD/'retention_worker_v8.py').read_text(encoding='utf8')
    worker=worker.replace("p.add_argument('--kind',required=True,choices=('flat','spin','world'));", "p.add_argument('--router-mode',required=True,choices=('rule_eval','gate_eval'));p.add_argument('--kind',required=True,choices=('flat','spin','world'));")
    worker=worker.replace('MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015',D.name)
    worker=worker.replace('case=dict(kind=a.kind,', 'case=dict(router_mode=a.router_mode,kind=a.kind,')
    worker=worker.replace('only_actor_loaded=True','only_actor_loaded=False,pair18_and_trained_gate6_loaded=True')
    worker=worker.replace("CONTEXT['save']=save;CONTEXT['output_dir']=str(O)","CONTEXT['save']=save;CONTEXT['output_dir']=str(O);CONTEXT['router_mode']=a.router_mode")
    (Q/'retention_worker_v8.py').write_text(worker,encoding='utf8')
    exact=[]
    for kind in ('flat','spin','world'):
        p=Q/('retention_'+kind+'_native_v8.py');assert p.read_bytes()==(OLD/p.name).read_bytes();exact.append(dict(kind=kind,sha256=H(p)))
    sys.path[:0]=[str(Q)]
    from s4_shared_feedback_hardtop1_v1 import PairRouter
    from s4_eval_trained_gate_source_v1 import load_trained_gate
    refs=copy.deepcopy(pair['sources'])
    for row in refs:row['local_path']=str(Q/'source'/Path(row['local_path']).name)
    ck=torch.load(Q/'source/S4_gate_first_final.pt',map_location='cpu',weights_only=False)
    base=ck['S4_shared_control_state']['cache']['policy'];rng=torch.get_rng_state().clone()
    for n in (80,88):
        for mode in ('rule_eval','gate_eval'):
            router=PairRouter(refs,n,'cpu');load_trained_gate(router,dict(gate,local_path=str(Q/'source/S4_gate_first_final.pt')))
            x=base[:n].clone();router.last_action=x[:,22:28].clone();p=router.decide(0,lambda:x,mode)
            if mode=='rule_eval':expected=((x[:,0].abs()>0)&(x[:,0].abs()<=.300001)&(x[:,1:3].abs().amax(-1)<=1e-6)).long()
            else:expected=p['logits'].argmax(-1)
            assert torch.equal(p['z'],expected) and torch.equal(p['raw_action'],p['expert_means'][torch.arange(n),expected])
            assert not router.optimizer.state
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    old=json.loads((OLD/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
    m={k:old[k] for k in ('shared_source_freeze','V7_actual_native_binding','v5_sdk_primary_stub')}
    m.update(epoch=time.time(),namespace=D.name,approved_GPU=False,status='CPU_PREPARED_ONLY',no_SSH_or_GPU_or_PPO=True,
        sources={'W35_scene_anchor':pair['sources'][1]},source_pair=pair['sources'],trained_gate=gate,
        source_fullstate_not_restored=True,only_actor_loaded=False,pair18_and_trained_gate6_loaded=True,
        original_physics_numeric_main_AST_and_bytes_exact=exact,original_seed20261002=True,
        original_manifest_provenance=dict(path=str(OLD/'RETENTION_CPU_MANIFEST_V8.json'),sha256=H(OLD/'RETENTION_CPU_MANIFEST_V8.json')),
        allowed_router_modes=['rule_eval','gate_eval'],new_native_and_full_cases_not_yet_admitted=True)
    m['package_files_v8']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RETENTION_CPU_MANIFEST_V8.json']
    (Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(m,indent=2),encoding='utf8')
    z=D/'FIRST_GATE_RETENTION_ORIGINAL_V8_PAIR_SOURCE_V1.zip';assert not z.exists()
    with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for p in sorted(Q.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:archive.write(p,p.relative_to(Q).as_posix())
    result=dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,package=dict(path=str(z),sha256=H(z),bytes=z.stat().st_size),
        manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),worker_SHA=H(Q/'retention_worker_v8.py'),
        pair_manifest_SHA=H(Q/'S4_PAIR_SOURCE_MANIFEST.json'),source_complete_file_SHA=gate['sha256'],
        original_three_mainloop_bytes_exact=exact,actual80_88_saved35_both_mode_whole6_CPU_exact=True,
        CPU_RNG_unchanged_0optimizersteps=True,new_namespace=ROOT,first_trained_gate35_complete_input_SHA=H(GATE/'reports/S4_FIRST_TRAINED_GATE35_COMPLETE_DIRECT_RULE_PAIR_CPU_REVIEW.json'),
        original_V8_actualPlane_metadata_sourceonly_limits_retained=True,template_approved_GPU_false_not_future_pass=True)
    (R/'FIRST_GATE_RETENTION_PAIR_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(prepared=True,package_SHA=H(z),files=len(m['package_files_v8']),new_GPU=False)))

if __name__=='__main__':main()
