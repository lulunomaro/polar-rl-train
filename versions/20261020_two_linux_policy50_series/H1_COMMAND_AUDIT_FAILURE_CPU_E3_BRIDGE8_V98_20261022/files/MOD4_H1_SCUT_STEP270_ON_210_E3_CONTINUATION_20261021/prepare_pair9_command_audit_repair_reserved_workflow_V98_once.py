from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_COMMAND_AUDIT_PAIR_V9_20261022';OLD=T/'H1_STEP270_E3_PAIR_V7_20261022';B=T/'E3_bridge_continuation_V8'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes())
assert N.is_dir() and not (N/'reports').exists();(N/'reports').mkdir();shutil.copytree(OLD/'controllers',N/'controllers')
repair=read(R/'V98_H1_STEP270_EXTERNAL_COMMAND_AUDIT_RECORDED_BOUNDARY_CPU_ACTUAL.json');assert repair['passed'] and repair['candidate']['normalized_rest_AST_exact']
q=read(B/'reports/RECOVERY_BRIDGE_DETACHED_ACTUAL.json');cfg=dict(sequence=9,cohort_id=N.name,previous_stage_dir=str(B),previous_actual_run_id=q['run_id'],qualified_H1_stage=str(T/'H1_STEP270_E3_PAIR_V6_20261022'),failed_pair_stage=str(OLD),owner_root='/mnt/mod4_linux_durable_20261013/H1step270_commandaudit_2210v9/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_commandaudit_2210v9/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_commandaudit_2210v9/recovery'))
with (N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').open('x',encoding='utf8') as f:json.dump(cfg,f,indent=2)
for name in ('deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py'):
    s=(OLD/name).read_text('utf8')
    if name=='deploy_pair_new_original_writer_bounded_once.py':
        needle=" spec=q['specs']['h1'];root=q['roots']['h1'];local=Path(q['payloads']['h1'])";assert s.count(needle)==1
        extra=""" put('H1_PREVIOUS_FAILED_PAIR7_FRESH_ALL_OUT_ACTUAL.json',d.code(c,d.t.PY,\"from pathlib import Path;import json,os,psutil;B=Path(v['root']);e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and r['original_error'] and r['final'] is None;assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(actual_failed_H1_allout=True,no_FINAL_claim=True)))\",dict(root=q['failed_h1_root']),timeout=45))
"""
        s=s.replace(needle,extra+needle)
    ast.parse(s);(N/name).open('x',encoding='utf8').write(s)
loader=(T/'closed_step270_same_phase_production_source_CPU_v1.py').read_text('utf8').replace('import hashlib,json,os,psutil','import ast,hashlib,json,os,psutil')
needle="    cpu=read(B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')";assert loader.count(needle)==1
extra="""    repair=read(B/'H1_EXTERNAL_REQUEST_AUDIT_REPAIR_CPU_ACTUAL.json');failure=read(B/'H1_PREVIOUS_FAILED_PAIR_ORIGINAL_COST_EVIDENCE.json')
    assert repair['passed'] and repair['candidate']['normalized_rest_AST_exact'] and failure['H1_production_failed_no_FINAL'] and failure['original_canonical_cost_settled']
    path='h1_step270_sdk_runtime_candidate.py';current={x['relative']:x for x in m['files']}
    assert prior[path]['SHA']==repair['candidate']['old_runtime_SHA'] and current[path]['SHA']==repair['candidate']['candidate_runtime_SHA'] and H(B/path)==current[path]['SHA']
    normalized=ast.parse((B/path).read_text('utf8'));normalized.body=[x for x in normalized.body if not isinstance(x,ast.FunctionDef) or x.name!='audit_step270_external_request']
    cls=next(x for x in normalized.body if isinstance(x,ast.ClassDef) and x.name=='H1Step270Env');init=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__');assert isinstance(init.body[-2],ast.Import) and isinstance(init.body[-1],ast.Assign);init.body=init.body[:-2]
    assert H(old/path)==prior[path]['SHA'] and ast.dump(normalized,include_attributes=False)==ast.dump(ast.parse((old/path).read_text('utf8')),include_attributes=False)
    for row in m['files']:
        rel=row['relative']
        if rel.endswith('.py') and rel in prior and rel not in (path,'closed_production_continuation_CPU_v2.py'):
            assert row['SHA']==prior[rel]['SHA'] and row['bytes']==prior[rel]['bytes']
"""
loader=loader.replace(needle,extra+needle);ast.parse(loader);p=T/'closed_step270_external_request_audit_repair_source_CPU_v1.py';p.open('x',encoding='utf8').write(loader)
for p in N.glob('*.py'):ast.parse(p.read_text('utf8'))
v=dict(epoch=time.time(),source_AST_reserved_only=True,no_future_E3_model_prepared=True,no_remote_Task_or_GO=True,H1_intended_qualified_source_SHA='8da7fb20453866eacc2a9b687edb16757e94ba421d5281e12bfaed0141c9fa68',H1_intended_Adam=677660,H1_fallback_after_failed100_not_new_FINAL=True,requires_bridge8_actual_full_CPU_original_cost_allout=True,H1_audit_candidate_not_installed=True,H1_native3_query9_same_geometry_reused=True,controller_bytes_exact=all(H(p)==H(OLD/'controllers'/p.name) for p in (N/'controllers').glob('*.py')),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in N.rglob('*') if p.is_file()],new_loader=dict(path=str(T/'closed_step270_external_request_audit_repair_source_CPU_v1.py'),SHA=H(T/'closed_step270_external_request_audit_repair_source_CPU_v1.py')))
with (R/'V98_PAIR9_COMMAND_AUDIT_REPAIR_UNUSED_WORKFLOW_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(reserved=str(N),not_deployed=True,only_H1_audit_adapter_repair=True)))
