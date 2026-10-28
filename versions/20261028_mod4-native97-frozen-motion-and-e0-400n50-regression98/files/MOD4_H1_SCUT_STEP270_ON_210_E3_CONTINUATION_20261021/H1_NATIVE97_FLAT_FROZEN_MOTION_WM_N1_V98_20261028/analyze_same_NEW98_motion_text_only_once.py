from pathlib import Path
import json,math,os,sys,importlib.util
assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
S=Path(__file__).resolve().parent;T=S.parent;B=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028/payload';R=S/'reports'
index=json.loads((R/'FROZEN98_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes());rows={r['relative']:r for r in index['rows']}
def read(name):return json.loads(Path(rows[name]['local_path']).read_bytes())
status=read('case/episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json');pair=read('case/episode/FROZEN_WM_EIGHT_STEP_PAIRED_ACTUAL.json')
assert status['controls']==500 and status['physics_callbacks']==2000 and status['last_termination_terms']['values']['time_out'] and not any(v for k,v in status['last_termination_terms']['values'].items() if k!='time_out')
controls=[json.loads(line) for line in Path(rows['case/episode/ACTUAL_100HZ_CONTROLS.jsonl']['local_path']).read_text('utf8').splitlines()]
physics=[json.loads(line) for line in Path(rows['case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl']['local_path']).read_text('utf8').splitlines()]
assert len(controls)==500 and len(physics)==2001
import torch,numpy as np
sp=importlib.util.spec_from_file_location('same_admitted_flat_phase_text_analysis',B/'source/flat_jump_phase_objective_source_v1.py');phase=importlib.util.module_from_spec(sp);sys.modules[sp.name]=phase;sp.loader.exec_module(phase)
ages=torch.tensor([r['age_for_action'][0] for r in controls]);target=phase.FlatJumpPhase().targets(ages+1,torch.zeros_like(ages));input_target=phase.FlatJumpPhase().targets(ages,torch.zeros_like(ages))
reference=json.loads((B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json').read_bytes());neutral_z=reference['neutral_packed73'][2]
t=np.arange(1,501)*.01;state=[r['terminal_pre_reset']['state'] for r in controls];actual_z=np.array([r['root13_sdk_xyzw'][2] for r in state]);actual_bottom=np.array([r['metrics']['wheel_bottom_above_floor_m'] for r in state]);mean=np.array([r['mean6'] for r in controls]);applied=np.array([r['physical_applied_processed6'] for r in state]);flight=target['flight'].numpy();goal_z=neutral_z+input_target['height'].numpy()
both_bottom=[min(row['state']['metrics']['wheel_bottom_above_floor_m']) for row in physics]
wm1=[abs(pred-act) for row in controls for pred,act in zip(row['frozen_WM_one_step']['predicted_wheel_bottom'],row['frozen_WM_one_step']['actual_wheel_bottom'])]
wm8=[abs(pred-act) for row in pair['rows'] for pred,act in zip(row['predicted_wheel_bottom'],row['actual_wheel_bottom'])]
summary=dict(passed=True,case_seed=20260928,controls=500,callbacks=2000,termination='original time_out only',flat_events=status['flat_real_physics_events']['lifetime'],actual_both_wheel_bottom_peak_m=max(both_bottom),actual_body_height_range_m=[float(actual_z.min()),float(actual_z.max())],current_input_body_height_goal_range_m=[float(goal_z.min()),float(goal_z.max())],neutral_body_height_from_source_m=neutral_z,flight_body_actual_minus_current_input_goal_range_m=[float((actual_z-goal_z)[flight].min()),float((actual_z-goal_z)[flight].max())],all_sampled_requested_flight_body_targets_below_actual=bool(np.all((goal_z-actual_z)[flight]<0)),WM_teacher_actual_action_one_step_wheel_bottom_max_abs_error_m=max(wm1),WM_teacher_actual_action_eight_step_wheel_bottom_max_abs_error_m=max(wm8),WM_accuracy_scope='This single grounded case and its executed actions only; no airborne or counterfactual accuracy proved',mean_action_min6=mean.min(0).tolist(),mean_action_max6=mean.max(0).tolist(),actual_applied_min6=applied.min(0).tolist(),actual_applied_max6=applied.max(0).tolist(),important_phase_scope='Recorded public_request is original270 phase. Plot uses actual flat private phase from original source and actual ages, not that public flag.',finding='Body moves while both wheels remain on floor. Fixed neutral-body-height goal is below the observed extended standing body during both requested flat-flight intervals. This is an input/reward geometry inconsistency candidate, not proven sole cause.',no_actor_WM_forward_model_PT_read_hash_new_physics_training_or_remote=True,originals_retained=True)
with (R/'NEW98_SAME_CASE_MOTION_GOAL_AND_WM_TEXT_ANALYSIS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(summary,f,indent=2,allow_nan=False)
with (R/'LOCAL_SOURCE_READER_MISSING_FILENAME_ERROR_AND_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(error='Get-Content: own_flat_jump_phase_v1.py does not exist',correct_actual_import_source='flat_jump_phase_objective_source_v1.py',no_remote_model_or_training_effect=True),f,indent=2)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family']=['Microsoft YaHei'];plt.rcParams['axes.unicode_minus']=False
fig,axs=plt.subplots(3,1,figsize=(11,8.5),sharex=True,constrained_layout=True)
axs[0].plot(t,target['height'].numpy()*1000,'k--',label='任务要求的轮底高度');axs[0].plot(t,actual_bottom[:,0]*1000,label='左轮实际最低点');axs[0].plot(t,actual_bottom[:,1]*1000,label='右轮实际最低点');axs[0].set_ylabel('轮底净空 (mm)');axs[0].set_ylim(-2,56);axs[0].legend(loc='upper right',ncol=3);axs[0].set_title('最新97策略的一次真实仿真：有跳跃请求，双轮仍贴地')
axs[1].plot(t,actual_z,label='实际机身高度');axs[1].plot(t,goal_z,'--',label='输入给策略的当前机身高度目标');axs[1].set_ylabel('机身高度 (m)');axs[1].legend(loc='upper right');axs[1].text(.02,.05,'目标高度来自固定初始姿态；请求期间低于实际伸腿站姿。因果影响待验证。',transform=axs[1].transAxes,fontsize=10)
for i in range(4):axs[2].plot(t,applied[:,i],label=f'腿关节动作 {i+1}')
axs[2].set_ylabel('实际施加的归一化动作');axs[2].set_xlabel('实际仿真时间 (s)');axs[2].legend(loc='upper right',ncol=4)
for ax in axs:
 ax.grid(alpha=.25);ax.set_xlim(0,5)
 for start in (2.,4.5):ax.axvspan(start,start+2*math.sqrt(2*9.81*.05)/9.81,color='orange',alpha=.13)
fig.suptitle('固定种子20260928 · 500控制步 / 2000物理回调 · 仅超时结束\n橙色为平地跳请求；真实起跳/达高/落地/站稳均为0',fontsize=13)
figure=S/'NEW98_ACTUAL_MOTION_AND_INPUT_HEIGHT_GOAL.png';fig.savefig(figure,dpi=155);plt.close(fig)
print(json.dumps(summary,ensure_ascii=False));print(str(figure))
