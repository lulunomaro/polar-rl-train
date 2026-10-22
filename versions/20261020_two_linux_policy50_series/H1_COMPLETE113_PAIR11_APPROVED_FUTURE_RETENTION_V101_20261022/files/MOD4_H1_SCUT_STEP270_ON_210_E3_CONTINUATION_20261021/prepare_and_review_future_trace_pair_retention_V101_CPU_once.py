from pathlib import Path
import ast,hashlib,importlib.util,json,os,shutil,tempfile,time,traceback
T=Path(__file__).resolve().parent;R=T/'reports';C=T/'trace_retention_candidate_V1_UNINSTALLED';N=T/'H1_STEP270_E3_PAIR_V11_20261022'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    old=N/'payloads/h1/h1_production_control_prefix_trace_v1.py';original=old.read_text('utf8');addition='\nfrom h1_prefix_pair_retention_v1 import wrap_trace_persist\nH1ControlPrefixTrace.persist=wrap_trace_persist(H1ControlPrefixTrace.persist)\n'
    new=C/old.name;new.open('x',encoding='utf8').write(original+addition);tree=ast.parse(new.read_text('utf8'));assert ast.dump(ast.Module(body=tree.body[:-2],type_ignores=[]),include_attributes=False)==ast.dump(ast.parse(original),include_attributes=False)
    spec=importlib.util.spec_from_file_location('candidate_retention',C/'h1_prefix_pair_retention_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=[]
    with tempfile.TemporaryDirectory(prefix='CPU_FILES_ONLY_',dir=C) as temp:
        parent=Path(temp).resolve();assert parent.is_relative_to(C.resolve())
        def fixture(name,n=6,incomplete=None):
            folder=parent/name;folder.mkdir();rows=[]
            for i in range(n):
                raw=folder/f'control_prefix_{i}.npz';src=folder/f'preupdate_fullsource_{i}.pt';raw.write_bytes(b'CPU_SYNTHETIC_NOT_TRAINING_NPZ'+bytes([i])*17);src.write_bytes(b'CPU_SYNTHETIC_NOT_WEIGHTS'+bytes([i])*11)
                rows.append(dict(path=str(raw),bytes=raw.stat().st_size,SHA=H(raw),controls=7 if i==incomplete else 24,preupdate_source=dict(path=str(src),bytes=src.stat().st_size,SHA=H(src))))
            m.put(folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json',dict(index=rows,all_success_and_failed_control_prefixes_retained=True))
            return folder,rows
        def present(folder):return {int(p.stem.split('_')[-1]) for p in folder.glob('control_prefix_*.npz')}
        def record(name,ok):assert ok,name;cases.append(dict(name=name,passed=True))
        folder,rows=fixture('normal');m.apply_retention(folder,rows);v=read(folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');record('six_pairs_keep_first_and_last_two_raw_and_matching_sources',present(folder)=={0,4,5} and {int(p.stem.split('_')[-1]) for p in folder.glob('preupdate_fullsource_*.pt')}=={0,4,5});record('producer_SHA_history_retained_and_not_all_raw_claimed',v['index']==rows and not v['all_success_and_failed_control_prefixes_retained'])
        m.apply_retention(folder,rows);record('repeated_persist_does_not_redelete_or_make_new_transactions',len(read(folder/'PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json')['transactions'])==1)
        folder,rows=fixture('three',3);m.apply_retention(folder,rows);record('three_or_fewer_pairs_all_retained',present(folder)=={0,1,2})
        folder,rows=fixture('incomplete',6,1);m.apply_retention(folder,rows);record('incomplete_prefix_is_additionally_protected',present(folder)=={0,1,4,5})
        folder,rows=fixture('failure');(folder/'ACTUAL_STEP_ORIGINAL_ERROR.json').write_text('{}');m.apply_retention(folder,rows);record('current_failure_flag_preserves_every_present_pair',present(folder)==set(range(6)))
        folder,rows=fixture('hash_error');Path(rows[2]['path']).write_bytes(b'corrupted');failed=False
        try:m.apply_retention(folder,rows)
        except RuntimeError:failed=True
        record('wrong_SHA_rejected_before_any_delete',failed and present(folder)==set(range(6)))
        folder,rows=fixture('outside');outside=parent/'control_prefix_88.npz';outside.write_bytes(b'outside');rows[1]['path']=str(outside);failed=False
        try:m.apply_retention(folder,rows)
        except RuntimeError:failed=True
        record('outside_folder_rejected_without_deletion',failed and outside.read_bytes()==b'outside' and len(present(folder))==6)
        folder,rows=fixture('hardlink');link=parent/'extra_link';os.link(rows[1]['path'],link);failed=False
        try:m.apply_retention(folder,rows)
        except RuntimeError:failed=True
        record('multiple_links_rejected_before_delete',failed and len(present(folder))==6)
        folder,rows=fixture('partial_IO');unlink=Path.unlink;calls=[0]
        def interrupted(path,*a,**k):
            calls[0]+=1
            if calls[0]==2:raise OSError('CPU injected source-unlink failure')
            return unlink(path,*a,**k)
        failed=False;Path.unlink=interrupted
        try:m.apply_retention(folder,rows)
        except OSError:failed=True
        finally:Path.unlink=unlink
        record('partial_IO_keeps_intent_error_and_remaining_source',failed and not Path(rows[1]['path']).exists() and Path(rows[1]['preupdate_source']['path']).exists() and bool(list(folder.glob('PREFIX_PAIR_RETENTION_INTENT_*'))) and bool(list(folder.glob('PREFIX_PAIR_RETENTION_ORIGINAL_ERROR_*'))))
        (folder/'ACTUAL_STEP_ORIGINAL_ERROR.json').write_text('{}');m.apply_retention(folder,rows);record('later_failure_path_reports_partial_truth_and_stops_pruning',not read(folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')['all_success_and_failed_control_prefixes_retained'] and Path(rows[2]['path']).exists())
        # Execute the actual original persist body with no live rows, wrapped by
        # the candidate. No runner/env/actor is available to this fixture.
        folder,rows=fixture('original_persist');cls=next(x for x in ast.parse(original).body if isinstance(x,ast.ClassDef));fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='persist');ns=dict(Path=Path,time=time,np=None,H=H,put=m.put);exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_original_persist_CPU','exec'),ns)
        class State:pass
        state=State();state.folder=folder;state.rows=[];state.index=rows;state.source_models=[x['preupdate_source'] for x in rows];state.total=144;state.terms=['fixture']
        m.wrap_trace_persist(ns['persist'])(state);record('actual_original_persist_wrapper_preserves_control_metadata',read(folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')['controls']==144 and present(folder)=={0,4,5})
    report=dict(epoch=time.time(),passed=True,not_installed=True,requires_explicit_human_approval=True,scope='CPU synthetic filesystem and isolated actual original persist; no Kit/GPU/learning/native/query or trained-model sample',original_trace=dict(path=str(old),SHA=H(old)),candidate_trace=dict(path=str(new),SHA=H(new)),candidate_adapter=dict(path=str(C/'h1_prefix_pair_retention_v1.py'),SHA=H(C/'h1_prefix_pair_retention_v1.py')),original_trace_AST_exact_except_two_append_nodes=True,all_act_term_reward_step_and_original_persist_bodies_unchanged=True,cases=cases,policy=m.POLICY,only_future_new_root_pairs=True,all_existing_raw_untouched=True,keep_all_production_FINAL_source_failed_models_text_errors_costs_and_full_producer_SHA_history=True,older_future_intermediate_raw_and_preupdate_pairs_not_recoverable_after_pruning=True,no_new_admission_or_physics_or_graduation_threshold=True,no_RNG_actor_optimizer_environment_access_in_adapter=True,no_future_payload_remote_Task_or_GO=True)
    put(R/'V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json',report);print(json.dumps(dict(passed=True,CPU_cases=len(cases),not_installed=True,requires_explicit_approval=True)))
if __name__=='__main__':
    try:main()
    except BaseException:put(R/('V101_TRACE_RETENTION_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),not_installed=True,no_replay=True));raise
