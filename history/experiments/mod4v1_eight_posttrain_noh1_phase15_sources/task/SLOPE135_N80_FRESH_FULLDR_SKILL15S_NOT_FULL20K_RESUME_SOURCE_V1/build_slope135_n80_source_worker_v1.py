"""DeriveoriginalN80 bench with explicitclock/cache/freshnominal scopediff only.
This generator readsUTF8 source/metadata only. It neverimportsTorch orSDK.
"""
from pathlib import Path
import ast,difflib,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf')
SRC=W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/implementation/frozen_history_flat_SLOPE134.py'
R=T/'E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1';MOD=R/'runtime/isaac/mod4'
H=lambda x:hashlib.sha256(x).hexdigest()
s=SRC.read_text(encoding='utf-8-sig');tr=ast.parse(s);node=next(x for x in tr.body if isinstance(x,ast.FunctionDef) and x.name=='main');original=ast.get_source_segment(s,node);body=original;changes=[]
def change(old,new,count=1):
 global body
 assert body.count(old)==count,(old,body.count(old));body=body.replace(old,new);changes.append(dict(old=old,new=new,count=count))
change('def main():','def run_original_slope135_bench():')
# Only the1500 literals arecontrolindices/results; physical6000 iskept.
assert body.count('1500')==4
change('1500','750',4)
change('    cfg.scene.num_envs = args.num_envs','    cfg.scene.num_envs = args.num_envs\n    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,"threshold":.01}\n    configure_new_task(cfg, identity)')
change("    r = e.scene['robot']","    r = e.scene['robot']\n    guard=attach_fresh_guard(e,identity,torch,tensor)")
change('    e.reset()','    e.reset()\n    audit_before=fresh_full_dr_audit(e,guard,tensor)\n    feedback_start=int(e._feedback_100hz_tick)')
change('assert e.physics_dt == 0.0025 and e.step_dt == 0.01','assert e.physics_dt == 0.0025 and e.step_dt == 0.02')
change('    vec, policy, observer = build_frozen_policy(RslRlVecEnvWrapper(e, clip_actions=6.0), args.checkpoint, e.device)','    vec, policy, observer = build_cached_frozen_policy(e, cache, torch, tensor)')
change('    rawforces = []','    rawforces = []\n    HOLDER.update(loop_rows=rows,rawforces=rawforces)')
change('    for step in range(args.steps):','    for step in range(args.steps):\n        if time.time()>=task_descriptor["absolute_worker_deadline_epoch"]:raise RuntimeError("Originalfiniteparentdeadline; preserveownpartialresult, no retry")')
change('assert len(rawforces) == (step + 1) * 4','assert len(rawforces) == (step + 1) * 8')
change('np.stack(rawforces[-4:])','np.stack(rawforces[-8:])')
change("float(np.max(abs(independent - phase['impulse']))) / 0.01","float(np.max(abs(independent - phase['impulse']))) / 0.02")
change('speed = along[:, ids] / 0.01','speed = along[:, ids] / 0.02')
change('    output.write_text(json.dumps(result, indent=2))','''    cache.assert_entire_root_unchanged()
    for key,value in HOLDER['actor'].state_dict().items():assert torch.equal(value.detach().cpu(),cache.core('actor_state_dict')[key]),key
    assert int(e._feedback_100hz_tick)-feedback_start==1500
    result.update(purpose=PURPOSE,physical_scope='N80_FRESH_FULLDR_SKILL15S_NOT_FULL20K_RESUME',saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,source_retyped=False,source_cache=cache.receipt(),fresh_N80_D0_D7_before=audit_before,fresh_N80_D0_D7_after=fresh_full_dr_audit(e,guard,tensor),physical_feedback_samples=1500,original135_predicate=metric_from_control_arrays(data,route_scope,r.body_names,np),source_whole20k_native_PASS_is_separate=True,current_guard_scope='closure.01/mimic.01,newasset; originaloldflagsretained,notpairedphysicalgate/DRcohortcomparison',original_actor_A0_STD_loaded=True,critic17AdamLRiter_cached_preserved_not_live_runner_restore=True,one_explicit_fresh_reset=1,no_new_aggregate_graduation_rate=True)
    output.write_text(json.dumps(result, indent=2))''')
change('    e.close()','    e.close()\n    HOLDER["closed"]=True')
helpers='\n\n'.join(ast.get_source_segment(s,x) for x in tr.body if isinstance(x,ast.FunctionDef) and x.name in ('cpu','js','assignments'))
header='''"""FutureparentadmittedN80 SLOPE135freshfullDR skill15s; NOT20kresume.
SOURCE_ONLY untilnewparentTask/admission. No checkpointmigration/fullstatehelper.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,os,sys,time,traceback
from n80_fresh_scope_core import PURPOSE,require_scope,WholeCheckpointIdentityCache
from n80_fresh_runtime_bridge import HOLDER,attach_fresh_guard,fresh_full_dr_audit,build_cached_frozen_policy,metric_from_control_arrays

'''
footer='''

def main():
    global torch,np,wp,task,args,identity,cache,tensor,configure_new_task,E1ResetEvidenceLearningEnv,query,configure_intro,declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS,task_descriptor
    parser=argparse.ArgumentParser();parser.add_argument('--job-root',required=True,type=Path);parser.add_argument('--task',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    # Onlysource/stdmetadata beforeApp; theseadmissionvaluesmustcome fromparent.
    preliminary,unknown=parser.parse_known_args();job=preliminary.job_root.resolve();task_descriptor=json.loads(preliminary.task.read_bytes());require_scope(task_descriptor)
    assert task_descriptor['actual_parent_resources_and_source_SDK_admitted'] is True
    assert task_descriptor['absolute_worker_deadline_epoch']>time.time()
    meta=json.loads((job/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());assert meta['canonical']=='SLOPE135'
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    os.environ.update({k:str(v) for k,v in meta['original_env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
    os.environ.update(RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4V1_E1_ACTUAL_JOB_ROOT=str(job),MOD4V1_E1_KIT_STORAGE_ROOT=str(job/'kit_isolation'))
    storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
    sys.path[:0]=[str(job/'runtime/isaac/mod4'),str(job/'runtime')]
    from launcher_mod4v1_e1_actual import E1IsolatedAppLauncher as AppLauncher
    AppLauncher.add_app_launcher_args(parser);cli=parser.parse_args();cli.out.mkdir(exist_ok=False)
    app=None
    try:
        app=AppLauncher(cli).app
        import numpy as np,torch,warp as wp
        from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task
        identity=bind_before_task_import(job/'new_assets')
        import mod4_task as task
        verify_task_module(task,identity);assert task.POLICY_HZ==50 and task.DECIMATION==8
        from slope5_geometry import configure_slope as configure_intro
        from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
        from e1_terrain_training_health import declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS
        from e1_full_pose_reset import query
        from mild_dr import tensor
        cache=WholeCheckpointIdentityCache(task_descriptor['source_path'],torch)
        def no_optim(*aa,**kk):raise RuntimeError('N80freshskill purpose forbids every optimizerupdate')
        torch.optim.Optimizer.step=no_optim;torch.optim.Adam.step=no_optim
        args=SimpleNamespace(steps=750,num_envs=80,seed=20260928,dr_profile='white_v3',checkpoint=task_descriptor['source_path'],output=str(cli.out/'SLOPE135_N80_FRESH_FULLDR_SKILL15S_RESULT.json'))
        with torch.inference_mode():run_original_slope135_bench()
        cache.assert_entire_root_unchanged()
        (cli.out/'N80_FRESH_SCOPE_COMPLETE.json').write_text(json.dumps(dict(purpose=PURPOSE,controls=750,physics=6000,feedback=1500,source_cache=cache.receipt(),original_scope_not_full20k_resume=True,optimizer_updates=0,canonical_GO_operations=0,env_close_returned=HOLDER['closed']),indent=2))
    except BaseException:
        failure=dict(purpose=PURPOSE,error=traceback.format_exc(),no_automatic_retry=True,original_bench_partial_preserved=True,saved20k_DR_physically_applied=False)
        if 'np' in globals() and HOLDER.get('loop_rows'):
            data={k:np.stack(v) for k,v in HOLDER['loop_rows'].items() if v}
            if HOLDER.get('rawforces'):data['physical_wheel_force_N']=np.stack(HOLDER['rawforces'])
            if data:np.savez_compressed(cli.out/'OWN_PARTIAL_N80_SKILL_RAW.npz',**data)
        (cli.out/'N80_FRESH_SKILL_ORIGINAL_ERROR.json').write_text(json.dumps(failure,indent=2));raise
    finally:
        try:
            if HOLDER.get('env') is not None and not HOLDER.get('closed',False):HOLDER['env'].close();HOLDER['closed']=True
        finally:
            if app is not None:(cli.out/'APP_CLOSING.json').write_text(json.dumps(dict(original_Appclose_called=True)));app.close()
if __name__=='__main__':main()
'''
worker=header+helpers+'\n\n'+body+footer;compile(worker,'worker_slope135_n80_freshskill15s.py','exec')
with (B/'worker_slope135_n80_freshskill15s.py').open('x',encoding='utf-8') as f:f.write(worker)
with (B/'ORIGINAL_FACTORY_CLOCK_CACHE_SCOPE_DIFF_V1.patch').open('x',encoding='utf-8') as f:f.write(''.join(difflib.unified_diff(original.splitlines(True),body.splitlines(True),fromfile=str(SRC)+':main',tofile='worker_slope135_n80_freshskill15s.py:run_original_slope135_bench')))
# Reverse everyexactreplacement in reverseorder proves no incidentalbody edits.
reverse=body
for c in reversed(changes):
 assert reverse.count(c['new'])==c['count'],c['old'];reverse=reverse.replace(c['new'],c['old'])
assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(ast.parse(original),include_attributes=False)
proof=dict(kind='ORIGINAL80_FACTORY_AST_BODY_RECONCILIATION_SOURCE_ONLY',original=dict(path=str(SRC),SHA=H(SRC.read_bytes()),function='main'),derived=dict(path=str(B/'worker_slope135_n80_freshskill15s.py'),SHA=H(worker.encode())),explicit_replacements=changes,reverse_original_main_AST_exact=True,other_original_geometry_placement_command_metric_statements_unchanged=True,no_saved20k_restore_helper_call=True,one_explicit_reset_and_no_SDKVec_constructor=True,sourceonly_no_model_SDK_operations=0)
with (B/'ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json').open('x',encoding='utf-8') as f:json.dump(proof,f,indent=2)
print(json.dumps(dict(worker=str(B/'worker_slope135_n80_freshskill15s.py'),explicit_replacements=len(changes),reverse_AST_exact=True,model_SDK_operations=0),indent=2))
