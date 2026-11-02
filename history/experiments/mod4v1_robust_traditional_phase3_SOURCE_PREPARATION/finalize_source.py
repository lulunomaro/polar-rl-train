"""Normalize provenance-only reader aliases, verify snapshot, SEAL without Git.
Original first-pass manifest/gaps are retained byte-for-byte, never overwritten.
"""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parent;WT=P.parents[2];S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):assert not p.exists(),str(p);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'relative':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'SHA':sha(p)}
def main():
    assert not (P/'INDEX.json').exists()
    mf=load(P/'SOURCE_MANIFEST.json');gaps=load(P/'MISSING_AND_VERSION_GAPS.json');roots=load(P/'EXPLICIT_ROOT_ALLOWLIST.json');entries=mf['entries'];byrel={e['source_relative']:e for e in entries}
    # ARM object's row contains BOTH source .c and object .o; its SHA is for the
    # object. First-pass generic walker associated it with both. The original
    # misleading six source-version claims stay in initial report + erratum.
    arm=byrel['SPR_AUDIT/ARM_OBJECT_BUILD_V1/INDEX.json'];arm_payload=load(WT/arm['snapshot_path']);object_claims={}
    for o in arm_payload['objects']:object_claims[(o['source'].lower(),o['sha256'])]=o
    false_object_source=[];unresolved=[]
    for c in gaps['unresolved_expected_source_versions']:
        key=(c['path'].lower(),c['expected_SHA'])
        if key in object_claims:
            o=object_claims[key];false_object_source.append({**c,'correction':'SHA belongs to object field, not source field','actual_object_path':o['object'],'object_bytes':o['bytes'],'object_SHA':o['sha256'],'producer_original_retained':arm['snapshot_path']})
        else:unresolved.append(c)
    assert len(false_object_source)==6 and not unresolved
    resolved_basename=[];outside=[];remaining=[]
    for x in gaps['events']:
        if x['reason']=='outside_project_text_dependency_not_read':outside.append(x);continue
        if x['reason']=='named_source_or_artifact_absent':
            h=set(x.get('expected_SHA',[]));matches=[r for r in mf['source_version_claims_resolved'] if r['path']==x['path'] and r['expected_SHA'] in h]
            if matches:resolved_basename.append({**x,'correction':'basename-only producer metadata resolved by preserved source-byte SHA, not a missing module file','matching_saved_versions':matches});continue
        remaining.append(x)
    assert len(resolved_basename)==4 and not remaining
    root_expected={x['path'].lower():set(x['expected_source_SHA']) for x in roots['root_files']};root_checks=[]
    for e in entries:
        if e['snapshot_path']:
            assert sha(WT/e['snapshot_path'])==e['snapshot_SHA'],'snapshot byte mismatch'
            assert e['source_SHA']==e['snapshot_SHA'] or e.get('redactions',0)>0
            p=Path(e['path']);st=p.stat();assert (st.st_size,st.st_mtime_ns)==(e['bytes'],e['mtime_ns']),'closed source changed after capture'
            if p.parent==S:
                wanted=root_expected.get(str(p).lower(),set());assert not wanted or e['source_SHA'] in wanted,'current root source is not any admitted executed version';root_checks.append({'path':str(p),'SHA':e['source_SHA'],'execution_SHA_pinned':bool(wanted),'explicit_root_closure':True})
    for name in ['SPR_AUDIT/portable_control_v3_current/INDEX.json','SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/INDEX.json','SPR_AUDIT/portable_spin_h2_v1/INDEX.json','DYNAMIC_COM_MOTION_V1/INDEX.json','SENSOR_CAPTURE_CLOOP_V1/MANIFEST.json','COM_SENSOR_CAPTURE_AUDIT_V1/INDEX.json','INTEGRATED_COM_WINDOW_V1/INDEX.json','C_P25_SPEC625_H4_V1/PROTOCOL.json','ARCHIVE_PHASE2_RECEIPT.json','CONTINUATION_R34.md']:
        assert name in byrel and byrel[name]['snapshot_path'],name+' missing'
    assert byrel['SPR_AUDIT/portable_control_v3_current/INDEX.json']['source_SHA']=='51cfc25a956539557144208900ab238a3573c63ded0dd3fde4be6ded06c37a09'
    assert byrel['SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/INDEX.json']['source_SHA']=='6f123646715090474cc49e33f8b2f2827afd113133fc6cf1e2281f9e1bd097ef'
    reg=load(P/'CASE_AND_FAILURE_REGISTRY.json');assert len(reg['physical_result_files'])==270 and len(reg['software_errors_separate_not_robot_zero_ofN'])==4
    assert all('/r35_' not in x['attempt_id'].lower() and '/r36' not in x['attempt_id'].lower() for x in reg['physical_result_files'])
    for x in reg['software_errors_separate_not_robot_zero_ofN']:assert '/r25_' in x['attempt_id'].lower()
    unknown_raw=[{'path':e['path'],'bytes':e['bytes'],'status':e.get('SHA_status'),'producer_claims':e.get('producer_claims',[])} for e in entries if e['kind'].endswith('metadata_only') and e['source_SHA'] is None]
    raw=[{'path':e['path'],'source_relative':e['source_relative'],'bytes':e['bytes'],'producer_SHA':e['source_SHA'],'status':e.get('SHA_status'),'producer_claims':e.get('producer_claims',[]),'content_read_or_rehashed_for_snapshot':False} for e in entries if e['kind'].endswith('metadata_only')]
    new(P/'PRODUCER_RAW_INDEX.json',{'raw':raw,'unknown':unknown_raw,'known':len(raw)-len(unknown_raw),'binary_or_JSONL_not_reopened':True})
    reconciliation={'status':'PROVENANCE_METADATA_ASSOCIATION_ERRATUM_ONLY_SNAPSHOT_PAYLOADS_UNCHANGED','original_manifest_SHA':sha(P/'SOURCE_MANIFEST.json'),'original_gap_table_SHA':sha(P/'MISSING_AND_VERSION_GAPS.json'),'six_object_SHA_were_not_C_source_SHA':false_object_source,'four_ambiguous_basename_paths_resolved_by_saved_SHA':resolved_basename,'legacy_external_comparison_paths_not_read':outside,'actual_unresolved_R17_R34_source_versions':unresolved,'remaining_in_scope_missing':remaining,'unknown_raw_SHA_remain_unknown':unknown_raw,'source_or_raw_content_rerun_rehash':False}
    new(P/'PROVENANCE_ASSOCIATION_ERRATUM.json',reconciliation)
    canonical_entries=json.loads(json.dumps(entries))
    alias_by_path={}
    for c in false_object_source:alias_by_path.setdefault(c['path'].lower(),set()).add(c['expected_SHA'])
    for e in canonical_entries:
        bad=alias_by_path.get(e['path'].lower(),set());removed=[h for h in e.get('expected_SHA',[]) if h in bad]
        if removed:e['expected_SHA']=[h for h in e['expected_SHA'] if h not in bad];e['object_digest_aliases_removed_from_source_expectations']=removed
    canonical_summary={**mf['summary'],'initial_reader_missing_events_preserved':mf['summary']['missing_table_events'],'initial_unresolved_version_claims_preserved':mf['summary']['unresolved_source_version_claims'],'unresolved_source_version_claims':0,'actual_in_scope_missing_source_versions':0,'reader_association_events_reconciled':10}
    final={'scope':mf['scope'],'summary':canonical_summary,'entries':canonical_entries,'source_version_claims_resolved':mf['source_version_claims_resolved'],'canonical_provenance_note':'Use PROVENANCE_ASSOCIATION_ERRATUM to classify six object-vs-source aliases and four basename-only references; initial reports preserved, no payload changed','actual_unresolved_in_scope_source_versions':0,'legacy_external_source_comparison_not_copied':len(outside),'unknown_raw_SHA_count':len(unknown_raw),'new_raw_content_hashes':0,'Git_status':'SOURCE_ONLY_PREPARED_NOT_STAGED_COMMITTED_OR_PUSHED'}
    new(P/'FINAL_SOURCE_MANIFEST.json',final)
    new(P/'FINAL_MISSING_AND_EXCLUSIONS.json',{'actual_in_scope_missing_source_versions':[],'preserved_prior_reader_association_events':'PROVENANCE_ASSOCIATION_ERRATUM.json','outside_project_legacy_comparison_unread':outside,'unknown_raw_SHA':unknown_raw,'historically_unavailable_not_reconstructed':['R25 discarded postprocessing-loss trajectories','R35 intentionally excluded despite handoff paragraph in CONT_R34'],'exclusions':'EXCLUSIONS.json','no_mtime_admission':True})
    s=canonical_summary;receipt={'status':'SEALED_SOURCE_PREPARATION_ONLY_WAIT_GIT_APPROVAL','prepared_source_cutoff':'through_R34_by_written_parent_authorization','summary':s,'source_snapshot_SHA_pairs_verified':sum(bool(e['snapshot_path']) for e in entries),'root_explicit_admitted_text_files':root_checks,'required_sealed_component_indexes_verified':True,'actual_unresolved_in_scope_source_versions':0,'provenance_reader_aliases_preserved_and_corrected':10,'unknown_raw_SHA':len(unknown_raw),'old_PH1_PH2_references_only':True,'source_root_writes':False,'Git_stage_commit_tag_push_or_recordhelper_calls':0,'original_expert_index_main_writes':False,'physics_tests_GPU_newagent_realIO':False,'final_manifest_SHA':sha(P/'FINAL_SOURCE_MANIFEST.json'),'case_registry_SHA':sha(P/'CASE_AND_FAILURE_REGISTRY.json'),'exclusions_SHA':sha(P/'EXCLUSIONS.json'),'final_gaps_SHA':sha(P/'FINAL_MISSING_AND_EXCLUSIONS.json'),'raw_index_SHA':sha(P/'PRODUCER_RAW_INDEX.json'),'sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    new(P/'FINAL_CONSISTENCY_RECEIPT.json',receipt)
    readme=f'''# PH3 SOURCE_PREPARATION through R34 — 本地已封，Git等待\n\n**仅source snapshot准备完成，不是Git提交：0stage/commit/tag/push/recordhelper，0physics/旧test/GPU/newagent/真实IO。sourceRoot和原expertindex/main未写。**\n\n## 范围与数量\n\n按父书面cutoff R34及[范围](<SCOPE.md>)，闭合R17–R34 source/result/失败，加明确sealed C3/HOST/H2/DYNAMIC_COM/CAPTURE_AUDIT/INTEGRATED及其具名闭包。根文件按explicit closure，不用mtime盲全树。\n\n- 源条目{s['source_entries']}；新text{s['new_text_copies']}份/{s['new_text_bytes']:,}B；PH1/2同byte Git引用{s['prior_PH1_PH2_Git_references']}份，不重record。\n- raw/binary/JSONL仅metadata{s['raw_metadata_only']}，已有producerSHA{s['raw_existing_producerSHA_known']}，unknown{len(unknown_raw)}；没有为归档重读raw/ZIP/USD/objects取得SHA。\n- R17–R34物理result270，R25软件ERROR4独立，22batch/software-abort报告；prep失败/消耗但丢轨迹不改成robot0/N，也不重建。\n- explicit root candidates{s['root_explicit_allowlist_count']}，实际被纳入的root text{len(root_checks)}；active/未来排除{s['excluded_paths_or_trees']}paths或wholetrees；源在capture后变化0，credentialredaction0。\n\n## 文件\n\n- [最终source manifest](<FINAL_SOURCE_MANIFEST.json>)：原SHA↔snapshot SHA/既有Git路径，所有text byte配对核验。\n- [explicit root allowlist](<EXPLICIT_ROOT_ALLOWLIST.json>)、[排除表](<EXCLUSIONS.json>)、[最终缺失表](<FINAL_MISSING_AND_EXCLUSIONS.json>)、[producer raw索引](<PRODUCER_RAW_INDEX.json>)。\n- [case/软件失败registry](<CASE_AND_FAILURE_REGISTRY.json>)、[最终一致性收据](<FINAL_CONSISTENCY_RECEIPT.json>)、[INDEX](<INDEX.json>)。\n- [初始manifest](<SOURCE_MANIFEST.json>)/[初始缺失事件](<MISSING_AND_VERSION_GAPS.json>)/[初始收据](<SNAPSHOT_CONSISTENCY_RECEIPT.json>)原样保留；[provenance关联erratum](<PROVENANCE_ASSOCIATION_ERRATUM.json>)纠正六个ARM objectSHA误关联source.C和四个basename metadata假缺失，保存原事件而不改原报告。最终实际in-scope source版本缺口0。\n- [初次归档脚本SyntaxError](<PREPARATION_FAILURE_001.txt>)及[原脚本](<revisions/prepare_source_attempt01.py>)保留，原SHA f40c3ffea5ffef4edb90087ba605ad9c24cf62d9bd29b767a9737ca06c488efc。只是归档实现错误，不是机器人/模型失败；修后纯ASTpreflight通过才运行，没跑物理/旧test。\n\n旧comparison报告提到的个人Desktop历史XML未外扩读取，已有sourceSHA线索保留；这不构成新R17–R34 executed闭包缺失。原R25未存trajectory仍不可重建；CONT_R34后段R35仅context，R35的实验/错误/流式logger与heading全部排除。\n\n## 重要标签不改\n\nC3/HOST/H2明确sealed；mathτ与finalGUARDEDτ两个物理cohort不混。ARM仅compile对象，不是ARM运行/WCET/BSP。H4stand60/64、forward64/64不冒直线车道/全Goal资格，secondary y偏离仍在；R30 contact tick为pair/point计数，不改作去重physicsstep。COM/window所有可信cue仍UNKNOWN/hardwareunbound，150ms条件区间不升级contact身份。\n\nACTIVE_BOX_QP_V3/ASQP_V3、FRONT_RANGE_PROPOSAL_V1、heading*、R35+、streamed_trace_rows_v1以及temporary/active路径一律排除，不因旧doc链接自动扩入。\n\n此目录位于独立owner worktree，预期branch mod4v1-lqr-mpc-robust/base02b5ff84，仅metadata依据，不调用Git。后续新phase3trial与任何stage/commit/push等待父另行批准；原helper/Phase1/2不修改、不重record。整体Goal保持active。\n'''
    (P/'README.md').write_text(readme,encoding='utf-8')
    files=sorted(p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='INDEX.json')
    new(P/'INDEX.json',{'name':'PH3_SOURCE_PREPARATION','status':'SEALED_LOCAL_SOURCE_ONLY_NOT_GIT_COMMITTED','source_cutoff':'through_R34_only','README':meta(P/'README.md'),'final_manifest':meta(P/'FINAL_SOURCE_MANIFEST.json'),'consistency_receipt':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'provenance_erratum':meta(P/'PROVENANCE_ASSOCIATION_ERRATUM.json'),'no_sourceRoot_or_Git_writes':True,'new_physics_tests_Git_newagent_realIO':False,'files':[meta(p) for p in files]})
    links=0
    for p in P.glob('*.md'):
        for link in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):assert (p.parent/link.split('#')[0]).exists(),(p,link);links+=1
    print(json.dumps({'README':meta(P/'README.md'),'INDEX':meta(P/'INDEX.json'),'FINAL_SOURCE_MANIFEST':meta(P/'FINAL_SOURCE_MANIFEST.json'),'FINAL_CONSISTENCY_RECEIPT':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'source_summary':s,'actual_in_scope_missing_versions':0,'unknown_raw_SHA':len(unknown_raw),'root_actual_text_files':len(root_checks),'links_checked':links,'Git_stage_commit_tag_push':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
