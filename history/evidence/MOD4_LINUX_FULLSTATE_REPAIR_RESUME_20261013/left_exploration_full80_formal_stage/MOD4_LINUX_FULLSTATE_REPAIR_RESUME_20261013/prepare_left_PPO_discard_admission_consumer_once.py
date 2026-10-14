"""New four-update discard admission, never a source for the repair formal window."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
s=(D/'original_linux_formal_parent.py').read_text()
replacements={
 'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json':'LEFT_PPO_DISCARD_ADMISSION_MANIFEST.json',
 'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json':'LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json',
 'FORMAL_ONCE_CONSUMED.json':'LEFT_DISCARD4_PPO_ONCE_CONSUMED.json',
 "a=R/'formal'":"a=R/'left_discard4PPO_v1'",
 'original_linux_formal_worker.py':'left_exploration_worker_v1.py',
 "'--max_iterations','10000'":"'--max_iterations','4'",
 'E1_WAVE50_original_Linux20k_continuation':'E1_WAVE50_left_exploration_discard4',
 'begun+3600':'begun+600',
 "kind='Linux_original20k_resume_'":"kind='Linux_left20k_discard4_PPO_admission_'",
 'original_Linux20k_load_restore_learn':'left20k_same_branch_discard4_PPO_admission',
 'ORIGINAL_LINUX_SAVED_REVIEW_READY.json':'LEFT_DISCARD4_PPO_PASSED.json',
 'ORIGINAL_PARENT_ERROR.json':'LEFT_DISCARD4_PARENT_ERROR.json',
 "stop=R/'formal/STOP_AFTER_SAVE.json'":"stop=R/'left_discard4PPO_v1/STOP_AFTER_SAVE.json'",
 "v=json.loads(q.read_bytes());assert v['passed'];markers.append(dict(path=str(q),sha256=sha(q),proof=v))":"v=json.loads(q.read_bytes());assert v['pid']==child['pid'] and v['source_sha256']==m['source']['sha256'];\n            if 'passed' in v:assert v['passed'] is True\n            for k,z in v.items():\n                if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True\n            markers.append(dict(path=str(q),sha256=sha(q),proof=v))",
 'assert len(markers)>=10':"assert len(markers)==13\n        import torch\n        from left_exploration_resume_contract_v1 import same,KEY\n        ck=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(m['source']['path'],map_location='cpu',weights_only=False)\n        delta=[float(ck['optimizer_state_dict']['state'][i]['step'])-float(source['optimizer_state_dict']['state'][i]['step']) for i in range(17)]\n        assert delta==[80.]*17 and sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items())==9\n        assert same(ck[KEY],source[KEY])\n        health=json.loads((p.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes())\n        from e1_terrain_training_health import learning_health_pass\n        assert learning_health_pass(health) and health['control_steps']==96 and health['actual_physics_callbacks']==384 and health['stop_reason'] is None",
 'actual_fullsave=info,own_sourcefreeze_SHA':"discarded_preflight=True,actual_saved_updates=4,envsteps=1920000,callbacks=384,optimizer_step_delta=80,actor9_changed=True,own_checkpoint=str(p),checkpoint_sha256=sha(p),health=health,not_own_formal_source=True,actual_fullsave=info,own_sourcefreeze_SHA"
}
for a,b in replacements.items():
 assert a in s,a
 s=s.replace(a,b)
s=s.replace("env.update(m['original_environment']);begun=time.time()","env.update(m['original_environment']);env.update(OMNI_KIT_ACCEPT_EULA='YES');begun=time.time()")
# Each launch has exactly the same original worker parameters except finite discard iterations.
q=D/'left_PPO_discard_admission_parent_v1.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
(D/'reports/LEFT_PPO_DISCARD_CONSUMER_CPU_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),new_consumer=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),actual_native0PPO_required_first=True,new_four_fullPPO_updates_only=True,source_must_own_native0PPO1e776=True,original20k_parameters_and_rescue_safesave_and_sole_account_function_preserved=True,typed13_startup_schema_required=True,discard_weights_not_formal_source=True,GPU_PPO_NOT_dispatched=True,qualified50=False),indent=2),encoding='utf8')
print(str(q))
