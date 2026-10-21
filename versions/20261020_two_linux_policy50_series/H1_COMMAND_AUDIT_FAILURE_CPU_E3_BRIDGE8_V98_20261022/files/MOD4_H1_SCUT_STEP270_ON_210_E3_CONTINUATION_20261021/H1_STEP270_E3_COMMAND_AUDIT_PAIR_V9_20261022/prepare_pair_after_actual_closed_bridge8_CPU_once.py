from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');B=Path(cfg['previous_stage_dir']);P=Path(cfg['qualified_H1_stage']);failed=Path(cfg['failed_pair_stage'])
    bridge=read(B/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');closed=read(B/'reports/TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL.json');hproof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');failure=read(failed/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    assert closed['actual_finite_transport_returned'] and bridge['passed'] and bridge['all_owner_nodes_children_actual_out'] and bridge['original_canonical_cost_settled'] and set(bridge['models'])=={'recovery'} and bridge['remaining_actual_snapshot']>82512.86069250107
    assert hproof['passed'] and hproof['original_canonical_cost_settled'] and failure['H1_production_failed_no_FINAL'] and failure['original_canonical_cost_settled']
    repair=read(T/'reports/V98_H1_STEP270_EXTERNAL_COMMAND_AUDIT_RECORDED_BOUNDARY_CPU_ACTUAL.json');assert repair['passed'] and repair['candidate']['normalized_rest_AST_exact'] and repair['not_installed']
    assert hproof['models']['h1']['final']['SHA']=='8da7fb20453866eacc2a9b687edb16757e94ba421d5281e12bfaed0141c9fa68' and hproof['models']['h1']['Adam']==677660
    put('PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GO=True,H1_qualified_fallback_not_failed100=True))
    rec=read(B/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');rec.update(remaining_after=bridge['remaining_actual_snapshot'],derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,source_current_cohort_original_cost_summary=bridge);put('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
    payloads={};specs={};sources={}
    for key in ('h1','recovery'):
        oldq=read((failed if key=='h1' else B)/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');base=Path(oldq['payloads'][key]);dest=N/'payloads'/key;assert not dest.exists();shutil.copytree(base,dest)
        oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=(hproof if key=='h1' else bridge)['models'][key];final=model['final'];source=Path(final['local_path']);assert final['twohost_complete_SHA'] and source.stat().st_size==final['bytes']
        spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep'];parent_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['roots']['h1'] if key=='h1' else oldq['roots']['recovery']
        spec.update(previous_runtime_root=parent_root,previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],closed_production_continuation=True,reuse_completed_native=False)
        shutil.copy2(source,dest/'job0/source'/spec['source_filename'])
        if key=='h1':
            shutil.copy2(T/'production_candidate_V3_COMMAND_AUDIT_UNINSTALLED/h1_step270_sdk_runtime_candidate.py',dest/'h1_step270_sdk_runtime_candidate.py')
            shutil.copy2(T/'closed_step270_external_request_audit_repair_source_CPU_v1.py',dest/'closed_production_continuation_CPU_v2.py')
            shutil.copy2(T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')
            (dest/'H1_EXTERNAL_REQUEST_AUDIT_REPAIR_CPU_ACTUAL.json').write_text(json.dumps(repair,indent=2),encoding='utf8');(dest/'H1_PREVIOUS_FAILED_PAIR_ORIGINAL_COST_EVIDENCE.json').write_text(json.dumps(failure,indent=2),encoding='utf8')
            proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json';modelproof=hproof
        else:
            p=dest/'recovery_worker.py';s=p.read_text('utf8');needle='{'+str(oldAdam)+'+20*updates}';assert s.count(needle)==1;p.write_text(s.replace(needle,'{'+str(model['Adam'])+'+20*updates}'),encoding='utf8');proofname='CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json';modelproof=bridge
        for p in (N/'controllers').glob('*.py'):shutil.copy2(p,dest/p.name)
        task=read(dest/'job0/TASK.json');(dest/'PREVIOUS_TASK_METADATA_HISTORICAL.json').write_text(json.dumps(task,indent=2),encoding='utf8')
        task.update(id=cfg['cohort_id']+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_parent_production_root=parent_root,source_policy_hz=spec['policy_hz'],policy_hz=spec['policy_hz'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True,same_step270_phase_complete_continuation=key=='h1',explicit_step270_task_migration=False,qualified_source_fallback_after_failed_pair7=key=='h1',only_command_audit_adapter_repair=key=='h1')
        (dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
        for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,modelproof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
            (dest/name).write_text(json.dumps(value,indent=2),encoding='utf8')
        prior={x['relative']:x for x in oldm['files']};rows=[]
        for p in sorted(dest.rglob('*')):
            if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
            if p.suffix=='.py':ast.parse(p.read_text('utf8'))
            rel=p.relative_to(dest).as_posix();sha=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p);rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
        m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1',explicit_command_audit_adapter_repair=key=='h1');(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
        spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(dest);specs[key]=spec;sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'],qualified_fallback_after_failed_pair7=key=='h1')
    bq=read(B/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');fq=read(failed/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=cfg['roots'],owner_root=cfg['owner_root'],previous_owner_root=bq['owner_root'],failed_h1_root=fq['roots']['h1'],H1_last_qualified57_fallback_current_failed100_not_source=True,E3_latest_bridge8_full_CPU_cost_allout=True,no_native_or_query_replay=True,no_remote_Task_or_GO_yet=True)
    put('TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q);print(json.dumps(dict(prepared=True,sources=sources,no_GO=True)))
if __name__=='__main__':
    try:main()
    except BaseException:
        put('PAIR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_or_GO=True));raise
