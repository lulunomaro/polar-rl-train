from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;N=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D=S/'display';D.mkdir();(D/'reports').mkdir();V=T/'H1_USER_MUJOCO_REAL_BLUE_IMAGINATION_V115_20261029'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
qcpu=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1/reports/NATIVE116_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json';qual=read(qcpu);assert qual['passed'];model=qual['model']
case_report=S/'reports/FROZEN118_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json';case=read(case_report);assert case['actual_waited_exit']==0 and case['case']['passed'] and not case['errors']
rows=read(S/'reports/FROZEN118_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json')['rows'];control=next(x for x in rows if x['relative'].endswith('/ACTUAL_100HZ_CONTROLS.jsonl'))
B=N/'payloads/seed27';manifest=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mr=read(manifest)
q=dict(source_payload=str(B),manifest=str(manifest),manifest_SHA=H(manifest),source_PY_rows=[x for x in mr['files'] if x['relative'].startswith('source/') and x['relative'].endswith('.py')],qualified116_CPU=str(qcpu),qualified116_CPU_SHA=H(qcpu),formal_SHA=model['SHA'],formal_bytes=model['bytes'],formal_local_path=model['local_path'],actual_case_report=str(case_report),actual_case_report_SHA=H(case_report),raw_control_producer=control,native_iteration=model['original_producer']['updates'])
(S/'PURPOSE118_TYPED_DISPLAY_BINDING.json').write_text(json.dumps(q,indent=2),encoding='utf8')
old=(V/'prepare_user_visualization.py').read_text(encoding='utf8')
a="q=read(T/'H1_NATIVE111_ACTUAL_ACTION_WM_FORWARD_CPU_V113_20261029/PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json')";assert old.count(a)==1
src=old.replace(a,"q=read(HERE.parent/'PURPOSE118_TYPED_DISPLAY_BINDING.json')").replace('T=HERE.parent','T=HERE.parent.parent').replace('H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029','H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029')
for a,b in [('qualified111','qualified116'),('native111','native116'),('frozen111','frozen116'),('actual112','actual118'),('recorded112','recorded118'),('Recorded112','Recorded118'),('111 Pi','116 Pi'),('case112','case118'),('USER_ACTUAL112_AND_BLUE111_DISPLAY_POSES.npz','USER_ACTUAL118_AND_BLUE116_DISPLAY_POSES.npz'),("native['iteration']==18597","native['iteration']==20809"),('display_is_prior_case_not114=True','display_is_latest_qualified116=True')]:src=src.replace(a,b)
a="require(len(records)==2000 and [r['control'] for r in records]==list(range(1,2001)),'entire20s real case')";assert src.count(a)==1
src=src.replace(a,"n=len(records);require(33<n<=2000 and [r['control'] for r in records]==list(range(1,n+1)),'actual complete recorded case until its original termination')")
a="require([r['age_for_action'] for r in records]==list(range(2000)),'unaltered original action clock')";assert src.count(a)==1
src=src.replace(a,"require([r['age_for_action'] for r in records]==[[i] for i in range(n)],'unaltered original one-element action clock')")
src=src.replace('(2000,127)','(n,127)').replace('(2000,31)','(n,31)').replace('(2000,86)','(n,86)').replace('(2000,31,3)','(n,31,3)').replace('(2000,31,4)','(n,31,4)').replace('reshape(2000,31,3,3)','reshape(n,31,3,3)').replace('rows=2000','rows=n').replace('np.arange(1,1968,5','np.arange(1,n-32,5')
src=src.replace("actual_case='112 frozen116 mean policy,2000controls20s; recordedPhysX,not MuJoCo dynamics'","actual_case=f'118 latest116 frozen mean policy,{n}controls/{n*.01:.2f}s until original termination; recordedPhysX,not MuJoCo dynamics'")
src=src.replace('actual_true270_success=False',"actual_true270_counter=case['case']['result']['original270_terminal_physics_events'],actual_controls=n,actual_duration_s=n*.01,actual_both_wheel_peak_m=float(bottom.min(axis=1).max()),actual_root_progress_m=float(pos[-1,0,0]-pos[0,0,0])")
src=src.replace('not_current114_rollout=True','latest_qualified116_policy_actual118=True')
assert '18597' not in src and "range(2000)" not in src and '(2000,' not in src
ast.parse(src);(D/'prepare118_latest116_actual_and_blue_CPU_once.py').write_text(src,encoding='utf8',newline='\n')
with (S/'reports/LOCAL118_VISUAL_TYPED_SOURCE_BEFORE_MODEL_READ.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_SHA=hashlib.sha256(src.encode()).hexdigest(),binding_SHA=H(S/'PURPOSE118_TYPED_DISPLAY_BINDING.json'),raw_controls_reads=0,checkpoint_reads=0,latest116_model_SHA=model['SHA'],actual_case_controls=case['case']['result']['controls'],variable_original_termination_length_supported=True,age_one_element_reader_fixed_before_read=True,one_new_CPU_visual_decode_planned=True,no_old112raw_or_model_read=True),f,indent=2)
print(json.dumps(dict(source_ready=True,display=str(D),actual_controls=case['case']['result']['controls'],model=model['SHA'])))
