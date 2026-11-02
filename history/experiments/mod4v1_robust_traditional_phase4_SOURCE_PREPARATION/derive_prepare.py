"""Create NEW PH4 capture implementation from immutable PH3 sourceprep design.
Never edits old preparation/index, does not run the generated capture here.
"""
from pathlib import Path
import ast,hashlib
P=Path(__file__).resolve().parent;WT=P.parents[2];old=WT/'history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/prepare_source.py';dest=P/'prepare_source.py';assert not dest.exists();src=old.read_text(encoding='utf-8')
src=src.replace('PH3 SOURCE_PREPARATION only: explicit closed closure through R34.','PH4 SOURCE_PREPARATION only: explicit R35/R36/R38/R39 + approved closed modules.').replace("P=WT/'history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION'","P=WT/'history/experiments/mod4v1_robust_traditional_phase4_SOURCE_PREPARATION'")
def change(a,b):
 global src
 assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
start=src.index('MODULES=');end=src.index('CONTAINERS=',start)
src=src[:start]+"MODULES=['SPR_AUDIT/portable_control_v3_current','SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1','SPR_AUDIT/portable_spin_h2_v1','SPR_AUDIT/ACTIVE_BOX_QP_V3','SPR_AUDIT/portable_fsm_detector_v1','SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1','SPR_AUDIT/HOST_ACTIVE_QP_IO_V1','C_ACTIVE_MPC_SUPERVISOR_V1','ROUGH_POSTURE_CAUSAL_V1','RAW2K_COM_WINDOW_V1','RAW2K_SHADOW_V1','FRONT_RANGE_PROPOSAL_V1','MINIHOP_V1','DELIVERY_STAGE1_20261102_V1']\nROOT_DOCS={'CONTINUATION_R38.md','CONTINUATION_R36.md','CONTINUATION_R34.md','CONTINUATION_R28.md','CONTINUATION_R26.md','CONTINUATION_R16.md','reports/STAGE1_DELIVERY_PROGRESS_20261102.md','build_stage1_delivery_v1.py'}\nCLOSED_ROUNDS={35,36,38,39}\n"+src[end:]
change("if any(x in low for x in ('active_box_qp_v3','asqp_v3','front_range_proposal_v1','heading','streamed_trace_rows_v1')):return 'explicit_ACTIVE_or_heading_front_streamed_exclusion'","if any(x in low for x in ('rough_world_leg_v1','prepare_world_leg_v1.py','run_world_leg_case_v1.py','minihop_audit_v2','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py','run_minihop_case_v2.py','continuation_stage1_delivery.md')):return 'explicit_current_active_worldleg_minihopv2_round4_continuation_exclusion'")
change("if any(int(n)>34 for n in ROUND.findall(low)):return 'R35plus_outside_written_cutoff'","if any(int(n)>39 for n in ROUND.findall(low)):return 'R40plus_outside_written_cutoff'")
# Canonical PH3 schema is normalized into the earlier prior-ref layout.
anchor="    def exclude(p,reason,producer=None):"
insert="""    mf3=WT/'history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json'
    raw3=mf3.read_bytes();assert sha(raw3)=='341429634a62b9aab996d3539ac3f07275b48c442f304945eefe218736fd1f8b';obj3=json.loads(raw3);commit3='fa6838807f4d69d2b8ac52300d74ad40f365d2ed';prior_paths.append({'path':str(mf3),'SHA':sha(raw3),'commit':commit3})
    for e in obj3['entries']:
        if e.get('snapshot_path') and e.get('source_SHA'):
            row={'source_relative':e['source_relative'],'original_sha256':e['source_SHA'],'archive_path':e['snapshot_path'],'archive_sha256':e['snapshot_SHA'],'prior_commit':commit3};priors[(e['source_relative'],e['source_SHA'])]=row;prior_sha.setdefault(e['source_SHA'],[]).append(row)
"""
change(anchor,insert+anchor)
change("for rel in MODULES:tree(S/rel,'explicit_closed_module_or_completed_R17_R34_evidence_closure')","for rel in MODULES:tree(S/rel,'explicit_PH4_named_closed_or_BLOCKED_prototype_evidence_closure')")
change("for name in ROOT_DOCS:add(S/name,'explicit_parent_continuation_or_PH2receipt',unpinned=True)","for name in ROOT_DOCS:add(S/name,'explicit_PH4_closed_continuation_or_stage_delivery_allowlist',unpinned=True)\n    add(WT/'history/experiments/mod4v1_robust_traditional_phase4_PENDING/ARCHIVE_PHASE3_RECEIPT.json','explicit_PH3_postcommit_receipt_PH4_admitted',unpinned=True)")
change("if any(x>34 for x in nums):exclude(p,'R35plus_container_namespace_not_traversed');continue","if any(x>39 for x in nums):exclude(p,'R40plus_container_namespace_not_traversed');continue")
change("if nums and any(17<=x<=34 for x in nums):","if nums and any(x in CLOSED_ROUNDS for x in nums):")
src=src.replace("'closed_R17_R34_'","'closed_R35_R36_R38_R39_'")
change("for rel in ['SPR_AUDIT/ACTIVE_BOX_QP_V3','SPR_AUDIT/ASQP_V3','FRONT_RANGE_PROPOSAL_V1','heading_hold_controller_v1.py','streamed_trace_rows_v1.py']:exclude(S/rel,'explicit_parent_active_exclusion')","for rel in ['ROUGH_WORLD_LEG_V1','prepare_world_leg_v1.py','run_world_leg_case_v1.py','MINIHOP_AUDIT_V2','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py','run_minihop_case_v2.py','CONTINUATION_STAGE1_DELIVERY.md']:exclude(S/rel,'explicit_parent_active_future_exclusion')")
# Use artifact-specific attribution: object/source dual rows must not attach .o
# digest to .c; ZIP members are a virtual namespace, not host source admission.
a=src.index('    def walk(obj,producer,loc=');b=src.index('    def markdown_closure(',a)
src=src[:a]+'''    def walk(obj,producer,loc='$',source_context=False):
        if producer.name=='PACKAGE_MANIFEST.json' and (loc.startswith('$.files') or loc.startswith('$.omitted')):return
        if isinstance(obj,dict):
            digest=next((obj[k] for k in ('SHA','sha256','SHA256','sha','original_sha256','source_SHA','output_sha256','producer_SHA') if isinstance(obj.get(k),str) and HEX.fullmatch(obj[k])),None)
            object_value=obj.get('object',obj.get('object_path'))
            keys=('object','object_path') if digest and isinstance(object_value,str) else ('path','file','source','source_path','source_file','output','original_path','artifact','archive','npz_path','raw_path')
            for k in keys:
                val=obj.get(k)
                if digest and isinstance(val,str) and not val.startswith(('http://','https://')):
                    target=resolve(val,producer);producer_claim(target,digest,producer,loc+'.'+k,obj.get('bytes',obj.get('size_bytes',obj.get('size'))))
                    if source_context:add(target,'named_executed_source_manifest_or_sealed_index_dependency',digest,str(producer),False)
            if isinstance(object_value,str) and isinstance(obj.get('source'),str) and isinstance(obj.get('source_SHA'),str) and HEX.fullmatch(obj['source_SHA']):add(resolve(obj['source'],producer),'explicit_source_SHA_separate_from_object_SHA',obj['source_SHA'],str(producer),False)
            for key,val in obj.items():
                context=source_context or key.lower() in ('source','sources','files','source_files','source_hashes','source_and_evidence_sha256','frozen_source','source_closure','seal_anchors_verified')
                if isinstance(val,str) and HEX.fullmatch(val) and ('/' in str(key) or '\\\\' in str(key)):
                    target=resolve(str(key),producer);producer_claim(target,val,producer,loc+'.'+str(key))
                    if context:add(target,'named_source_hash_mapping_dependency',val,str(producer),False)
                walk(val,producer,loc+'.'+str(key),context)
        elif isinstance(obj,list):
            for i,v in enumerate(obj):walk(v,producer,loc+'['+str(i)+']',source_context)
''' + src[b:]
change("new_round=any(17<=n<=34 for n in round_ids)","new_round=any(n in CLOSED_ROUNDS for n in round_ids)")
change("any(int(x)>34 for x in ROUND.findall(e['source_relative']))","any(int(x)>39 for x in ROUND.findall(e['source_relative']))")
src=src.replace('prior_PH1_PH2_Git_references','prior_PH1_PH2_PH3_Git_references').replace('prior_PH1_PH2_Git_byte_SHA','prior_PH1_PH2_PH3_Git_byte_SHA').replace('historical_PH1_PH2_case_reference_reports_not_new_cases','historical_PH1_PH2_PH3_case_reference_reports_not_new_cases')
src=src.replace("'PH3_SOURCE_PREPARATION_ONLY_NOT_COMMITTED'","'PH4_SOURCE_PREPARATION_ONLY_NOT_COMMITTED'").replace("'through_R34_end_by_parent_written_authorization'","'R35_R36_failures26cases_R38six_R39four_plus_named_components_by_written_authorization'").replace("'containers_rounds':[17,34]","'containers_rounds':sorted(CLOSED_ROUNDS)").replace("'owner_base_expected':'02b5ff84b905a4e40f207a44b0491aeff2f79b7e'","'owner_base_expected':'fa6838807f4d69d2b8ac52300d74ad40f365d2ed'")
src=src.replace("'R35plus_container_namespace_not_traversed'","'R40plus_container_namespace_not_traversed'").replace("'R35_in_continuation_only_not_experiment_admission':True","'R40plus_unrun_or_active_excluded':True").replace("'R35 handoff only, all source/experiment excluded here'","'R35 lost trace/counter not fabricated; only saved config/abort evidence'").replace("'R35_excluded_despite_CONT_R34_handoff':True","'R35_software_loss_not_capability_zero_ofN_or_reconstructed':True").replace("'old_phase1_phase2_records_replayed':False","'old_phase1_phase2_phase3_records_replayed':False")
# Keep oldCONT_R34 section cutoff as historical context. Do not follow newround4
# continuation, even if closed package text links it.
change("p=Path(p).resolve();bad=forbidden(p)","p=Path(p).resolve();bad=forbidden(p)\n        if p.parent==S and p.name.startswith('CONTINUATION') and p.name not in ROOT_DOCS:bad='continuation_not_in_exact_PH4_authority_allowlist'")
src=src.replace('PH4 section not traversed, no R35 case/source admission','oldR34cutoff narrative retained; R35/R36 now explicitly PH4admitted, newround4/R40plus still excluded')
ast.parse(src);dest.write_text(src,encoding='utf-8');print({'new_capture_script':str(dest),'SHA':hashlib.sha256(dest.read_bytes()).hexdigest(),'base_script_unchanged_SHA':hashlib.sha256(old.read_bytes()).hexdigest(),'AST_only_no_capture_yet':True})
