"""Derive the original one-GPU parent without resource/lifecycle changes. Source only, no evaluation/stage."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101'
P=D/'source_fudan_frozen_parent_v2_n20000';assert not P.exists()
old=(D/'source_fudan_frozen_parent_v1/fudan_eval_parent_wait_contract_v1.py').read_text(encoding='utf8')
safe=(D/'source_fudan_frozen_native_eval_v2_n20000/fudan_frozen_eval_safe.py').read_bytes();safe_sha=hashlib.sha256(safe).hexdigest();assert safe_sha=='92b2f98d4d6cb44047803bebe86baf7bd142c39fbfd19090c5bdee3602e47ce5'
q=old.replace('b42feb400aacb53e8c75c16973f6bae580cfbc1c4eb83d3a8eca847add4c0694',safe_sha).replace('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V1','FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V2_N20000')
q=q.replace('_TRAINING_KIND =', '_LEARNER_SOURCE_SHA = "47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d"\n_TRAINING_KIND =',1)
anchor='        learner = audit.mapping("source.learner_counters", prov.get("learner_counters"))';end='        if "expected_learner_counters" in t:'
assert q.count(anchor)==q.count(end)==1
start=q.index(anchor);stop=q.index(end,start)
q=q[:start]+'''        base = audit.mapping("source.base_counters", prov.get("base_counters"))
        audit.eq("source.exact_base", base, dict(updates=64, policy_optimizer_steps=1280,
                 encoder_optimizer_steps=1280, transitions_seen=12582912))
        window = audit.mapping("source.window_counters", prov.get("window_counters"))
        wu0 = window.get("updates")
        audit.check("source.positive_current_window_updates", _integer(wu0, 1), actual=wu0)
        wu = wu0 if _integer(wu0, 1) else 0
        audit.fields("source.current_window", window, dict(updates=wu, policy_optimizer_steps=20*wu,
                     encoder_optimizer_steps=20*wu, transitions_seen=48*20000*wu))
        continuation = audit.mapping("source.learner_continuation", prov.get("learner_continuation"))
        audit.eq("source.continuation_base", continuation.get("base_counters"), base)
        audit.fields("source.continuation", continuation, dict(source_envs=4096, new_envs=20000,
                     fresh_env_history_DR=True, source_env_history_DR_queues_applied=False,
                     pending_rollout_discarded_at_stream_cut=True))
        audit.mapping("source.actual_training_learner_source_receipt", prov.get("training_learner_source_receipt"))
        learner = audit.mapping("source.learner_counters", prov.get("learner_counters"))
        native = audit.mapping("source.native_counters", prov.get("native_counters"))
        u = 64 + wu
        audit.fields("source.learner", learner, dict(updates=u, policy_optimizer_steps=1280+20*wu,
                     encoder_optimizer_steps=1280+20*wu, transitions_seen=12582912+48*20000*wu))
        controls = native.get("actual_native_policy_steps")
        audit.check("source.positive_native_controls", _integer(controls, 1), actual=controls)
        c = controls if _integer(controls, 1) else 0
        audit.fields("source.native", native, dict(actual_native_policy_steps=c,
                     actual_native_transitions=20000*c, physical_callbacks=8*c,
                     feedback_callbacks=2*c, termination_computations=c))
        audit.check("source.native_covers_current_window_and_bounded_partial", wu > 0 and 0 <= c-48*wu <= 48)
'''+q[stop:]
a='            source_checkpoint_sha256=_MOTHER_SHA, full_save_structure_checked=True, native_updates_required=True,'
b='            source_checkpoint_sha256=_LEARNER_SOURCE_SHA, ancestral_mother_checkpoint_sha256=_MOTHER_SHA,\n            schema_version=2, training_num_envs=20000, source_N20000_DR_history_sliced=False,\n            full_save_structure_checked=True, native_updates_required=True,'
assert q.count(a)==1;q=q.replace(a,b)
a='                training_history_DR_optimizer_RNG_applied=False, training_N4096_state_sliced=False,'
b=a+'\n                training_num_envs=20000, training_N20000_state_sliced=False,\n                source_N20000_DR_history_sliced=False, ancestor_N4096_checkpoint_physically_opened=False,'
assert q.count(a)==1;q=q.replace(a,b)
a='        audit.check("source.FILE_SHA_metadata", _sha(binding["sha256"]) and binding["sha256"] != _MOTHER_SHA)'
assert q.count(a)==1;q=q.replace(a,a.replace('binding["sha256"] != _MOTHER_SHA','binding["sha256"] not in (_MOTHER_SHA, _LEARNER_SOURCE_SHA)'))

base=(T/'NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py').read_text(encoding='utf8')
p=base.replace('from worker_sources.parent.task_contract import make_task','from worker_sources.parent.fudan_task_contract_v2 import make_task\nfrom worker_sources.parent.fudan_eval_parent_wait_contract_v1 import qualify_waited_eval')
for a,b in (('len(roles)==9','len(roles)==1'),("len({r['role']for r in roles})==9","{r['role']for r in roles}=={'E3'}"),('len(children)==9','len(children)==1'),('len(ready)==9','len(ready)==1'),('nineisolatedSDKworkers','oneE3isolatedSDKworker'),('ONEGPU_NINE_FRESH80_SKILL_EVAL_NO_LEARNING','ONEGPU_E3_FDN_FRESH80_ORIGINAL_SKILL_EVAL_NO_LEARNING'),('All9SDKscenes+liveactors+N80fullDRreadybeforeanycontrolledstep','E3SDKscene+livefrozenmean+N80fullDRreadybeforeanycontrolledstep'),('NineSDKstartupreadybarrier900s expired','E3SDKstartupreadybarrier900s expired'),('ACTUAL_SINGLE_GPU_NINE_FRESH80_PARALLEL_SKILL_SCREEN','ACTUAL_SINGLE_GPU_E3_FDN_FRESH80_ORIGINAL_SKILL_SCREEN')):
 assert a in p,a;p=p.replace(a,b)
rows=p.splitlines();hits=[i for i,x in enumerate(rows) if 'rc=p.wait();data=' in x];assert len(hits)==1;i=hits[0];line=rows[i];indent=line[:len(line)-len(line.lstrip())]
needle='terminal.append(dict(role=';assert needle in line
line=line.replace(needle,'qualification=qualify_waited_eval(out,json.loads((out/"task.json").read_bytes()),actual_child_pid=p.pid,actual_parent_pid=os.getpid(),returncode=rc,actual_waited=True);terminal.append(dict(fdn_wait_qualification=qualification,role=',1)
needle="and(out/'PRE_CLOSE.json').exists()),data=data";assert needle in line;line=line.replace(needle,"and(out/'PRE_CLOSE.json').exists()and qualification.get('qualified')is True),data=data",1)
rows[i]=line+'\n'+indent+"if not terminal[-1]['passed_execution']:raise RuntimeError('FDN actual-wait qualification failed; own metadata preserved')"
p='\n'.join(rows)+'\n'
# Exact original critical blocks survive the metadata/cardinality adapter.
for begin,end in (('class BusyResource(Exception):pass','deadline=time.time()+2400'),('finally:\n','if __name__')):
 assert p[p.index(begin):p.index(end,p.index(begin))]==base[base.index(begin):base.index(end,base.index(begin))]
assert "pass_fds=tuple(f.fileno()for f in locks)" in p

task='''"""Pure original task wrapper for an actually closed positive N20000 save; no I/O."""
import os
from worker_sources.parent.task_contract import make_task as _original_make_task

def make_task(role, plan, deadline, fds):
    assert role['role']=='E3' and role['controls']==160
    assert role['source_training_execution_qualified'] is True
    assert len(fds)==2 and fds[0]!=fds[1]
    t=_original_make_task(role, plan, deadline, fds)
    for name in ('source_iteration','source_Adam17','source_LR'):
        t.pop(name,None)
    kind='E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1'
    t.update(kind=kind,purpose=kind,owner_parent_pid=os.getpid(),
             policy_interface='fudan_sequence_raw35_history5_latent3_clipped_mean_v1',
             evaluation_scope='ORIGINAL_E3_74_PLUS_6_NORMAL',source_training_execution_qualified=True)
    return t
'''
outputs={'single_gpu_group_supervisor.py':p,'fudan_eval_parent_wait_contract_v1.py':q,'fudan_task_contract_v2.py':task}
for name,text in outputs.items():ast.parse(text,filename=name);compile(text,name,'exec')
P.mkdir()
for name,text in outputs.items():(P/name).write_bytes(text.encode('utf8'))
print(json.dumps(dict(source_only=True,files=[dict(path=name,bytes=len(text.encode('utf8')),SHA=hashlib.sha256(text.encode('utf8')).hexdigest())for name,text in outputs.items()],original_resource_wait_and_finally_blocks_exact=True,SDK_GPU_model_canonical_or_fixture_calls=0,stage_or_dispatch=False),indent=2))
