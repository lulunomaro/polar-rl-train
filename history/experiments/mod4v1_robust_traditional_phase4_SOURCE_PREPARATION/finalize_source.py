"""Append-only PH4 canonical provenance and snapshot verification. NO Git/rawread."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re
P=Path(__file__).resolve().parent;WT=P.parents[2];S=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102')
BINARY={'.jsonl','.npz','.npy','.usd','.usda','.usdc','.stl','.stp','.step','.zip','.7z','.exe','.dll','.obj','.o','.lib','.a','.bin','.elf','.hex','.pt','.pth','.onnx','.png','.jpg','.jpeg','.pdf','.mp4','.raw','.dat','.f32','.f64','.ioc','.sct','.uvprojx'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):assert not p.exists(),str(p);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'relative':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'SHA':sha(p)}
def main():
    assert not (P/'FINAL_INDEX.json').exists()
    m=load(P/'SOURCE_MANIFEST.json');g=load(P/'MISSING_AND_VERSION_GAPS.json');entries=m['entries'];bysha={};byname={};bypath={};verified=0;postchange=[]
    for e in entries:
        bypath[e['path'].lower()]=e;byname.setdefault(Path(e['path']).name.lower(),[]).append(e)
        if e['source_SHA']:bysha.setdefault(e['source_SHA'],[]).append(e)
        for claim in e.get('producer_claims',[]):bysha.setdefault(claim['SHA'],[]).append(e)
        if e['snapshot_path']:
            assert sha(WT/e['snapshot_path'])==e['snapshot_SHA'];verified+=1;st=Path(e['path']).stat()
            if (st.st_size,st.st_mtime_ns)!=(e['bytes'],e['mtime_ns']):postchange.append({'path':e['path'],'status':'postcapture_source_version_only_not_replaced','captured_SHA':e['source_SHA']})
    # Prior record keys are REPOSITORY-relative, not TASK-root-relative. Preserve
    # initial false paths; resolve only keys explicitly hashed by the old record.
    record3=load(WT/'history/experiments/20261102-mod4v1-robust-traditional-phase3.json');oldmap=record3['source_and_evidence_sha256'];repo_alias=[];content_alias=[];hint_alias=[];external=[];remaining=[]
    for e in g['events']:
        if e['reason']=='outside_project_text_dependency_not_read':external.append(e);continue
        expected=e.get('expected_SHA',[]);p=Path(e['path']);repo=None
        if p.is_relative_to(S):
            rel=p.relative_to(S).as_posix();candidate=WT/rel
            if rel in oldmap and oldmap[rel] in expected and candidate.is_file() and candidate.suffix.lower() not in BINARY:
                assert sha(candidate)==oldmap[rel];repo={'repository_path':rel,'prior_commit':'fa6838807f4d69d2b8ac52300d74ad40f365d2ed','SHA':oldmap[rel],'reference_only':True}
        if repo:repo_alias.append({'initial_event':e,'resolution':'old_record_repository_relative_not_task_relative','reference':repo});continue
        matches=[x for h in expected for x in bysha.get(h,[])]
        if matches:content_alias.append({'initial_event':e,'resolution':'already_saved_text_or_existing_producer_digest','matching_paths':sorted({x['path'] for x in matches}),'not_a_new_source_read':True});continue
        if not expected:
            names=byname.get(p.name.lower(),[]);producers=e.get('producers',[])
            scoped=[]
            for c in names:
                for producer in producers:
                    norm=producer.replace('\\','/')
                    # Known saved revision docs retained original pre-move links.
                    if '/SPR_AUDIT/' in norm and '/SPR_AUDIT/' in c['path'].replace('\\','/'):
                        mod=norm.split('/SPR_AUDIT/',1)[1].split('/',1)[0]
                        if '/SPR_AUDIT/'+mod+'/' in c['path'].replace('\\','/'):scoped.append(c)
            if scoped:
                hint_alias.append({'initial_event':e,'resolution':'unversioned_saved_revision_link_module_basename_hint','candidates':[{'path':x['path'],'SHA':x['source_SHA'],'snapshot':x['snapshot_path']} for x in scoped],'not_executed_version_identity':True});continue
        remaining.append(e)
    version_raw=[];version_alias=[];version_gaps=[]
    for e in g['unresolved_expected_source_versions']:
        p=Path(e['path']);h=e['expected_SHA'];matches=bysha.get(h,[])
        if matches:version_alias.append({'initial_claim':e,'resolution':'existing_saved_SHA_or_producer_metadata','paths':sorted({x['path'] for x in matches}),'raw_never_rehashed':True})
        elif p.suffix.lower() in BINARY:
            version_raw.append({'claim':e,'status':'historical_raw_producer_SHA_claim_only_current_bytes_not_verified','current_entry':None if e['path'].lower() not in bypath else {'bytes':bypath[e['path'].lower()]['bytes'],'SHA_status':bypath[e['path'].lower()]['SHA_status']},'source_text_gap':False,'not_rehashed_or_rebuilt':True})
        else:version_gaps.append(e)
    unknown=[{'path':e['path'],'bytes':e['bytes'],'status':e['SHA_status'],'producer_claims':e.get('producer_claims',[])} for e in entries if e['kind'].endswith('metadata_only') and e['source_SHA'] is None]
    ziprel='DELIVERY_STAGE1_20261102_V1/MOD4v1_Traditional_Stage1_20261102_V1.zip';z=next(e for e in entries if e['source_relative']==ziprel)
    assert z['bytes']==10725489 and z['source_SHA']=='8b5bd15b3c26db510ee353b233597332b5899e81e5cec4ef723d265dabe01288' and z['snapshot_path'] is None
    registry=load(P/'CASE_AND_FAILURE_REGISTRY.json');assert len(registry['physical_result_files'])==36
    exclusions=load(P/'EXCLUSIONS.json');bad=[]
    for e in entries:
        low=e['path'].lower();nums=[int(n) for n in re.findall(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',e['source_relative'],re.I)]
        if any(n>39 for n in nums) or any(s in low for s in ('rough_world_leg_v1','prepare_world_leg_v1','run_world_leg_case_v1','minihop_audit_v2','physics_bridge_minihop_flat_v2','physics_bridge_minihop_rm_v2','run_minihop_case_v2','continuation_stage1_delivery')):bad.append(e['path'])
    assert not bad,bad
    reconcile={'status':'APPEND_ONLY_METADATA_NAMESPACE_AND_HISTORICAL_ARTIFACT_RESOLUTION','initial_reports_unchanged':True,'prior_record_repository_path_aliases':repo_alias,'selected_content_or_producer_aliases':content_alias,'saved_revision_document_basename_hints':hint_alias,'external_legacy_comparison_pointers_not_read':external,'remaining_named_missing_or_unbound_links':remaining,'version_claims_resolved_by_existing_metadata':version_alias,'historical_binary_producer_claims_not_current_verified':version_raw,'actual_missing_saved_smalltext_version_claims':version_gaps,'unknown_raw_metadata_preserved':unknown,'no_original_raw_content_reads':True}
    new(P/'PROVENANCE_RECONCILIATION.json',reconcile)
    missing={'initial_events':len(g['events']),'initial_version_claims':len(g['unresolved_expected_source_versions']),'repository_namespace_aliases':len(repo_alias),'saved_digest_aliases':len(content_alias),'revision_document_hints':len(hint_alias),'external_legacy_pointers':external,'remaining_named_missing_or_unbound_links':remaining,'actual_missing_saved_smalltext_version_claims':version_gaps,'historical_binary_claims_metadata_only':version_raw,'raw_unknowns':unknown,'postcapture_future_source_versions':postchange,'exclusions':exclusions,'R35_loss':'4savedconfig/logattempts, postprocessing serialization failure; no valid result/prefix counters retained; exact consumed steps unknown, do not infer4*24000 or0/N ability','parent_cutoff_review_required':True}
    new(P/'FINAL_MISSING_AND_EXCLUSIONS.json',missing)
    facts={'stage_delivery':{'ZIP':{'path':z['path'],'bytes':z['bytes'],'producer_SHA':z['source_SHA'],'content_read_for_archive':False},'not_firmware_or_full_hardware_qualification':True},'components':{'C3_HOST_P25_H2_ASQP_nativeFSM_nativeMPC':'sealed math/interface/compile evidence, not board/WCET/whole robot','C_ACTIVE_MPC_SUPERVISOR_V1':'UNSEALED prototype v2 evidence preserved','HOST_ACTIVE_QP_IO_V1':'BLOCKED_NOT_SEALED, productionframesUNSENT0requests; actorofbinarydisappearanceUNKNOWN, no attribution or bypass','FRONT_RANGE_PROPOSAL_V1':'STATIC_SENSOR_PROPOSAL_ONLY hardwarefalse','MINIHOP_V1':'closednominal4caseprototype, no fabricatedINDEX/seal/qualification'},'cutoff_cases':'R35losses, R36closed26, R38sensoronly6, R39nominal4; all original outcomes retained, no historical-case double count','newphysics_Git_oldonce_GPU_agents_realIO':False,'scope_current_round4_not_admitted':True}
    new(P/'QUALIFICATION_AND_DELIVERY_BOUNDARIES.json',facts)
    canonical_summary={**m['summary'],'initial_missing_events_retained':len(g['events']),'initial_version_claims_retained':len(g['unresolved_expected_source_versions']),'metadata_repository_aliases_resolved':len(repo_alias),'saved_content_aliases_resolved':len(content_alias),'remaining_named_link_gaps':len(remaining),'actual_missing_saved_smalltext_version_claims':len(version_gaps),'historical_binary_version_claims_metadata_only':len(version_raw)}
    new(P/'FINAL_SOURCE_MANIFEST.json',{'scope':m['scope'],'summary':canonical_summary,'entries':entries,'initial_source_manifest_SHA':sha(P/'SOURCE_MANIFEST.json'),'provenance_reconciliation_SHA':sha(P/'PROVENANCE_RECONCILIATION.json'),'prior_record_references_no_new_Git_operation':repo_alias,'original_initial_reports_retained':True,'raw_producer_only_unknowns_not_rehashed':True})
    new(P/'FINAL_CONSISTENCY_RECEIPT.json',{'status':'PH4_LOCAL_SOURCE_PREPARATION_VERIFIED_WAIT_PARENT_CUTOFF_REVIEW_NOT_GIT','source_summary':canonical_summary,'text_source_snapshot_SHA_pairs_verified':verified,'source_payloads_unchanged_after_provenance_reconciliation':True,'postcapture_future_source_versions_not_substituted':postchange,'all_active_exclusions_enforced':True,'stage_ZIP_existingproducerSHA_only_verified_metadata':facts['stage_delivery'],'actual_missing_smalltext_version_claims':version_gaps,'raw_unknown_count':len(unknown),'Git_stage_commit_tag_push_recordhelper':False,'physics_tests_compile_GPU_agents_realIO':False,'sourceRoot_oldexpertindex_main_writes':False,'Goal_active_unchanged':True,'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    md=f'''# PH4 SOURCE_PREPARATION — local only, parent cutoff review pending\n\n**No stage/commit/tag/push/recordhelper. No sourceRoot/oldexpertindex/main edit, physics/oldonce/test/compile/GPU/newagent/realIO.**\n\n## Prepared scope\n\nR35savedserialization/preparationfailures; closedR36/R36b26cases, R38sixsensoronly, R39fournominalminihop. NamedsealedC3/HOST-P25/H2/ASQP/nativeFSM/nativeMPC and rough/raw2k/front closedsource preserved; supervisor remainsUNSEALED, stdioQP remainsBLOCKED_NOT_SEALED/UNSENT, not silently promoted. Stage1package is source/progress/build adaptation, not flashable firmware/robotgraduation.\n\nInitialcapture:{m['summary']['source_entries']}entries;{m['summary']['new_text_copies']}newtext/{m['summary']['new_text_bytes']:,}B +{m['summary']['prior_PH1_PH2_PH3_Git_references']}samebytePH1/2/3references;{m['summary']['raw_metadata_only']}rawmetadata/{m['summary']['raw_existing_producerSHA_known']}producerSHAknown/{len(unknown)}unknown. All{verified}textSHApairs verified. No raw orZIP content rehash.\n\n[FINAL_SOURCE_MANIFEST](<FINAL_SOURCE_MANIFEST.json>), [consistencyreceipt](<FINAL_CONSISTENCY_RECEIPT.json>), [case/failure registry](<CASE_AND_FAILURE_REGISTRY.json>), [explicitrootallowlist](<EXPLICIT_ROOT_ALLOWLIST.json>), [missing/exclusions](<FINAL_MISSING_AND_EXCLUSIONS.json>), [provenance reconciliation](<PROVENANCE_RECONCILIATION.json>), [component/delivery limits](<QUALIFICATION_AND_DELIVERY_BOUNDARIES.json>), [FINAL_INDEX](<FINAL_INDEX.json>).\n\nRoot admission is explicit executedSHA/document/dependency closure, nevermtime. CurrentR40/R41+/ROUGH_WORLD_LEG andbridges/runner/MINIHOP_AUDIT_V2/v2mini bridges/runner/newround4continuation/tempactive paths stay outside even if linked. Earliercontinuation pending/sealed narratives are chronological data, not newexecution instructions.\n\n## Reader/version limits kept honestly\n\nInitial2226missingevents/53versionclaims are preserved in[initialgaps](<MISSING_AND_VERSION_GAPS.json>), not overwritten. PH3record keys are repositoryrelative; initialgenericresolver treatedthem asTASKrelative, accountingfor{len(repo_alias)}aliases. They now reference exact alreadyrecordedbytes, no repeatrecord/cutoff expansion. Other oldrevision/basename and savedSHA/producer associations are separatelyresolved or remain ambiguous.\n\nRemainingnamed/unboundlinks:{len(remaining)}; actualmissing savedSMALLTEXTversionclaims:{len(version_gaps)}. These remain in tables, not fabricated or replaced with activecurrentcode. HistoricalbinarySHAclaims:{len(version_raw)}metadataonly, not proof currentbinarybytes. LegacyDesktopcomparisonpointers remainunread. R35empty/lostraw staysunknown; exactphysicsconsumption isnot reconstructed from configuredcap.\n\n## StageZIP\n\nOnlymetadata:10,725,489B, producerSHA8b5bd15b3c26db510ee353b233597332b5899e81e5cec4ef723d265dabe01288. ZIPnotreopened/hashchecked/extractedforarchival. Packagevirtualfiles/omittednamespace isnot hostpath/sourceadmission. Actualbuilder/manifest/receipt/progress/buildscript preserved.\n\nR36TRAINscreen/lane outcomes, R39errors/failures, all ASQP nonconverged/revisions and reader errors remain original. No benchmarkgraduation/newhardwareclaim fromINDEX. PH1/2/3trial/tag not rerun. Everything here remains local PH4pending; waitparentreview BEFORE any Git action.\n'''
    (P/'README.md').write_text(md,encoding='utf-8')
    for p in P.glob('*.md'):
        for link in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
            if link=='FINAL_INDEX.json':continue
            assert (p.parent/link.split('#')[0]).exists(),(p,link)
    files=sorted(p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_INDEX.json')
    new(P/'FINAL_INDEX.json',{'name':'PH4_SOURCE_PREPARATION','status':'LOCAL_SOURCE_ONLY_PARENT_REVIEW_PENDING_NO_GIT','README':meta(P/'README.md'),'manifest':meta(P/'FINAL_SOURCE_MANIFEST.json'),'receipt':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'missing_tables_are_not_overwritten':True,'Git_not_authorized_or_called':True,'scope_not_expanded_after_capture':True,'files':[meta(p) for p in files]})
    print(json.dumps({'FINAL_INDEX':meta(P/'FINAL_INDEX.json'),'README':meta(P/'README.md'),'FINAL_SOURCE_MANIFEST':meta(P/'FINAL_SOURCE_MANIFEST.json'),'RECEIPT':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'summary':canonical_summary,'named_gaps':remaining,'smalltext_version_gaps':version_gaps,'raw_unknowns':[{'path':x['path'],'bytes':x['bytes']} for x in unknown],'Git_calls':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
