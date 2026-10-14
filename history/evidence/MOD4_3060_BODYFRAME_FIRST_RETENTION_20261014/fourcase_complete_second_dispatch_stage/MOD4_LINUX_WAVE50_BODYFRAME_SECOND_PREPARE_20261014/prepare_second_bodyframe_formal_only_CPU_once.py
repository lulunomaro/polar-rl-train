"""CPU preparation while the finite 3060 owner runs. All admission remains pending."""
from pathlib import Path
import ast,json,hashlib,time,shutil
D=Path(__file__).resolve().parent;W=D.parent;B=W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014';R=D/'reports';P=D/'payload_v1'
SOURCE='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not P.exists();P.mkdir(parents=True);R.mkdir();proof=json.loads((B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes());assert proof['passed'] and proof['own_checkpoint']['sha256']==SOURCE and proof['actual_parent_guardian_child_out'] and proof['two_actual_fcntl_free']
 names=['birth_bodyframe_state_v1.py','birth_bodyframe_reset_adapter_v6.py','birth_bodyframe_full_checkpoint_v5.py','bodyframe_deferred_original_import_v1.py']
 for n in names:shutil.copy2(B/'payload_v1'/n,P/n)
 prior=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/payload_v1'
 shutil.copy2(prior/'left_sameidentity_typed13_receipts.py',P/'left_sameidentity_typed13_receipts.py');shutil.copy2(prior/'second_target_CPU_pure_guard_v2.py',P/'bodyframe_original_CPU_guard.py')
 worker=(B/'payload_v1/bodyframe_formal_worker_v6.py').read_text(encoding='utf8');new=worker.replace("manifest['mode']=='formal300' and manifest['duration_seconds']==300","manifest['mode']=='formal3600' and manifest['duration_seconds']==3600")
 new=new.replace("assert manifest['actual_parent_pid']==os.getppid()", "assert manifest['same_declared_BODY_profile_continuation'] is True and manifest['new_axis_initializer_requested'] is False\n    assert manifest['actual_source_SHA']=='"+SOURCE+"'\n    assert manifest['actual_parent_pid']==os.getppid()")
 (P/'bodyframe_second_formal_worker_v1.py').write_text(new,encoding='utf8')
 parent=(B/'payload_v1/bodyframe_finite_pipeline_parent_v6.py').read_text(encoding='utf8')
 oldmain=next(n for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef) and n.name=='main');start=parent.index('def main():');end=parent.index("\nif __name__=='__main__':",start)
 mainbody='''def main():
    config=json.loads((R/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert config['passed'] and config['target_CPU_actual']
    assert config['same_declared_BODY_profile_continuation'] is True and config['source']['sha256']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
    decision=json.loads((R/'FOURCASE_SECOND_BODY_SCOPE_DECISION_ACTUAL.json').read_bytes())
    assert decision['passed'] and decision['all_own_four_cases_actual_complete'] and decision['second_body3600_reasonable'] and decision['scope_learning_block_index']==2 and decision['max_blocks_same_axis']==2
    assert not (R/'PIPELINE_ONCE_CONSUMED.json').exists()
    for item in config['active_files']:assert sha(R/item['name'])==item['sha256']
    leases=[]
    try:
        for path in LOCKS:
            f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);leases.append(f)
        budget_guard();guard_resources()
        write(R/'PARENT_IDENTITY.json',ident(os.getpid()))
        write(R/'PIPELINE_ONCE_CONSUMED.json',dict(epoch=time.time(),parent=ident(os.getpid()),human_repair_then_train_authorized=True,second_and_last_declared_BODY_block=True,no_native_or_fullrestore_GPU_replay=True))
        subprocess.Popen([sys.executable,str(__file__),'--guardian',str(os.getpid())],cwd=R,start_new_session=True,stdout=(R/'guardian.log').open('xb'),stderr=subprocess.STDOUT)
        c,rc=run_stage(config,'formal3600',Path(config['source']['path']),'formal3600',True)
        write(R/'PIPELINE_COMPLETE_REVIEW_READY.json',dict(epoch=time.time(),passed=True,formal=rc,no_auto_third_learning_block=True,fulltrace_and_3060_behavior_review_next=True,qualified50=False))
        write(R/'CURRENT_STAGE.json',dict(epoch=time.time(),phase='formal_saved_review_ready',checkpoint=record(c),child=None))
    except BaseException:
        write(R/'PIPELINE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_outcomes_preserved=True))
        raise
    finally:
        for f in reversed(leases):fcntl.flock(f,fcntl.LOCK_UN);f.close()
'''
 parent=parent[:start]+mainbody+parent[end:]
 parent=parent.replace('formal300','formal3600').replace('bodyframe_formal_worker_v6.py','bodyframe_second_formal_worker_v1.py').replace('64800+300','64800+3600').replace("duration_seconds=300 if mode=='formal3600'", "duration_seconds=3600 if mode=='formal3600'").replace("str(begun+300) if formal", "str(begun+3600) if formal").replace('Linux_WAVE50_birth_bodyframe_first_bounded_','Linux_WAVE50_birth_bodyframe_second_bounded_')
 anchor="formal_native_and_fullrestore_admitted=admitted)";assert parent.count(anchor)==1;parent=parent.replace(anchor,"formal_native_and_fullrestore_admitted=admitted,same_declared_BODY_profile_continuation=True,new_axis_initializer_requested=False)")
 anchor="    import torch\n    sys.path.insert(0,str(R));";assert parent.count(anchor)==1;parent=parent.replace(anchor,"    assert mode=='formal3600' and admitted is True,'Only the second same BODY profile learning block is admitted'\n    import torch\n    sys.path.insert(0,str(R));")
 anchor="    if KEY in ck:validate(ck[KEY]);assert ck[MARK]['actual_GPU_fullrestore'] is True";assert parent.count(anchor)==1;parent=parent.replace(anchor,"    assert KEY in ck and sha(source)=='"+SOURCE+"'\n    validate(ck[KEY]);assert ck[MARK]['actual_GPU_fullrestore'] is True")
 (P/'bodyframe_second_formal_parent_v1.py').write_text(parent,encoding='utf8')
 # The original fullstate adapter and RL main file are unchanged. Only independent stage admission/deadline and parent orchestration differ.
 for n in names:assert (P/n).read_bytes()==(B/'payload_v1'/n).read_bytes()
 for p in P.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
 mainnode=next(n for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef) and n.name=='main')
 calls=[n for n in ast.walk(mainnode) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run_stage'];assert len(calls)==1 and ast.literal_eval(calls[0].args[1])=='formal3600'
 def node(text,name):return ast.dump(next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
 assert node(new,'main').count("Constant(value='wave50_lifetime_full_checkpoint')")==node(worker,'main').count("Constant(value='wave50_lifetime_full_checkpoint')")
 template=dict(epoch=time.time(),source_SHA=SOURCE,source_path_CPU=proof['own_checkpoint']['path'],duration_seconds=3600,first_body_seconds=300,total_axis_planned_seconds=3900,max_blocks_same_axis=2,scope_learning_block_index=2,formal_only=True,only_original_native144_fullrestore120_scope_actual_SHA_reuse_no_GPU_replay=True,whole_core_and_BODY_strict_restore_required=True,approved_GPU=False,target_CPU_actual=False,fourcase_decision_actual_pending=True,sourcefreeze_actual_pending=True,new_axis_initializer_requested=False,same_declared_BODY_profile_continuation=True,new_first_transition_requested=False,old_scope_identity_fields_retained_as_profile_history=True,no_PPO_no_SSH_no_budgetwrite=True,active_files={p.name:dict(bytes=p.stat().st_size,sha256=H(p)) for p in P.glob('*.py')})
 (P/'SECOND_BODY_CPU_TEMPLATE_NOT_ADMITTED.json').write_text(json.dumps(template,indent=2),encoding='utf8');(R/'SECOND_BODY_FORMAL_ONLY_CPU_COMPONENTS_PREPARED.json').write_text(json.dumps(template,indent=2),encoding='utf8');print(json.dumps(dict(CPU_prepared=True,actual_fourcase_and_target_GPU_admission_pending=True,files=len(template['active_files']),no_remote_GPU=True)))
if __name__=='__main__':main()
