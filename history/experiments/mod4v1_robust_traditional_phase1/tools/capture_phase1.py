"""PHASE1 sealed text capture and producer-digest-only raw indexing.
No simulation, SDK, tests, remote hosts, or input file modifications.
Only new owned worktree history directory is written.
"""
from pathlib import Path
import datetime,hashlib,importlib,json,os,re,sys,traceback
SOURCE=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102')
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust')
PHASE=WT/'history/experiments/mod4v1_robust_traditional_phase1'
CUTOFF=datetime.datetime.fromisoformat('2026-11-02T12:37:47+08:00').timestamp()
CUT_TEXT='2026-11-02T12:37:47+08:00'
TEXT={'.py','.md','.json','.jsonl','.log','.txt','.csv','.tsv','.c','.h','.cpp','.hpp','.cmake','.yml','.yaml','.toml','.xml','.urdf','.sh','.ps1','.bat','.diff','.out','.ini','.cfg','.j2','.m','.jl','.ld','.s','.inc','.hex.txt','.sha256'}
BINARY={'.usd','.usdc','.usda','.stl','.step','.stp','.zip','.7z','.tar','.gz','.exe','.obj','.o','.a','.lib','.dll','.bin','.elf','.hex','.npz','.npy','.pt','.pth','.onnx','.png','.jpg','.jpeg','.gif','.webp','.pdf','.mp4','.mp3','.wav','.hf'}
ACTIVE_DIRS={'portable_mpc_qp_v1'}
ROOT_NAMES={'TASK_SCOPE.md','PROPOSED_ACCEPTANCE_V1.md','nominal_gain_v1.json','physics_bridge.py','physics_bridge_v2.py','physics_bridge_v3.py','ground_controller.py','ground_controller_v2.py','ground_controller_v3.py','ground_controller_v4.py','sensor_core.py','sensor_core_v2.py','sensor_core_v3.py','sensor_core_v4.py','run_ground_case.py','run_ground_case_v2.py','run_ground_case_v3.py','run_ground_case_v4.py','prepare_nominal_gain_v1.py','test_sensor_core.py','fix_command_shaper_v2.py','freeze_sources_r00.py','analyze_r00_first_six.py','analyze_r01_spin.py','derive_r01_sensor_controller.py','derive_r01_case_runner.py','derive_r02_sources.py','derive_r03_sources.py','launch_r01_nominal_screen.py','launch_r02_screen.py','launch_r03_screen.py'}
PHASE_RE=re.compile(r'(^|[^a-z0-9])r(?:0[4-9]|[1-9][0-9])(?=[^0-9]|$)',re.I)
SHA_RE=re.compile(r'^[0-9a-fA-F]{64}$')
SELF_REL=PHASE.relative_to(WT).as_posix()

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists(),str(p)+' already exists'
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def statmeta(p):
    st=p.stat();return {'path':str(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'mtime_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat()}
def future_reason(rel):
    low=rel.as_posix().lower()
    if any(part.lower() in ACTIVE_DIRS for part in rel.parts):return 'active_portable_mpc_qp_v1_phase2'
    if PHASE_RE.search(low) or rel.name=='run_ground_case_v5.py':return 'R04_or_later_source_config_batch_result_phase2'
    return None

def selected(rel,st):
    reason=future_reason(rel)
    if reason:return False,reason
    low=rel.as_posix().lower()
    if any(x in rel.parts for x in ['__pycache__','.git','.venv','node_modules']):return False,'runtime_cache_not_archived'
    if rel.name.lower().startswith(('.env','id_rsa','id_ed25519')) or rel.suffix.lower() in {'.pem','.key','.kdbx'} or ('ssh' in rel.name.lower() and rel.suffix.lower() in {'.py','.sh','.ps1','.bat'}):return False,'credential_path_or_old_ssh_script_excluded'
    # This directory was sealed by the parent AFTER the original source cutoff,
    # before the phase snapshot was sealed. Its explicit late admission is logged.
    late_v2=len(rel.parts)>1 and rel.parts[:2]==('SPR_AUDIT','portable_core_v2_kinematics')
    if st.st_mtime>CUTOFF and not late_v2:return False,'post_cutoff_or_future_change_phase2'
    if len(rel.parts)==1:
        ok=rel.name in ROOT_NAMES or (rel.name.startswith(('PROPOSED_ACCEPTANCE','nominal_gain')) and rel.suffix.lower() in {'.md','.json','.txt'}) or bool(re.search(r'(^|[^a-z0-9])r0[0-3](?=[^0-9]|$)',rel.name,re.I)) or (rel.suffix.lower()=='.log' and not future_reason(rel))
        return ok,'sealed_root_whitelist' if ok else 'outside_minimal_phase1_root_whitelist_phase2'
    first=rel.parts[0]
    if first in {'MODEL_AUDIT','DATA_DIAGNOSTIC','SPR_AUDIT'}:return True,'sealed_portable_v2_parent_admission_exception' if late_v2 else 'sealed_audit_directory'
    if first=='snapshots' and len(rel.parts)>1 and rel.parts[1]=='sensor_core_v1_jerk_failure':return True,'preserved_jerk_failure'
    if first=='source_snapshots':return True,'sealed_source_snapshot'
    if first in {'batches','results'} and len(rel.parts)>1 and re.match(r'^r0[0-3](?:_|$)',rel.parts[1],re.I):return True,'sealed_R00_R03_evidence'
    if first in {'configs','reports'}:return True,'sealed_config_or_parent_report'
    return False,'outside_minimal_phase1_whitelist_phase2'

def main():
    assert not (PHASE/'manifest.json').exists(),'Never replace a sealed snapshot'
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    allpaths=sorted((p for p in SOURCE.rglob('*') if p.is_file() and not p.is_symlink()),key=lambda p:str(p.relative_to(SOURCE)).lower())
    initial_paths={str(p.relative_to(SOURCE)) for p in allpaths};chosen=[];pending=[];ignored=[];errors=[]
    for p in allpaths:
        rel=p.relative_to(SOURCE)
        try:st=p.stat()
        except OSError as exc:errors.append({'path':str(p),'error':type(exc).__name__});continue
        ok,why=selected(rel,st)
        if ok:chosen.append((p,rel,st,why))
        else:
            row=dict(statmeta(p),source_relative=rel.as_posix(),reason=why)
            (ignored if why in {'runtime_cache_not_archived','credential_path_or_old_ssh_script_excluded'} else pending).append(row)
    entries=[];json_producers=[];texts={};redactions_total=0
    for p,rel,before,why in chosen:
        entry=dict(statmeta(p),source_relative=rel.as_posix(),selection_reason=why,original_sha256=None,archive_path=None,archive_sha256=None)
        ext=p.suffix.lower()
        index_only=(ext in BINARY or p.name.lower()=='trace.jsonl' or ext in {'.raw','.f32','.f64','.dat'} or (ext=='.jsonl' and ('trace' in p.stem.lower() or 'trajectory' in p.stem.lower())))
        if index_only:
            entry.update(capture_kind='index_only_original_not_read',sha256_status='unknown_until_resolved_from_existing_producer_receipt');entries.append(entry);continue
        if ext not in TEXT and p.name not in {'LICENSE','NOTICE','Makefile','CMakeLists.txt','Dockerfile'}:
            entry.update(capture_kind='index_only_unclassified_format_not_read',sha256_status='unknown_no_rehash');entries.append(entry);continue
        if before.st_size>10_000_000:
            entry.update(capture_kind='index_only_large_text_not_read',sha256_status='unknown_no_rehash');entries.append(entry);continue
        raw=p.read_bytes();after=p.stat()
        if (before.st_mtime_ns,before.st_size)!=(after.st_mtime_ns,after.st_size):
            pending.append(dict(statmeta(p),source_relative=rel.as_posix(),reason='moving_during_capture_phase2'));continue
        encoding='utf-8';text=None
        for enc in (['utf-16'] if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else ['utf-8-sig','gb18030']):
            try:text=raw.decode(enc);encoding=enc;break
            except UnicodeDecodeError:pass
        if text is None:
            entry.update(capture_kind='index_only_nontext_unexpected_not_copied',sha256_status='unknown_no_rehash');entries.append(entry);continue
        sanitized,n=redact(text);redactions_total+=n
        captured=raw if not n else sanitized.encode('utf-8')
        dest=PHASE/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(captured)
        entry.update(capture_kind='complete_text_byte_identical' if captured==raw else 'credential_redacted_text_utf8',original_sha256=sha(raw),archive_path=dest.relative_to(WT).as_posix(),archive_sha256=sha(captured),archive_bytes=len(captured),source_encoding=encoding,redactions=n,stable_during_read=True)
        entries.append(entry);texts[rel.as_posix()]=text
        if ext=='.json':
            try:json_producers.append((p,json.loads(text)))
            except Exception as exc:errors.append({'path':str(p),'error':'JSON producer parse '+type(exc).__name__,'archived_bytes_preserved':True})
    # Producer receipt digest bindings only; raw/trace/bin are NEVER reopened.
    claims={}
    def admissible(path):
        low=str(path).lower();return not any(x in low for x in ['/.ssh/','\\.ssh\\','site-packages','dsh-spill','credentials'])
    def add_claim(value,digest,producer,where,size=None):
        if not isinstance(value,str) or not isinstance(digest,str) or not SHA_RE.fullmatch(digest):return
        if value.startswith(('http://','https://')) or '!' in value:return
        p=Path(value)
        if not p.is_absolute():
            a=producer.parent/p;b=SOURCE/p
            p=a if a.exists() else b
        try:p=p.resolve()
        except OSError:return
        if not admissible(p):return
        key=str(p).lower();claim={'sha256':digest.lower(),'producer':str(producer),'producer_json_location':where,'producer_bytes':size}
        if claim not in claims.setdefault(key,[]):claims[key].append(claim)
    def walk(node,producer,where='$'):
        if isinstance(node,dict):
            digest=next((node[k] for k in ['sha256','SHA256','SHA','sha','original_sha256','output_sha256'] if isinstance(node.get(k),str) and SHA_RE.fullmatch(node[k])),None)
            if digest:
                for k in ['path','source_path','file','source','source_file','original_path']:
                    if isinstance(node.get(k),str):add_claim(node[k],digest,producer,where+'.'+k,node.get('bytes',node.get('size')))
            if isinstance(node.get('trace_SHA'),str):
                case=node.get('case')
                if isinstance(case,str):add_claim(str(SOURCE/'results'/case/'trace.jsonl'),node['trace_SHA'],producer,where+'.case+trace_SHA',node.get('trace_bytes'))
                elif producer.name=='r01_spin_analysis.json':add_claim(str(SOURCE/'results/r01_spin_midpoint/trace.jsonl'),node['trace_SHA'],producer,where+'.trace_SHA bound by analyze_r01_spin.py:5')
            for k,v in node.items():
                if isinstance(v,dict) and isinstance(v.get('sha256'),str) and SHA_RE.fullmatch(v['sha256']) and ('/' in k or '\\' in k):add_claim(k,v['sha256'],producer,where+'.'+k,v.get('bytes'))
                walk(v,producer,where+'.'+str(k))
        elif isinstance(node,list):
            for i,v in enumerate(node):walk(v,producer,where+'['+str(i)+']')
    for producer,obj in json_producers:walk(obj,producer)
    for entry in entries:
        if not entry['capture_kind'].startswith('index_only'):continue
        available=claims.get(entry['path'].lower(),[])
        compatible=[x for x in available if x['producer_bytes'] in (None,entry['bytes'])]
        hashes=sorted({x['sha256'] for x in compatible})
        entry['producer_digest_claims']=available
        if len(hashes)==1:entry.update(original_sha256=hashes[0],sha256_status='existing_producer_claim_only_not_rehashed_for_archive')
        elif len(hashes)>1:entry.update(sha256_status='conflicting_existing_producer_claims_current_hash_unknown')
        else:entry.update(sha256_status='unknown_no_existing_bound_producer_SHA_and_no_rehash')
    # Index explicitly referenced external authority originals; do not read content.
    external=[]
    allowed_roots=[SOURCE.parent/'traditional_control_20261101/model',SOURCE.parent/'mod4_usd_scut_fudan_20261101/candidates/v1']
    allowed_zip=Path(r'C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip')
    for key,cc in sorted(claims.items()):
        path=Path(key)
        if path.is_relative_to(SOURCE) or not (any(path.is_relative_to(x) for x in allowed_roots) or str(path).lower()==str(allowed_zip).lower()):continue
        if path.suffix.lower() not in BINARY|{'.xml'}:continue
        try:st=path.stat();size=st.st_size;exists=True
        except OSError:size=None;exists=False
        unique=sorted({x['sha256'] for x in cc if x['producer_bytes'] in (None,size)})
        external.append({'path':str(path),'exists_metadata_only':exists,'bytes':size,'sha256':unique[0] if len(unique)==1 else None,'sha256_status':'existing_producer_claim_not_rehashed' if len(unique)==1 else 'unknown_or_conflicting_claim','producer_claims':cc,'content_read_for_archival':False})
    byrel={e['source_relative']:e for e in entries}
    trials=[]
    for rel,e in byrel.items():
        if rel.startswith('results/') and rel.endswith('/result.json'):
            obj=json.loads(texts[rel]);case=rel.split('/')[1]
            metrics={k:v for k,v in obj.items() if k.startswith(('tail_','estimator_','max_','nonwheel_','actual_yaw_','xy_','proposed_','peak_')) or k in {'complete','stop_reason','controls','physics_callbacks','duration_actual_s','mode','nominal','model_SHA','terrain','world_truth_control_bypasses'}}
            trials.append({'attempt_id':case,'kind':'existing_recorded_physics_screen_not_new_archive_run','config':obj.get('config'),'result_archive_path':e['archive_path'],'source_result_sha256':e['original_sha256'],'actual_recorded_fields':metrics,'original_result_status_not_reclassified':True,'human_acceptance_or_holdout_inferred':False})
    historical=[
      {'attempt_id':'unit-r00-jerk-attempt01','status':'9_pass_1_fail','evidence':'snapshot/snapshots/sensor_core_v1_jerk_failure/ERROR.json','meaning':'pure numerical command shaper jerk endpoint error, not physics'},
      {'attempt_id':'unit-r00-jerk-attempt02','status':'parent_reported_10_pass_after_fix','evidence':'snapshot/test_sensor_core.py plus archived unit stdout if present; first failure retained','not_rerun_for_archival':True},
      {'attempt_id':'model-three-MCI-diagnostic','status':'compile_pass_diagnostic_only_not_latest_model','evidence':'snapshot/MODEL_AUDIT/DERIVATION_RECEIPT.json'},
      {'attempt_id':'model-preliminary-fullaligned','status':'compile_pass_then_superseded_actual_tire_mesh_missing','evidence':'snapshot/MODEL_AUDIT/USD_SOURCE_DERIVATION_RECEIPT.json'},
      {'attempt_id':'model-actual-USD-source-aligned','status':'compile_pass_with_declared_engine_semantic_choices','evidence':'snapshot/MODEL_AUDIT/MODEL_ALIGNMENT.md'},
      {'attempt_id':'static-nv0-fixture01','status':'failed_fixture_assumption_original_assertion_retained','evidence':'snapshot/DATA_DIAGNOSTIC/STATIC_FRAME_FAILURE_001.txt'},
      {'attempt_id':'static-nv1-frame-fixture02','status':'static_forward_checks_pass_no_step','evidence':'snapshot/DATA_DIAGNOSTIC/STATIC_FRAME_GEOMETRY.json'},
      {'attempt_id':'C-v1-build01-Werror','status':'exit1_9_misleading_indentation_warnings','evidence':'snapshot/SPR_AUDIT/portable_core_v1/build_attempt_01.log'},
      {'attempt_id':'C-v1-build02','status':'build_pass','evidence':'snapshot/SPR_AUDIT/portable_core_v1/build_attempt_02.log'},
      {'attempt_id':'C-v1-selftest01','status':'18101_checks_0_fail_host_only','evidence':'snapshot/SPR_AUDIT/portable_core_v1/selftest_attempt_01.log'},
      {'attempt_id':'C-v1-selftest02','status':'18151_checks_0_fail_host_only','evidence':'snapshot/SPR_AUDIT/portable_core_v1/selftest_attempt_02.log'},
      {'attempt_id':'C-v1-selftest03','status':'18152_checks_0_fail_host_only','evidence':'snapshot/SPR_AUDIT/portable_core_v1/selftest_attempt_03.log'},
      {'attempt_id':'C-v2-kinematics-selftest02','status':'2761_checks_0_fail_host_only_not_ARM','evidence':'snapshot/SPR_AUDIT/portable_core_v2_kinematics/VALIDATION.json'},
      {'attempt_id':'r00-metrics-time-alignment-erratum','status':'original_result_preserved_corrected_prior_grade_timestamp_analysis','evidence':'snapshot/reports/r00_first_six_analysis.json and snapshot/DATA_DIAGNOSTIC/R00_DATA_DIAGNOSTIC.md'},
      {'attempt_id':'git-worktree-empty-index-setup01','status':'initial_307122_staged_D_avoided_no_commit_then_index_only_repair','evidence':'WORKTREE_SETUP_REPAIR.json'}]
    # Observe new files created after initial inventory without consuming active data.
    for p in SOURCE.rglob('*'):
        if p.is_file() and not p.is_symlink() and str(p.relative_to(SOURCE)) not in initial_paths:
            try:pending.append(dict(statmeta(p),source_relative=p.relative_to(SOURCE).as_posix(),reason='created_after_phase1_inventory_phase2'))
            except OSError:pass
    snapshot_changes=[]
    for e in entries:
        if e.get('archive_path'):
            p=Path(e['path']);now=p.stat()
            if (now.st_mtime_ns,now.st_size)!=(e['mtime_ns'],e['bytes']):snapshot_changes.append({'path':e['path'],'captured_sha256':e['original_sha256'],'reason':'source_changed_after_capture_append_in_phase2'})
            assert sha((WT/e['archive_path']).read_bytes())==e['archive_sha256']
    summary={'selected_entries':len(entries),'copied_text_files':sum(bool(x['archive_path']) for x in entries),'copied_text_bytes':sum(x.get('archive_bytes',0) for x in entries),'raw_index_only_files':sum(x['capture_kind'].startswith('index_only') for x in entries),'raw_known_producer_sha':sum(x['capture_kind'].startswith('index_only') and x['original_sha256'] is not None for x in entries),'external_authority_index_entries':len(external),'case_result_count':len(trials),'redactions_total':redactions_total,'pending_observed_files':len(pending),'snapshot_sources_changed_after_capture':len(snapshot_changes),'new_simulation_steps':0,'tests_rerun_for_archival':0}
    dump(PHASE/'manifest.json',{'schema_version':1,'phase':'mod4v1_robust_traditional_phase1','source_root':str(SOURCE),'source_cutoff':CUT_TEXT,'capture_started_utc':started,'capture_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cutoff_exception':'Parent explicitly sealed portable_core_v2_kinematics while phase snapshot unsealed; admitted with actual capture metadata. portable_mpc_qp_v1 excluded.','summary':summary,'entries':entries,'external_authority_artifacts':external,'errors':errors,'original_bytes_to_archive_bytes_sha_mapping':True,'raw_binary_trace_content_never_read_for_archival':True,'sha_unknowns_are_intentional_no_rehash':True})
    dump(PHASE/'CASE_AND_ATTEMPT_REGISTRY.json',{'case_results':trials,'historical_independent_attempts':historical,'no_old_failure_reclassified':True,'new_physics_runs_for_archive':0})
    dump(PHASE/'PHASE2_PENDING.json',{'scope':'R04 all files even if complete32/32; R05+ config/training; active portable_mpc_qp_v1; all post-cutoff/future changes and post-commit receipts','observed_files':pending,'credential_or_runtime_omissions':ignored,'captured_then_changed':snapshot_changes,'future_not_yet_created':['ARCHIVE_PHASE1_RECEIPT.json and any post-commit synchronization report','new parent reports after this capture'],'R04_parent_report_only_not_phase1_evidence':{'complete':32,'stand_proposed_pass':8,'forward_proposed_pass':5,'spin_gated_proposed_pass':2,'spin_gyro_proposed_pass':3,'per_group_n':8,'failure_causes_reported':'drift>.3m and off-target speed','status':'phase2_pending_do_not_equate_complete_with_pass'},'holdout_270_board_MPC_new_model':'not_qualified_in_phase1','goal_status':'active'})
    dump(PHASE/'CAPTURE_SUMMARY.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        PHASE.mkdir(parents=True,exist_ok=True)
        (PHASE/'CAPTURE_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
