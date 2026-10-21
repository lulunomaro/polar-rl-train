from pathlib import Path
import ast, hashlib, json, shutil, time, traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
    cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json')
    P=Path(cfg['previous_stage_dir'])
    closed=read(P/'reports/TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    proof=read(P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    assert closed['actual_finite_transport_returned'] and proof['passed'] and proof['original_canonical_cost_settled']
    assert set(proof['models'])=={'recovery'} and proof['remaining_actual_snapshot']>82512.86069250107
    hp=read(R/'H1_STEP270_PAYLOAD_AND_EXISTING_NATIVE_QUERY_BINDING_CPU_V2_ACTUAL.json')
    assert hp['passed_H1_payload_source_and_reuse_binding_CPU_only']
    put(R/'PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GO=True))
    rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
    rec.update(remaining_after=proof['remaining_actual_snapshot'],derived_current_cohort_source_cost_receipt_only=True,
               legacy18_pending_not_reconciled_again=True,source_current_cohort_original_cost_summary=proof)
    put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
    dest=N/'payloads/recovery'
    assert not dest.exists()
    base=Path(oldq['payloads']['recovery'])
    shutil.copytree(base,dest)
    oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    model=proof['models']['recovery'];final=model['final']
    source=Path(final['local_path']);assert source.stat().st_size==final['bytes'] and final['twohost_complete_SHA']
    spec=dict(oldq['specs']['recovery'])
    oldAdam=spec['source_Adamstep']
    spec.update(previous_runtime_root=oldq['roots']['recovery'],source_SHA=final['SHA'],source_Adamstep=model['Adam'],
                source_policy_hz=50,policy_hz=50,closed_production_continuation=True)
    shutil.copy2(source,dest/'job0/source'/spec['source_filename'])
    worker=dest/'recovery_worker.py';text=worker.read_text('utf8');needle='{'+str(oldAdam)+'+20*updates}'
    assert text.count(needle)==1;text=text.replace(needle,'{'+str(model['Adam'])+'+20*updates}')
    worker.write_text(text,encoding='utf8')
    for p in (N/'controllers').glob('*.py'):shutil.copy2(p,dest/p.name)
    task=read(dest/'job0/TASK.json')
    task.update(id=cfg['cohort_id']+'_recovery',source_SHA=final['SHA'],source_Adamstep=model['Adam'],
                source_policy_hz=50,policy_hz=50,source_owned_updates=model['updates'],
                source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],
                same_clock_complete_source_no_native_replay=True)
    (dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    (dest/'QUALIFIED_RUNTIME_BASE_MANIFEST.json').write_text(json.dumps(oldm,indent=2),encoding='utf8')
    (dest/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
    (dest/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
    prior={x['relative']:x for x in oldm['files']};rows=[]
    for p in sorted(dest.rglob('*')):
        if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
        if p.suffix=='.py':ast.parse(p.read_text('utf8'))
        rel=p.relative_to(dest).as_posix()
        sha=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
        rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
    m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_policy_hz=50,policy_hz=50,files=rows)
    (dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
    spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    hsource=dict(SHA=hp['source']['SHA'],bytes=hp['source']['bytes'],Adam=674740,
                 path='/mnt/mod4_linux_durable_20261013/H1step270_full20k_native180_2110v3/job0/source.pt')
    q=dict(epoch=time.time(),passed=True,payloads=dict(h1=hp['payload'],recovery=str(dest)),
           specs=dict(h1=hp['spec'],recovery=spec),sources=dict(h1=hsource,recovery=dict(SHA=final['SHA'],
           bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])),
           roots=cfg['roots'],owner_root=cfg['owner_root'],
           latest_E3_complete_model_CPU_original_cost_and_allout=True,
           H1_actual_native3_query9_source_and_RSL_CPU_reused=True,no_remote_Task_or_GO_yet=True)
    put(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
    print(json.dumps(dict(prepared=True,keys=list(q['specs']),H1_GO=False,E3_source=final['SHA'])))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('PAIR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_GO=True))
        raise
