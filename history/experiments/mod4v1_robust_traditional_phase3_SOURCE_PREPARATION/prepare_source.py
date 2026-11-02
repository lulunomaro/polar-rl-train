"""PH3 SOURCE_PREPARATION only: explicit closed closure through R34.
No git subprocess/stage/commit/tag/push, physics/tests/raw digest reread.
Original Task files never written. Only this new owned directory is written.
"""
from pathlib import Path
from collections import deque
import ast,datetime,hashlib,importlib.util,json,math,re,sys,traceback
S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');PROJECT=S.parent
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');P=WT/'history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION'
ROUND=re.compile(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',re.I);HEX=re.compile(r'^[0-9a-fA-F]{64}$')
MODULES=['SPR_AUDIT/portable_control_v3_current','SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1','SPR_AUDIT/portable_spin_h2_v1','DYNAMIC_COM_MOTION_V1','SENSOR_CAPTURE_CLOOP_V1','COM_SENSOR_CAPTURE_AUDIT_V1','INTEGRATED_COM_WINDOW_V1','C_P25_SPEC625_H4_V1','RM_GRID_SCUT_V1','TALL_ROUGH_BANK_V1','MODEL_AUDIT/GUIDE_EFFECTIVE_MATERIAL_V1','MODEL_AUDIT/GUIDE_PRIORITY_VARIANT_V1','DATA_DIAGNOSTIC/FORWARD_DEFICIT_V1','DATA_DIAGNOSTIC/JUMP_CONTACT_IDENTITY_V1']
ROOT_DOCS={'ARCHIVE_PHASE2_RECEIPT.json','CONTINUATION_R34.md','CONTINUATION_R28.md','CONTINUATION_R26.md','CONTINUATION_R16.md'}
CONTAINERS=['batches','configs','results','errors','snapshots','source_snapshots','reports']
TEXT={'.py','.md','.json','.txt','.log','.csv','.tsv','.c','.h','.cpp','.hpp','.s','.asm','.inc','.ld','.map','.lst','.cmake','.cfg','.ini','.toml','.yaml','.yml','.xml','.urdf','.ps1','.sh','.bat','.cmd','.out','.diff','.html','.js','.css','.svg','.sha256'}
BINARY={'.jsonl','.npz','.npy','.usd','.usda','.usdc','.stl','.stp','.step','.zip','.7z','.gz','.tar','.exe','.dll','.obj','.o','.a','.lib','.bin','.elf','.hex','.pt','.pth','.onnx','.png','.jpg','.jpeg','.gif','.webp','.pdf','.mp4','.raw','.dat','.f32','.f64'}

def sha(b):return hashlib.sha256(b).hexdigest()
def safe(v):
    if isinstance(v,float) and not math.isfinite(v):return {'nonfinite_source_literal':str(v),'original_source_bytes_retained':True}
    if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [safe(x) for x in v]
    return v

def dump(p,x):
    assert not p.exists(),str(p)+' already exists';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(safe(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def stat(p):
    x=p.stat();return {'path':str(p),'bytes':x.st_size,'mtime_ns':x.st_mtime_ns}
def relative(p):
    p=p.resolve()
    if p.is_relative_to(S):return p.relative_to(S).as_posix()
    if p.is_relative_to(PROJECT):return '@project/'+p.relative_to(PROJECT).as_posix()
    return '@external/'+str(p).replace(':','').replace('\\','/')
def forbidden(p):
    low=str(p).replace('\\','/').lower();parts=low.split('/');name=p.name.lower()
    if any(x in parts for x in ('__pycache__','.git','.venv','node_modules')):return 'runtime_cache'
    if name.startswith(('.env','id_rsa','id_ed25519')) or p.suffix.lower() in {'.pem','.key','.kdbx'} or ('ssh' in name and p.suffix.lower() in {'.py','.sh','.ps1','.bat'}):return 'credential_or_legacy_ssh_path'
    if any(x in low for x in ('active_box_qp_v3','asqp_v3','front_range_proposal_v1','heading','streamed_trace_rows_v1')):return 'explicit_ACTIVE_or_heading_front_streamed_exclusion'
    if any(int(n)>34 for n in ROUND.findall(low)):return 'R35plus_outside_written_cutoff'
    if name.startswith(('tmp_','temp_','.~','~$')) or any(x in parts for x in ('tmp','temp')) or p.suffix.lower() in {'.tmp','.temp'}:return 'temporary_or_active_path'
    return None

def main():
    assert not (P/'SOURCE_MANIFEST.json').exists(),'No replacement of sealed source snapshot'
    sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();queue=deque();nodes={};processed={};excluded={};missing=[];claims={};jsondocs={};text_by_key={};root_allow={};refs=[];parse_events=[];version_claims=[];import_needs=[]
    priors={};prior_sha={};prior_paths=[]
    for phase,commit in [('mod4v1_robust_traditional_phase1','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),('mod4v1_robust_traditional_phase2','02b5ff84b905a4e40f207a44b0491aeff2f79b7e')]:
        mf=WT/'history/experiments'/phase/'manifest.json';obj=json.loads(mf.read_text(encoding='utf-8'));prior_paths.append({'path':str(mf),'SHA':sha(mf.read_bytes()),'commit':commit})
        for e in obj['entries']:
            if e.get('archive_path') and e.get('original_sha256'):
                row={**e,'prior_commit':commit};priors[(e['source_relative'],e['original_sha256'])]=row;prior_sha.setdefault(e['original_sha256'],[]).append(row)
    def exclude(p,reason,producer=None):
        key=str(p.resolve()).lower();excluded.setdefault(key,{'path':str(p),'relative':relative(p),'reason':reason,'not_traversed_or_read':True,'producer':producer})
    def add(p,reason,expected=None,producer=None,unpinned=False):
        p=Path(p).resolve();bad=forbidden(p)
        if bad:exclude(p,bad,producer);return
        if not p.is_relative_to(PROJECT):
            # External executables/assets may be indexed, never copied/read. No
            # external user-directory source search is performed.
            if p.suffix.lower() not in BINARY:missing.append({'path':str(p),'reason':'outside_project_text_dependency_not_read','producer':producer,'expected_SHA':expected});return
        key=str(p).lower()
        if key not in nodes:nodes[key]={'path':p,'reasons':[],'expected':set(),'producers':[],'allow_unpinned':False};queue.append(key)
        n=nodes[key];n['reasons'].append(reason)
        if expected and HEX.fullmatch(expected):n['expected'].add(expected.lower());version_claims.append({'path':str(p),'expected_SHA':expected.lower(),'producer':producer})
        if producer:n['producers'].append(producer)
        n['allow_unpinned']|=unpinned
        if p.parent==S:root_allow.setdefault(p.name,{'path':str(p),'reasons':[],'expected_source_SHA':set()});root_allow[p.name]['reasons'].append(reason);root_allow[p.name]['expected_source_SHA'].update(n['expected'])
    def tree(d,reason):
        d=Path(d).resolve();bad=forbidden(d)
        if bad:exclude(d,bad);return
        if not d.exists():missing.append({'path':str(d),'reason':'approved_closed_directory_absent','selection':reason});return
        for p in sorted(d.rglob('*')):
            if p.is_file() and not p.is_symlink():add(p,reason,unpinned=True)
    for rel in MODULES:tree(S/rel,'explicit_closed_module_or_completed_R17_R34_evidence_closure')
    for name in ROOT_DOCS:add(S/name,'explicit_parent_continuation_or_PH2receipt',unpinned=True)
    for parent in CONTAINERS:
        d=S/parent
        if not d.exists():continue
        for p in sorted(d.iterdir()):
            nums=[int(x) for x in ROUND.findall(p.name)]
            if any(x>34 for x in nums):exclude(p,'R35plus_container_namespace_not_traversed');continue
            if nums and any(17<=x<=34 for x in nums):
                if p.is_dir():tree(p,'closed_R17_R34_'+parent+'_namespace')
                elif p.is_file():add(p,'closed_R17_R34_'+parent+'_report',unpinned=True)
    for rel in ['SPR_AUDIT/ACTIVE_BOX_QP_V3','SPR_AUDIT/ASQP_V3','FRONT_RANGE_PROPOSAL_V1','heading_hold_controller_v1.py','streamed_trace_rows_v1.py']:exclude(S/rel,'explicit_parent_active_exclusion')
    def resolve(value,producer):
        p=Path(value.split('#')[0])
        if not p.is_absolute():
            a=producer.parent/p;b=S/p;p=a if a.exists() else b
        return p.resolve()
    def producer_claim(p,digest,producer,loc,size=None):
        if not isinstance(digest,str) or not HEX.fullmatch(digest):return
        key=str(p.resolve()).lower();row={'SHA':digest.lower(),'producer':str(producer),'location':loc,'producer_bytes':size}
        if row not in claims.setdefault(key,[]):claims[key].append(row)
    def walk(obj,producer,loc='$',source_context=False):
        if isinstance(obj,dict):
            digest=next((obj[k] for k in ('SHA','sha256','SHA256','sha','original_sha256','source_SHA','output_sha256') if isinstance(obj.get(k),str) and HEX.fullmatch(obj[k])),None)
            for k in ('path','file','source','source_path','source_file','object_path','output','original_path','artifact','npz_path','raw_path'):
                val=obj.get(k)
                if digest and isinstance(val,str) and not val.startswith(('http://','https://')):
                    target=resolve(val,producer);producer_claim(target,digest,producer,loc+'.'+k,obj.get('bytes',obj.get('size_bytes',obj.get('size'))))
                    if source_context:add(target,'named_executed_source_manifest_or_sealed_index_dependency',digest,str(producer),False)
            for key,val in obj.items():
                context=source_context or key.lower() in ('source','sources','files','source_files','source_hashes','source_and_evidence_sha256','frozen_source','source_closure')
                if isinstance(val,str) and HEX.fullmatch(val) and ('/' in str(key) or '\\' in str(key)):
                    target=resolve(str(key),producer);producer_claim(target,val,producer,loc+'.'+str(key));
                    if context:add(target,'named_source_hash_mapping_dependency',val,str(producer),False)
                walk(val,producer,loc+'.'+str(key),context)
        elif isinstance(obj,list):
            for i,v in enumerate(obj):walk(v,producer,loc+'['+str(i)+']',source_context)
    def markdown_closure(p,text):
        completed=text
        if p.name=='CONTINUATION_R34.md':completed=text.split('## 前测距proposal与最新heading尝试')[0]
        for value in re.findall(r'\]\(<([^>]+)>\)',completed):
            if value.startswith(('http://','https://')):continue
            target=resolve(value,p);bad=forbidden(target)
            if bad:exclude(target,bad,str(p));continue
            if not target.is_relative_to(PROJECT):continue
            if target.is_dir():
                # Only explicitly closed module trees are expanded. Unknown
                # directories do not pull a moving tree into the cutoff.
                if any(target==S/x for x in MODULES):tree(target,'completed_doc_named_closed_module')
                else:exclude(target,'directory_not_in_explicit_closed_module_allowlist_no_traversal',str(p))
            else:add(target,'completed_document_explicit_link',producer=str(p),unpinned=True)
    while queue:
        key=queue.popleft()
        if key in processed:continue
        n=nodes[key];p=n['path'];rel=relative(p);expected=n['expected'];is_root=p.parent==S
        if not p.exists():missing.append({'path':str(p),'reason':'named_source_or_artifact_absent','expected_SHA':sorted(expected),'producers':n['producers']});processed[key]=None;continue
        if p.is_dir():missing.append({'path':str(p),'reason':'named_dependency_is_directory_not_file'});processed[key]=None;continue
        before=stat(p);entry={**before,'source_relative':rel,'selection_reasons':n['reasons'],'expected_SHA':sorted(expected),'source_SHA':None,'snapshot_path':None,'snapshot_SHA':None,'prior_git_reference':False}
        ext=p.suffix.lower();is_text=ext in TEXT or p.name in {'LICENSE','NOTICE','Makefile','CMakeLists.txt'}
        if ext in BINARY or not is_text or before['bytes']>10_000_000:
            entry.update(kind='raw_or_binary_metadata_only',SHA_status='unknown_existing_producer_claim_only_no_rehash',content_read_for_snapshot=False);processed[key]=entry;continue
        if is_root and not expected and not n['allow_unpinned']:
            missing.append({'path':str(p),'reason':'root_dependency_not_explicitly_pinned_or_admitted','producers':n['producers']});processed[key]=None;continue
        raw=p.read_bytes();after=stat(p)
        if (before['bytes'],before['mtime_ns'])!=(after['bytes'],after['mtime_ns']):missing.append({'path':str(p),'reason':'source_changed_while_read_active_not_captured'});processed[key]=None;continue
        digest=sha(raw);entry['source_SHA']=digest
        if expected and digest not in expected and (is_root or not n['allow_unpinned']):
            missing.append({'path':str(p),'reason':'current_source_not_executed_SHA_no_current_substitution','current_SHA':digest,'expected_SHA':sorted(expected),'producers':n['producers']});processed[key]=None;continue
        text=None;encoding=None
        for enc in (['utf-16'] if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else ['utf-8-sig','gb18030']):
            try:text=raw.decode(enc);encoding=enc;break
            except UnicodeDecodeError:pass
        if text is None:entry.update(kind='unknown_nontext_metadata_only',source_SHA=None,content_read_for_decode_only=True);processed[key]=entry;continue
        sanitized,count=redact(text);buf=raw if not count else sanitized.encode('utf-8');snapsha=sha(buf);prior=priors.get((rel,digest))
        if prior and prior.get('archive_sha256')==snapsha:
            target=WT/prior['archive_path'];assert sha(target.read_bytes())==snapsha
            entry.update(kind='existing_PH1_PH2_Git_text_reference',snapshot_path=prior['archive_path'],snapshot_SHA=snapsha,prior_git_reference=True,prior_commit=prior['prior_commit'])
        else:
            sub=Path(rel) if not rel.startswith('@') else Path('external_text')/Path(rel.lstrip('@'))
            target=P/'snapshot'/sub;target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():assert target.read_bytes()==buf,'Existing partial snapshot differs; preserve/investigate'
            else:target.write_bytes(buf)
            entry.update(kind='complete_text' if not count else 'credential_redacted_text',snapshot_path=target.relative_to(WT).as_posix(),snapshot_SHA=snapsha)
        entry.update(snapshot_bytes=len(buf),redactions=count,source_encoding=encoding,stable_during_read=True,execution_version_pinned=bool(expected and digest in expected))
        processed[key]=entry;text_by_key[key]=text
        if ext=='.json':
            try:
                obj=json.loads(text);jsondocs[key]=(p,obj);source_context=any(word in p.name.lower() for word in ('source','index','manifest','protocol','freeze','provenance'))
                walk(obj,p,source_context=source_context)
            except Exception as exc:parse_events.append({'path':str(p),'error':type(exc).__name__+': '+str(exc),'original_bytes_preserved':True})
        if ext=='.md':markdown_closure(p,text)
        if ext in ('.log','.txt'):
            for v in re.findall(r'File\s+[\"\']([^\"\']+\.py)[\"\'],\s+line',text):
                target=resolve(v,p)
                if target.is_relative_to(S):add(target,'saved_closed_failure_traceback_source_reference',producer=str(p),unpinned=True)
        if ext=='.py':
            try:
                for node in ast.walk(ast.parse(text)):
                    names=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else ([node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else [])
                    for name in names:
                        target=(S/(name+'.py')).resolve()
                        if target.exists() and target!=p:
                            bad=forbidden(target)
                            if bad:exclude(target,bad,str(p))
                            else:import_needs.append({'path':str(target),'consumer':str(p),'reason':'local_import_closure_requires_named_sourceSHA_or_explicit_admission'})
            except SyntaxError as exc:parse_events.append({'path':str(p),'error':'preserved_source_SyntaxError: '+str(exc),'original_bytes_preserved':True})
    entries=[e for e in processed.values() if e];by_sha={}
    for e in entries:
        if e['snapshot_path']:by_sha.setdefault(e['source_SHA'],[]).append(e)
        if e['kind'].endswith('metadata_only'):
            cl=claims.get(e['path'].lower(),[]);unique=sorted({c['SHA'] for c in cl if c['producer_bytes'] in (None,e['bytes'])});e['producer_claims']=cl
            if len(unique)==1:e.update(source_SHA=unique[0],SHA_status='existing_producer_SHA_not_rehashed')
            elif len(unique)>1:e['SHA_status']='conflicting_producerSHA_current_unknown'
    resolved=[];unresolved=[]
    for claim in version_claims:
        h=claim['expected_SHA'];p=Path(claim['path']);rel=relative(p);candidates=by_sha.get(h,[]);prior=priors.get((rel,h))
        if candidates:resolved.append({**claim,'resolved_saved_path':candidates[0]['snapshot_path'],'resolution':'selected_saved_source_byte_SHA'})
        elif prior:resolved.append({**claim,'resolved_saved_path':prior['archive_path'],'resolution':'prior_PH1_PH2_Git_byte_SHA','prior_commit':prior['prior_commit']})
        else:
            e=processed.get(str(p).lower())
            if e and e['kind'].endswith('metadata_only') and e.get('source_SHA')==h:resolved.append({**claim,'resolution':'producer_only_original_artifact_not_copied'})
            else:unresolved.append({**claim,'reason':'no_saved_matching_version_in_admitted_or_prior_scope'})
    unresolved_imports=[x for x in import_needs if str(Path(x['path']).resolve()).lower() not in processed]
    missing.extend(unresolved_imports)
    # Do not read any otherwise unadmitted root source; just list explicit
    # omissions. No mtime-based admission is used anywhere.
    for p in S.iterdir():
        if p.is_file() and str(p.resolve()).lower() not in nodes:exclude(p,'root_file_not_in_explicit_closed_closure_no_content_read')
    physical=[];software=[];batch=[];evidence=[];historical_case_refs=[]
    for key,(p,obj) in jsondocs.items():
        rel=relative(p);e=processed[key]
        if not e or not e.get('snapshot_path'):continue
        record={'attempt_id':rel,'source_SHA':e['source_SHA'],'snapshot_path':e['snapshot_path'],'original_payload':safe(obj)}
        round_ids=[int(n) for n in ROUND.findall(rel)]
        new_round=any(17<=n<=34 for n in round_ids)
        if rel.startswith('results/') and p.name=='result.json':
            (physical if new_round else historical_case_refs).append(record)
        elif rel.startswith('results/') and p.name=='ERROR.json':
            (software if new_round else historical_case_refs).append(record)
        elif p.name in ('BATCH_RESULT.json','SOFTWARE_ABORT.json'):batch.append(record)
        if any(w in rel.lower() for w in ('error','fail','attempt','revisions/','prep.log','abort')):evidence.append({'id':rel,'source_SHA':e['source_SHA'],'snapshot_path':e['snapshot_path'],'original_status_not_filename_inferred_pass':True})
    for e in entries:
        if e['snapshot_path'] and e['path'].lower().endswith(('.log','.txt','.md','.py')) and any(w in e['source_relative'].lower() for w in ('error','failure','revisions/','prep','abort')):evidence.append({'id':e['source_relative'],'source_SHA':e['source_SHA'],'snapshot_path':e['snapshot_path'],'preserved_source_failure_or_correction':True})
    changes=[]
    for e in entries:
        if e['snapshot_path']:
            assert sha((WT/e['snapshot_path']).read_bytes())==e['snapshot_SHA']
            now=stat(Path(e['path']))
            if (now['bytes'],now['mtime_ns'])!=(e['bytes'],e['mtime_ns']):changes.append({'path':e['path'],'snapshot_SHA':e['snapshot_SHA'],'status':'source_changed_after_frozen_capture_future_version_not_substituted'})
    assert not any(forbidden(Path(e['path'])) for e in entries)
    assert not any(any(int(x)>34 for x in ROUND.findall(e['source_relative'])) for e in entries if not e['source_relative'].startswith('@external'))
    summary={'source_entries':len(entries),'new_text_copies':sum(e['snapshot_path'] is not None and not e['prior_git_reference'] for e in entries),'prior_PH1_PH2_Git_references':sum(e['prior_git_reference'] for e in entries),'new_text_bytes':sum(e.get('snapshot_bytes',0) for e in entries if not e['prior_git_reference']),'raw_metadata_only':sum(e['kind'].endswith('metadata_only') for e in entries),'raw_existing_producerSHA_known':sum(e['kind'].endswith('metadata_only') and e['source_SHA'] is not None for e in entries),'root_explicit_allowlist_count':len(root_allow),'physical_case_result_files':len(physical),'software_error_result_files':len(software),'saved_batch_or_software_abort_reports':len(batch),'missing_table_events':len(missing),'unresolved_source_version_claims':len(unresolved),'excluded_paths_or_trees':len(excluded),'source_changed_after_capture':len(changes),'redactions':sum(e.get('redactions',0) for e in entries),'new_physics_steps':0,'new_tests':0,'raw_content_rehashes':0,'Git_stage_commit_tag_push_calls':0,'newagents_GPU_realIO':False}
    scope={'stage':'PH3_SOURCE_PREPARATION_ONLY_NOT_COMMITTED','written_cutoff':'through_R34_end_by_parent_written_authorization','capture_started_utc':start,'capture_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'explicit_modules':MODULES,'containers_rounds':[17,34],'root_admission':'named closed continuation links / executed SOURCE_MANIFEST INDEX PROTOCOL SHA closure / saved closed failure traceback; no mtime admission','CONT_R34_postR34_handoff':'full document retained context-only; PH4 section not traversed, no R35 case/source admission','prior_manifests':prior_paths,'owner_worktree':str(WT),'owner_branch_expected':'mod4v1-lqr-mpc-robust','owner_base_expected':'02b5ff84b905a4e40f207a44b0491aeff2f79b7e','Git_not_called_or_staged':True,'sourceRoot_not_modified':True,'overall_Goal':'active'}
    dump(P/'SOURCE_MANIFEST.json',{'scope':scope,'summary':summary,'entries':entries,'source_version_claims_resolved':resolved,'producerSHA_only_binary_originals_no_rehash':True})
    dump(P/'EXPLICIT_ROOT_ALLOWLIST.json',{'root_files':[{**v,'expected_source_SHA':sorted(v['expected_source_SHA'])} for v in root_allow.values()],'no_mtime_or_blind_root_tree_selection':True})
    dump(P/'EXCLUSIONS.json',{'paths_or_whole_trees':list(excluded.values()),'R35_in_continuation_only_not_experiment_admission':True,'active_source_not_chased':True})
    dump(P/'MISSING_AND_VERSION_GAPS.json',{'events':missing,'unresolved_expected_source_versions':unresolved,'parse_or_original_source_syntax_events':parse_events,'source_changed_after_capture':changes,'not_reconstructed':['R25 unavailable postprocessing-loss trajectories','R35 handoff only, all source/experiment excluded here'],'current_source_does_not_rewrite_executed_version':True})
    dump(P/'CASE_AND_FAILURE_REGISTRY.json',{'physical_result_files':physical,'software_errors_separate_not_robot_zero_ofN':software,'historical_PH1_PH2_case_reference_reports_not_new_cases':historical_case_refs,'batch_and_software_abort_reports_not_double_counted':batch,'saved_failure_source_log_evidence':evidence,'R17_R23_R24_preparation_errors_not_physical':True,'R25_partial_consumed_work_and_unavailable_trajectory_not_reconstructed':True,'R35_excluded_despite_CONT_R34_handoff':True,'H4_forward64of64_not_lane_or_fullGoal_qualification':True,'R30_contact_tick_field_not_unique_physics_ticks':True})
    dump(P/'SNAPSHOT_CONSISTENCY_RECEIPT.json',{'status':'SOURCE_SNAPSHOT_ONLY_HASH_VERIFIED_PENDING_GIT','scope':scope,'summary':summary,'all_text_source_snapshot_SHA_pairs_verified':True,'all_saved_history_or_software_failures_retained_verbatim':True,'source_changes_after_capture':changes,'Git_stage_commit_tag_push_executed':False,'recordhelper_executed_or_modified':False,'original_expert_index_or_main_write':False,'sourceRoot_writes':False,'old_phase1_phase2_records_replayed':False,'raw_only_producerSHA_metadata':True,'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        P.mkdir(parents=True,exist_ok=True);n=1
        while (P/f'PREPARATION_FAILURE_{n:03d}.txt').exists():n+=1
        (P/f'PREPARATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'PREPARATION_SOURCE_FAILURE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
