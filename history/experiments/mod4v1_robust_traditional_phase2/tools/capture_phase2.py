"""PH2 R00--R16 sealed capture; no tests/physics/SDK/raw digest rereads.
Later rounds, mutable shared files after R16, active C-v3 and RM terrain are PH3.
Writes only this NEW owned history directory. Phase1 remains byte-unchanged.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,json,math,re,sys,traceback
S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');P=WT/'history/experiments/mod4v1_robust_traditional_phase2';P1=WT/'history/experiments/mod4v1_robust_traditional_phase1'
ROUND=re.compile(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',re.I);SHA=re.compile('^[0-9a-fA-F]{64}$')
LATE_TOP={'FSM_DETECTOR_V1','CONTACT_PROXY_NOMINAL_V1','MPC8_V1','NORMAL_P25_HOLDOUT_V1','SPIN_CENTER_V1','SPIN_H2_K20_V1'}
SEALED_SPR={'ARM_OBJECT_BUILD_V1','C_MPC8_NUMERIC_V1','ODOM2D_DIAGNOSTIC','portable_core_v1','portable_core_v2_kinematics','portable_mpc_qp_v1','portable_mpc_qp_v2_fast','reference_selected'}
ALLOWED_TOP=LATE_TOP|{'MODEL_AUDIT','DATA_DIAGNOSTIC','SPR_AUDIT','batches','configs','reports','results','snapshots','source_snapshots','errors','JUMP270_V1'}
R16=S/'batches/r16_jump_roll_train33/BATCH_RESULT.json'

def sha(b):return hashlib.sha256(b).hexdigest()
def safe(v):
    if isinstance(v,float) and not math.isfinite(v):return {'nonfinite_original_literal':str(v),'original_source_bytes_retained':True}
    if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [safe(x) for x in v]
    return v

def dump(p,v):
    assert not p.exists(),str(p)+' exists';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(safe(v),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):
    st=p.stat();return {'path':str(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'mtime_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat()}
def select(rel,st,cut):
    parts=rel.parts;name=rel.name;low=rel.as_posix().lower();rounds=[int(x) for x in ROUND.findall(low)]
    if any(x in parts for x in ('__pycache__','.git','.venv','node_modules')):return False,'runtime_cache'
    if name.lower().startswith(('.env','id_rsa','id_ed25519')) or rel.suffix.lower() in {'.pem','.key','.kdbx'} or ('ssh' in name.lower() and rel.suffix.lower() in {'.py','.ps1','.sh','.bat'}):return False,'credential_or_old_ssh_script_excluded'
    if 'portable_control_v3_current' in parts:return False,'explicit_ACTIVE_C_V3_PH3_PENDING'
    if parts[0]=='RM_GRID_SCUT_V1':return False,'post_R16_exact_RM_tiny_step_PH3_not_this_scope'
    if any(n>16 for n in rounds):return False,'R17_or_later_source_report_config_case_PH3'
    if parts[0] in LATE_TOP:return True,'explicit_parent_sealed_module_admission_including_CONTACT_after_R16'
    if len(parts)>1 and parts[0]=='SPR_AUDIT':return (True,'explicit_parent_sealed_SPR_module') if parts[1] in SEALED_SPR else (False,'unknown_or_active_SPR_module_PH3')
    if len(parts)>1 and parts[:2]==('DATA_DIAGNOSTIC','JUMP_CONTACT_IDENTITY_V1'):return True,'parent_sealed_R14_R16_static_identity_candidates_not_original_force_identity'
    if parts[0] not in ALLOWED_TOP and len(parts)>1:return False,'outside_PH2_sealed_root_scope_PH3'
    if rounds and max(rounds)<=16:return True,'explicit_closed_round_R00_R16_evidence'
    if re.search(r'(^|[^a-z0-9])h[12]([^a-z0-9]|$)',low):return True,'sealed_H1_H2_protocol_or_derivative_report'
    if st.st_mtime_ns>cut:return False,'shared_mutable_or_new_post_R16_source_report_PH3'
    return True,'at_or_before_R16_batch_closed_time'

def main():
    assert not (P/'manifest.json').exists(),'No replacement of sealed snapshot'
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();cut=R16.stat().st_mtime_ns
    sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    spec=importlib.util.spec_from_file_location('read_only_phase1_capture_constants',P1/'tools/capture_phase1.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    TEXT=old.TEXT|{'.map','.lst','.d','.asm','.def','.macros','.cmd','.html','.htm','.js','.css','.svg','.tex','.ipynb'};BINARY=old.BINARY
    p1=json.loads((P1/'manifest.json').read_text(encoding='utf-8'));prior={e['source_relative']:e for e in p1['entries']}
    paths=sorted((p for p in S.rglob('*') if p.is_file() and not p.is_symlink()),key=lambda x:x.relative_to(S).as_posix().lower());initial={p.relative_to(S).as_posix() for p in paths}
    entries=[];pending=[];ignored=[];errors=[];json_docs=[];texts={};redactions=0
    for p in paths:
        rel=p.relative_to(S);st=p.stat();ok,reason=select(rel,st,cut)
        if not ok:
            row=dict(meta(p),source_relative=rel.as_posix(),reason=reason);(ignored if reason in ('runtime_cache','credential_or_old_ssh_script_excluded') else pending).append(row);continue
        e=dict(meta(p),source_relative=rel.as_posix(),selection_reason=reason,original_sha256=None,archive_path=None,archive_sha256=None)
        ext=p.suffix.lower();raw_kind=ext in BINARY|{'.raw','.f32','.f64','.dat'} or ext=='.jsonl' or st.st_size>10_000_000
        if raw_kind or (ext not in TEXT and p.name not in {'LICENSE','NOTICE','Makefile','CMakeLists.txt','Dockerfile'}):
            e.update(capture_kind='index_only_original_not_read',sha256_status='unknown_existing_producer_SHA_only_no_rehash');entries.append(e);continue
        raw=p.read_bytes();after=p.stat()
        if (st.st_mtime_ns,st.st_size)!=(after.st_mtime_ns,after.st_size):pending.append(dict(meta(p),source_relative=rel.as_posix(),reason='changed_while_capture_PH3'));continue
        text=None;enc=None
        for candidate in (['utf-16'] if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else ['utf-8-sig','gb18030']):
            try:text=raw.decode(candidate);enc=candidate;break
            except UnicodeDecodeError:pass
        if text is None:e.update(capture_kind='index_only_nontext_not_rehashed',sha256_status='unknown_no_rehash');entries.append(e);continue
        cleaned,n=redact(text);captured=raw if not n else cleaned.encode('utf-8');redactions+=n;e.update(original_sha256=sha(raw),archive_sha256=sha(captured),archive_bytes=len(captured),redactions=n,source_encoding=enc,stable_during_read=True)
        olde=prior.get(rel.as_posix())
        if olde and olde.get('archive_path') and olde.get('original_sha256')==e['original_sha256'] and olde.get('archive_sha256')==e['archive_sha256']:
            ref=WT/olde['archive_path'];assert sha(ref.read_bytes())==e['archive_sha256'];e.update(capture_kind='existing_phase1_Git_byte_identical_reference',archive_path=olde['archive_path'],phase1_commit='93e0814f5d4dc165dda1f85f8ee12bc35be04d2f')
        else:
            dest=P/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():assert dest.read_bytes()==captured,'Partial prior capture differs; preserve and investigate'
            else:dest.write_bytes(captured)
            e.update(capture_kind='complete_text_byte_identical' if captured==raw else 'credential_redacted_text_utf8',archive_path=dest.relative_to(WT).as_posix())
        entries.append(e);texts[rel.as_posix()]=text
        if ext=='.json':
            try:json_docs.append((p,json.loads(text)))
            except Exception as exc:errors.append({'path':str(p),'event_id':'producer-json-read:'+rel.as_posix(),'error':type(exc).__name__,'source_bytes_preserved':True})
    claims={}
    def add(value,digest,producer,location,size=None):
        if not isinstance(value,str) or not isinstance(digest,str) or not SHA.fullmatch(digest) or value.startswith(('http://','https://')) or '!' in value:return
        path=Path(value)
        if not path.is_absolute():
            a=producer.parent/path;b=S/path;path=a if a.exists() else b
        path=path.resolve();key=str(path).lower()
        if any(x in key for x in ('/.ssh/','\\.ssh\\','credentials','site-packages','dsh-spill')):return
        c={'sha256':digest.lower(),'producer':str(producer),'location':location,'producer_bytes':size}
        if c not in claims.setdefault(key,[]):claims[key].append(c)
    def walk(x,p,loc='$'):
        if isinstance(x,dict):
            digest=next((x[k] for k in ('sha256','SHA256','SHA','sha','original_sha256','output_sha256','object_sha256') if isinstance(x.get(k),str) and SHA.fullmatch(x[k])),None)
            if digest:
                for k in ('path','source_path','file','source','source_file','original_path','object_path','output','artifact','output_path','artifact_path','npz_path','raw_path','binary_path'):
                    if isinstance(x.get(k),str):add(x[k],digest,p,loc+'.'+k,x.get('bytes',x.get('size',x.get('size_bytes'))))
            for key,val in x.items():
                if isinstance(val,dict) and isinstance(val.get('sha256'),str) and ('/' in key or '\\' in key):add(key,val['sha256'],p,loc+'.'+key,val.get('bytes'))
                if isinstance(val,str) and SHA.fullmatch(val) and key.lower() in ('trace_sha','trace_sha256'):
                    case=x.get('case',x.get('case_id'))
                    if isinstance(case,str):add(str(S/'results'/case/'trace.jsonl'),val,p,loc+'.case+trace_SHA',x.get('trace_bytes'))
                    elif p.name=='r01_spin_analysis.json':add(str(S/'results/r01_spin_midpoint/trace.jsonl'),val,p,loc+'.source_bound_r01_spin',None)
                walk(val,p,loc+'.'+str(key))
        elif isinstance(x,list):
            for i,v in enumerate(x):walk(v,p,loc+'['+str(i)+']')
    for p,obj in json_docs:walk(obj,p)
    for e in entries:
        if not e['capture_kind'].startswith('index_only'):continue
        available=claims.get(e['path'].lower(),[]);compatible=[c for c in available if c['producer_bytes'] in (None,e['bytes'])];unique=sorted({c['sha256'] for c in compatible});e['producer_claims']=available
        if len(unique)==1:e.update(original_sha256=unique[0],sha256_status='existing_producer_claim_not_rehashed_for_archive')
        elif len(unique)>1:e['sha256_status']='conflicting_producer_claims_current_SHA_unknown'
        else:e['sha256_status']='unknown_no_bound_existing_producer_SHA_no_rehash'
    external=[];roots=[S.parent/'traditional_control_20261101/model',S.parent/'mod4_usd_scut_fudan_20261101/candidates/v1'];zip_path=Path(r'C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip')
    for key,c in claims.items():
        q=Path(key)
        if q.is_relative_to(S) or not (any(q.is_relative_to(x) for x in roots) or str(q).lower()==str(zip_path).lower()):continue
        if q.suffix.lower() not in BINARY|{'.xml'}:continue
        exists=q.exists();size=q.stat().st_size if exists else None;unique=sorted({v['sha256'] for v in c if v['producer_bytes'] in (None,size)})
        external.append({'path':str(q),'bytes':size,'exists_metadata_only':exists,'sha256':unique[0] if len(unique)==1 else None,'status':'producer_only_no_rehash' if len(unique)==1 else 'unknown_or_conflicting','producer_claims':c,'content_read_for_archive':False})
    byrel={e['source_relative']:e for e in entries};physical=[];software=[];host=[];batches=[];attempt_evidence=[]
    for p,obj in json_docs:
        rel=p.relative_to(S).as_posix();e=byrel[rel]
        record={'attempt_id':rel,'archive_path':e['archive_path'],'source_sha256':e['original_sha256'],'stored_payload_not_rewritten':safe(obj)}
        if rel.startswith('results/') and p.name=='result.json':
            record.update(category='recorded_physical_case_no_new_archive_run',case_id=rel.split('/')[1],validity='original_result_and_protocol_fields_preserved_not_inferred_pass');physical.append(record)
        elif rel.startswith('results/') and p.name=='ERROR.json':
            is15=rel.split('/')[1].lower().startswith('r15_');record.update(category='R15_SOFTWARE_API_FAILURE_NOT_VALID_JUMP_SCORE' if is15 else 'recorded_runner_software_or_process_error',case_id=rel.split('/')[1],valid_completed_robot_evaluation=False,partial_consumed_work_preserved=True,missing_prefix_trace_not_reconstructed=is15);software.append(record)
        elif p.name=='BATCH_RESULT.json':record['category']='original_batch_summary_not_additional_case_count';batches.append(record)
        elif p.name in ('RESULT.json','VALIDATION.json','BUILD_RECEIPT.json','OBJECT_SUMMARY.json') or '/attempts/' in rel:record['category']='host_math_static_or_build_evidence_not_robot_qualification';host.append(record)
        if any(k in rel.lower() for k in ('attempt','error','failure','erratum','revision')):attempt_evidence.append({'attempt_evidence_id':rel,'archive_path':e['archive_path'],'source_sha256':e['original_sha256'],'status':'verbatim_original_report_not_filename_inferred_pass'})
    for e in entries:
        rel=e['source_relative']
        if e['archive_path'] and e['path'].lower().endswith(('.log','.txt','.md')) and any(k in rel.lower() for k in ('attempt','error','failure','erratum','revision')):attempt_evidence.append({'attempt_evidence_id':rel,'archive_path':e['archive_path'],'source_sha256':e['original_sha256'],'status':'verbatim_saved_build_unit_reader_source_failure_or_correction'})
    assert sum(x['case_id'].startswith('r16_') for x in physical)==33
    assert sum(x['case_id'].startswith('r15_') for x in software)==33
    assert not any(any(int(n)>16 for n in ROUND.findall(e['source_relative'])) or 'portable_control_v3_current' in e['source_relative'] or e['source_relative'].startswith('RM_GRID_SCUT_V1/') for e in entries)
    changes=[]
    for e in entries:
        if e['archive_path']:
            assert sha((WT/e['archive_path']).read_bytes())==e['archive_sha256']
            st=Path(e['path']).stat()
            if (st.st_size,st.st_mtime_ns)!=(e['bytes'],e['mtime_ns']):changes.append({'path':e['path'],'captured_sha256':e['original_sha256'],'status':'post_capture_version_PH3'})
    for p in S.rglob('*'):
        if p.is_file() and not p.is_symlink() and p.relative_to(S).as_posix() not in initial:pending.append(dict(meta(p),source_relative=p.relative_to(S).as_posix(),reason='new_after_PH2_inventory_PH3'))
    summary={'selected_entries':len(entries),'text_source_entries':sum(bool(e['archive_path']) for e in entries),'new_text_copies':sum(e['capture_kind'] in ('complete_text_byte_identical','credential_redacted_text_utf8') for e in entries),'existing_phase1_Git_text_references':sum(e['capture_kind']=='existing_phase1_Git_byte_identical_reference' for e in entries),'new_text_bytes':sum(e.get('archive_bytes',0) for e in entries if e['capture_kind']!='existing_phase1_Git_byte_identical_reference'),'raw_index_only':sum(e['capture_kind'].startswith('index_only') for e in entries),'raw_existing_producer_SHA_known':sum(e['capture_kind'].startswith('index_only') and e['original_sha256'] is not None for e in entries),'external_original_metadata_entries':len(external),'physical_result_files':len(physical),'software_error_case_files':len(software),'R15_software_failures':sum(x['case_id'].startswith('r15_') for x in software),'R16_valid_case_result_files':sum(x['case_id'].startswith('r16_') for x in physical),'pending_paths_observed':len(pending),'redactions':redactions,'captured_source_later_changes':len(changes),'new_physics_steps_for_archive':0,'tests_rerun_for_archive':0,'raw_content_rehashes_for_archive':0}
    scope={'phase':'mod4v1_robust_traditional_phase2','root':str(S),'historical_round_cutoff':'R16','shared_source_mtime_cutoff_utc':datetime.datetime.fromtimestamp(cut/1e9,datetime.timezone.utc).isoformat(),'cutoff_authority':meta(R16),'capture_start_utc':start,'capture_finish_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'explicit_sealed_module_admissions':sorted(LATE_TOP|{'SPR_AUDIT/'+x for x in SEALED_SPR}|{'DATA_DIAGNOSTIC/JUMP_CONTACT_IDENTITY_V1'}),'excluded_active':'SPR_AUDIT/portable_control_v3_current','post_R16':'R17/R18/R19/R20/R21/R22+ all paths including software prep errors, exact RM terrain and active/future versions are PH3pending','post_commit_receipt_policy':'All earlier PH1 receipts/errors admitted when present; new PH2 receipt/error/sync files are PH3pending, no recursive record/tag','goal_status':'active','R15_software_not_zero_of10_capability':True,'R15_consumed_prefix_physics_not_erased':True,'qualification_claims':'No wholeGoal/270mm/RM/board/complete RNE inferred from H1/H2, angular64/64, ARM compile6/6 or host tests'}
    dump(P/'PH2_ROOT_SCOPE.json',scope)
    dump(P/'manifest.json',{'schema':2,'scope':scope,'summary':summary,'entries':entries,'external_originals':external,'reader_errors':errors,'byte_SHA_source_to_archive_mapping':True,'raw_only_existing_producer_digest_claims_not_current_rehash':True})
    dump(P/'CASE_AND_ATTEMPT_REGISTRY.json',{'physical_cases':physical,'software_cases':software,'batch_summaries_not_doublecounted':batches,'host_static_math_build_reports':host,'independent_saved_attempt_evidence':attempt_evidence,'R15_classification_source':'reports/R15_SOFTWARE_FAILURE_ERRATUM.md','R15_original_partial_work_counts':'preserved from each ERROR JSON; original absent prefix-row traces remain absent','case_complete_not_qualification':True,'no_old_results_rewritten':True})
    dump(P/'PH3_PENDING.json',{'observed_files':pending,'ignored_runtime_or_credential_paths':ignored,'captured_then_changed':changes,'future_not_yet_created':['ARCHIVE_PHASE2_RECEIPT.json and post-commit operation/sync report','DYNAMIC_COM sensor-only prototype after PH2seal','new R17+ reports/cases and active C-v3 closure'],'goal_status':'active','no_phase1_tag_replay':True})
    dump(P/'CAPTURE_SUMMARY.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        P.mkdir(parents=True,exist_ok=True);n=1
        while (P/f'CAPTURE_FAILURE_{n:03d}.txt').exists():n+=1
        (P/f'CAPTURE_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8')
        (P/f'CAPTURE_SOURCE_FAILURE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
