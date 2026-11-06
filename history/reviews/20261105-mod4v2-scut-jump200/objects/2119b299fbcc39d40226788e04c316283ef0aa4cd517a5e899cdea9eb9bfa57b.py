"""Record already completed native evaluations; no model loads or physics."""
from pathlib import Path
import hashlib,json,time,copy
N=Path(__file__).resolve().parent
S=N.parents[1]
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
A=N/'supermimic_final5936_semantic_repair_1h'
R=A/'reports'
read=lambda p:json.loads(p.read_bytes())
f=read(R/'POSTROUND_FULL_RETURNED.json')['files']
diag=read(R/'SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json')
assert diag['passed'] and read(R/'POSTROUND_COMPLETED.json')['complete']
assert f['OWNER_EXIT.json']['original_leases_released']
teacher=read(N/'scut_teacher_verify/VERIFICATION_SUMMARY.json')
visual=[]
for parent in ['recorded_native','recorded_native_late']:
    visual+=read(A/'evaluation'/parent/'RENDER_REPORT.json')['media']
visual_review={'epoch':time.time(),'model_SHA':diag['checkpoint']['SHA'],'media':visual,'current_model_native_vision_reviewed_all4':True,'observations':['Early spawn descent followed by support and compression/extension','Late env0/1 short hops and turning before near edge; env40 falls at5.18s; env41 rocks and hops before edge','No whole-wheel clearance or top landing; no skill inference from upward flag'],'saved_quaternion':'wxyz','new_physics':0,'new_policy_inference':0}
(R/'ACTUAL_NATIVE_REVIEW.json').write_text(json.dumps(visual_review,ensure_ascii=False,indent=2),encoding='utf-8')
final=f['production/FINAL.json'];owner=f['OWNER_EXIT.json']
boundary={'epoch':time.time(),'status':'CLOSED_FINAL6845_ALL80_0SUCCESS_NATIVE_REVIEWED','checkpoint':diag['checkpoint'],'source_iteration':5936,'new_verified_H32':diag['learner']['counts']['pi_bptt_optimizer_steps']-5904,'new_model_rounds':6845-5936,'new_control_samples':final['worker_new_control_samples'],'timing':{'window_training_control_steps_per_second':final['window_training_control_steps_per_second'],'worker_control_steps_per_second':final['worker_control_steps_per_second'],'owner_elapsed':owner['actual_elapsed_seconds'],'owner_control_steps_per_second':final['worker_new_control_samples']/owner['actual_elapsed_seconds']},'new_numerical':1418-1232,'new_constraint':1609-1555,'all80':diag['all80'],'last_value':diag['learner']['semantic_repair']['last_value'],'unique_final_PT_diagnosis_completed':True,'do_not_repeat_final_PT_decode':True,'native_all4_reviewed':True,'collector62016_exited':True,'owner':owner,'SSH_FREE':read(R/'NEWTON_FORMAL_POSTROUND_RETURN_SSH_FREE.json'),'cumulative_upper_seconds':71437.70571112633+owner['actual_elapsed_seconds'],'cumulative_kind':'Conservative100h ceiling includes prior unknown reboot upper; not actualGPUcost','current_training_and_readers':0,'next':'Complete human requested original SCUT teacher/standing extension comparison; do not restart unchanged failedH32 or old once'}
(R/'FINAL6845_BOUNDARY_REVIEW.json').write_text(json.dumps(boundary,ensure_ascii=False,indent=2),encoding='utf-8')
for path in [S/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    state=read(path)
    if state.get('current_training')!=boundary['status']:
        state['pre_final6845_current_training']=copy.deepcopy(state.get('current_training'))
    state['current_training']=boundary['status']
    state['current_training_root']=str(A)
    state['local_controller']=None
    state['local_controller_role']='No live producer or collector; exact62016 completed and exited'
    state['final6845_boundary']=boundary
    semantic=state['supermimic_semantic_repair']
    semantic['status']=boundary['status'];semantic['current_checkpoint']=diag['checkpoint'];semantic['current_owner_cost_pending']=False
    semantic['final_boundary_review']=str(R/'FINAL6845_BOUNDARY_REVIEW.json')
    semantic['cumulative_upper_seconds_after']=boundary['cumulative_upper_seconds']
    semantic['observed_new_numerical']=boundary['new_numerical'];semantic['observed_new_constraint']=boundary['new_constraint']
    semantic['next']=boundary['next']
    state['scut_teacher_actual_verification']={'epoch':time.time(),'human_requests':['你验证一下华南虎教师能否跳台阶','测试一下站着腿伸直上台阶'],'root':str(N/'scut_teacher_verify'),'report':str(D/'SCUT_TEACHER_NATIVE_AND_STANDING_EXTENDED_20261106.md'),'verdict':teacher['verdict'],'actual_native_terrain':teacher['actual_native_terrain'],'no_MOD4_teacher_distillation_started':True,'all_original_failures_preserved':True}
    state['next']=boundary['next']
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')

# All teacher binary artifacts are references only, including plots, assets and trajectories.
rows=[]
for p in (N/'scut_teacher_verify').rglob('*'):
    if p.is_file() and p.suffix.lower() not in ['.py','.md','.json','.log','.txt']:
        with p.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
        rows.append({'path':str(p),'bytes':p.stat().st_size,'SHA':sha,'external_artifact':True,'model_loads_for_archive':0})
(N/'scut_teacher_verify/ARTIFACT_INDEX.json').write_text(json.dumps({'epoch':time.time(),'files':rows},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'status':boundary['status'],'teacher200':teacher['verdict'],'cumulative_upper':boundary['cumulative_upper_seconds'],'binary_refs':len(rows)},ensure_ascii=False))
