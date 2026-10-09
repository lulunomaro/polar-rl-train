"""Record actual retention regression and append an evidence-only central handoff."""
from pathlib import Path
import hashlib,json,os,statistics,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
read=lambda p:json.loads(p.read_bytes())
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
def dump(name,v):
    p=R/name;assert not p.exists(),('Preserve existing report',name)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p
def main():
    assert not (R/'METADATA_SYNCED.json').exists(),'Already synced; do not repeat'
    v=read(R/'REVIEW.json');c=read(R/'COLLECTED.json');block=v['block1']
    directions={}
    for role in ('previous32053','candidate'):
        rows=v['retention']['world'][role]['world_target']['rows'];directions[role]=[]
        for yaw in (-2.,-1.,1.,2.):
            a=[x for x in rows if x['command_yaw_rad_s']==yaw]
            directions[role].append(dict(yaw=yaw,count=len(a),original_factual_pass=sum(x['pass_'] for x in a),mean_cross_m_s=statistics.mean(x['cross_m_s'] for x in a),cross_range_m_s=[min(x['cross_m_s'] for x in a),max(x['cross_m_s'] for x in a)],mean_along_m_s=statistics.mean(x['along_m_s'] for x in a),mean_yaw_rad_s=statistics.mean(x['observed_yaw_rad_s'] for x in a),complete_signed_circle_count=sum(x['cycles'] for x in a)))
    diagnosis=dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK1-MATCHED-20261009',checkpoint=v['source'],source_count=313,snapshot_count=57,
        task_model_data_review_complete=True,terrain_same_scope_functional_evidence_accepted=True,
        significant_inherited_world_skill_regression_observed=True,no_full_skill_or_terrain_graduation_claim=True,
        directions=directions,world_original_factual_count_before=63,world_original_factual_count_after=16,total_world_cases=64,
        cross_max_abs_m_s_before=.05160225683439647,cross_max_abs_m_s_after=.12670850688204474,
        negative_pure4pi_original_signed_tolerance_count_before=5,negative_pure4pi_original_signed_tolerance_count_after=0,total_negative_pure4pi_cases=8,
        original_tolerances=dict(world_net_along_cross_m_s=.05,signed_yaw_rad_s=.2),new_graduation_percentage_added=False,
        physical_or_integrity_failure_observed=False,baseline_candidate_initial_root30q_parameters_recipes_assignment_feedback_age_same=True,
        actual_new_case_scope='3060; terrain seed20260928/80env and flat80-spin88-world88 seed20261002; white_v3; 1500control15s; exact existing packages',
        causal_status='Measured functional regression; narrowing learning commands to stand/BODYvx+-0.3/yaw0 is a plausible forgetting explanation, not an ablation-proven cause',
        E0_is_frozen_and_not_overwritten=True,E1_is_not_default_whole_robot_policy=True,
        current_second_block='Protect existing original scheduled own complete save. Do not hotpatch, force-kill, clear active or append a third gentle block',
        next_boundary='Independently review block2 own fullsave/accounting and all four planned completed cases. If same systematic regression persists without recovery, use an explicitly selected earlier balanced behavior-reviewed E1 source (32053 is a qualified candidate) for bounded corrective/progressive work; do not promote by maxiter/reward or claim regression harmless. Keep E0 frozen; do not revive optional93/94 or quota-mixed20k proposal',
        new_geometry='003 E1-G1 10mm CAD-derived continuous wave first; new ground/contact/reset/explicit geometry transition/fullresume contracts and necessary SDK/native/PPO scope remain required. CPU preparation is allowed while current trainer remains live; no new GPU/PPO authority before natural saved/settled boundary',
        revision_refs=['MOD4-RM-TERRAIN-CURRICULUM-REVISION-003','MOD4-RM-OUTER-CURB-AND-ROUGH-GEOMETRY-CLARIFICATION-002','MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001'],
        current_training_source_clock_DR_parameters_and_budget_unchanged=True,no_new_GPU_PPO_or_budget_operations=True,new_budget_seconds=0)
    dump('RETENTION_REGRESSION_DIAGNOSIS.json',diagnosis)
    dump('LOCAL_READER_REJECTIONS.json',dict(recorded_epoch=time.time(),production_unchanged=True,trials=[
        dict(id='E1-STABLE-BLOCK1-LOCAL-ROOT-LOOKUP-01',phase='rejected_local_path_reader',requested=['MOD4_E1_FINALIZED_STABLE_20261009','MOD4_S3_E1_PLANNED_BEHAVIOR_20261009','MOD4_E1_BEHAVIOR_ADMISSION_CPU_20261009'],result='rg reported directories absent before any GPU/ledger action; actual local root MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009 located by directory/file inventory',original_failed_paths_preserved=True),
        dict(id='E1-STABLE-BLOCK1-MASTER-HEADING-LOOKUP-01',phase='rejected_local_heading_reader',error='ValueError: substring not found',operation="s.index('## S3') / s.index('## S4')",functional_direction_rows_were_printed_before_exception=True,repair='Read actual numbered master sections with rg, no source or tolerance change'),
        dict(id='E1-STABLE-BLOCK1-OPTIONAL-ENV-PATH-LOOKUP-01',phase='rejected_local_path_reader',requested='MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/actual_source/isaac/mod4/e1_terrain_env.py',result='Get-Content path does not exist; optional preparation read only; no candidate generated or launched')]))
    charged=block['unique_completed_segment'][0]['accounted_through_epoch']-block['unique_completed_segment'][0]['started_epoch']
    note=f'''# E1 gentle block1 actual route and inherited-skill review

Own complete model32521 SHA498bd8813bc8957ff0c1f8f306c864472c4175455589ad8f9cd17a1c77bacd10 is CPU96 finite in the original completed receipt, bound to PID1718708, source313 and57 independently byte-verified snapshots. The first stable block made469 actual PPO updates/11256 control/225120000 environment policy steps/45024 exact physical callbacks. Ordinary/closure/integrity/unknown/nonfinite and STOP are absent; peak closure0.923257903mm. Declared time_out/route truncations have exact union coverage, not task failures. The original parent uniquely settled{charged:.9f}s including load/save/exit. This review does not charge or clear that segment.

Four existing completed no-learning3060 cases were collected, with all eight probe/result JSON byte-exact against the4090 bridge. The unchanged gentle route uses80env/seed20260928 and the inherited flat80/spin88/world88 use seed20261002/white_v3, each1500 control/15s and their exact existing immutable packages. The184040642-byte candidate route NPZ SHA9b0e9d5ac88c3d98c74834c24df9319829be3cc8bb0ca570efaf2e8f2369ec2b is independently reviewed and indexed, never committed as raw. Previous32053 complete cases are reused, without GPU replay. Initial root/30q/parameters/geometry/recipes/assignments and old-skill feedback ages pair exactly; full callbacks/processed-target formula, actual D5-D7 parameter readback, actor35/cleancritic38/no teacher and all signed circles are checked. Signed route displacement uses pre-reset root differences, excluding reset teleportation; ordinary failures and declared truncations are distinct, and independent contact impulse meanload uses the original0.1N tolerance. No90/95/100 admission line or cross-GPU bitexact claim is added.

Gentle forward/reverse/stand remain functional: means0.293626130/-0.295300648/-0.000191125m/s, tracking errors0.021386715/0.019901760/0.012962752m/s, zero ordinary terminations and108 declared route truncations. The source32053 values and all original strict flags are retained. This modest route improvement does not erase a substantial old-world behavior regression: the original factual world count falls63/64 to16/64. All24 positive-yaw2 and24 negative-yaw2 rows now fail the original cross tolerance, with sign-consistent mean cross+0.090348513/-0.096247399m/s; the worst absolute complete-circle netcross is0.126708507 versus0.051602257m/s. Yaw+-1 rows remain within their original factual bounds. Along progression and signed yaw remain finite with correct directions; this is not a newly observed GPU/physics/contact integrity fault. Pure positive4pi remains8/8, negative4pi becomes0/8 from5/8; negative mean is-12.260233641rad/s against the original signed tolerance. Flat+-1.5 errors rise to0.099916682/0.090132728m/s. All per-environment values, complete signed circles, raw and false flags remain in the report.

Learning only stand/BODYvx+-0.3/yaw0 is a plausible explanation for loss of unused fast/world skills, but this observation is not a causal ablation. E0 remains frozen, and E1 is a terrain specialist, not the whole robot's default policy. The regression still requires explicit diagnosis and source selection; model/data admissibility is not functional retention success. Protect the already running second block's original full-save boundary, without hotpatch/kill/clearactive or a third gentle block. At its natural complete/settled boundary review its four real cases. If the same systematic regression persists without recovery, select an earlier balanced fully reviewed E1 source for bounded corrective/progressive work rather than repeatedly adding gentle PPO. The already qualified32053 is a candidate, not a preselected replacement of the active source. Future003 E1-G1 10mm continuous CAD-derived wave requires actual new geometry/ground/contact/reset/explicit geometry transition/fullresume contracts. The proposal70/20/10quota mixture remains not adopted; optional93/94 and MuJoCo remain paused.003/002 and001 effective spin exclusions are preserved, with no new master/S8 approval.

The current3060 worker identity/creation/argv/sourceSHA is proven and has no current attention; it was not restarted. Original clock, full D0-D7, hardware envelope and canonical828000s remain unchanged, no new GPU/PPO/queue/canonical transaction and budget extension0. All completed cases are reused. The saved collector/reviewer reports, source and local rejected path/heading readers are captured in Git together; neither reader errors nor old false flags are silently dropped. Large weights/NPZ/assets remain path/size/SHA indexes and originals retained. Central synchronization is evidence/next-boundary handoff only, with active learning/evaluation/budget fields preserved. Git recording is independent of running training.
'''
    p=R/'REPORT.md';assert not p.exists();p.write_text(note,encoding='utf8')
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret
    sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
    conn=connect()
    try:
        with conn.open_sftp() as s:
            root='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
            context={}
            for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json'):
                raw=s.open(root+name).read();a=json.loads(raw);context[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
                if name=='PLAN_APPROVAL.json':assert a['approved'] and a['approved_plan_sha256']==MASTER and 'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in a['plan_annotations']
                if name=='EXECUTION_TRACKS.json':assert 'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in a['curriculum_annotations']
                if name=='MOE_PLAN_EXECUTION_CURRENT.json':assert a['next_E1_RM_terrain_work_order']['id']=='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003'
            uploaded=[]
            for local,name in [(R/'REVIEW.json','E1_GENTLE_BLOCK1_MATCHED_REVIEW.json'),(R/'RETENTION_REGRESSION_DIAGNOSIS.json','E1_GENTLE_BLOCK1_RETENTION_REGRESSION_DIAGNOSIS.json'),(R/'REPORT.md','E1_GENTLE_BLOCK1_MATCHED_REPORT.md')]:
                dest=root+name
                try:s.stat(dest)
                except FileNotFoundError:pass
                else:raise AssertionError('New report already exists; do not overwrite '+name)
                raw=local.read_bytes()
                with s.open(dest,'xb') as out:out.write(raw)
                assert s.open(dest).read()==raw
                uploaded.append(dict(source=str(local),remote=dest,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),bytes_exact=True))
            handoff=root+'LATEST_HANDOFF.md';before=s.open(handoff).read()
            marker='E1-STABLE-BLOCK1-MATCHED-20261009';assert marker.encode() not in before
            addition=('\n\n## '+marker+' actual bounded retention diagnosis\n'
                'Own completed32521/source313/57snapshot/CPU96 and469updates are verified; four completed3060 cases and full route raw independently reviewed. Gentle signed traversal remains functional, but inherited world original factual count63/64->16/64 with all yaw+-2 rows outside unchanged cross tolerance, negative pure4pi5/8->0/8; do not relabel as mature or physical failure. See E1_GENTLE_BLOCK1_MATCHED_REVIEW.json, E1_GENTLE_BLOCK1_RETENTION_REGRESSION_DIAGNOSIS.json and E1_GENTLE_BLOCK1_MATCHED_REPORT.md. Active second block keeps original own fullsave boundary; no hotpatch/kill/clearactive/third gentle block. Next actual block2 review/source selection and003 newscope contracts before progression. No70/20/10quota candidate, no paused93/94 or MuJoCo. Original active learning/evaluation/budget records byte unchanged.\n').encode()
            assert s.open(handoff).read()==before,'Concurrent handoff change; refuse overwrite'
            with s.open(handoff,'ab') as out:out.write(addition)
            after=s.open(handoff).read();assert after==before+addition
            for name,item in context.items():assert hashlib.sha256(s.open(root+name).read()).hexdigest()==item['sha256'],('Protected central metadata changed',name)
            dump('METADATA_SYNCED.json',dict(epoch=time.time(),trial_id=marker,uploads=uploaded,central_active_learning_evaluation_budget_files_byte_unchanged=context,handoff_before_sha256=hashlib.sha256(before).hexdigest(),handoff_after_sha256=hashlib.sha256(after).hexdigest(),append_exact=True,production_GPU_PPO_canonical_transactions=0,new_budget_seconds=0))
            print(json.dumps(dict(actual_retention_regression_diagnosed=True,central_reports_and_handoff_synced=True,source=v['source']['sha256'],active_block_not_interrupted=True,new_budget_seconds=0),ensure_ascii=True))
    finally:conn.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        dump('DIAGNOSIS_SYNC_01_ERROR.json',dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK1-DIAGNOSIS-SYNC-01',error=traceback.format_exc(),do_not_repeat_once_or_training=True));raise
