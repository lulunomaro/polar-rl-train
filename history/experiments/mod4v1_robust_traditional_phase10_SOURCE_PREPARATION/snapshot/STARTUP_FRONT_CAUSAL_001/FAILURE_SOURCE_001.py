"""One allowed startup control-trace pass only; no physics trace or project imports."""
from pathlib import Path
import datetime,hashlib,json,math,traceback
D=Path(__file__).resolve().parent;T=D.parent;B=T/'results/startup_front065_nominal_v1';OPENS=0;ROWS=0
TIMES=(0.,.25,.5,1.,1.5,2.,2.25,3.,4.,5.,6.)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def pick(d,keys):
 return next((d[k]for k in keys if k in d and d[k]is not None),None)
def num(x):return type(x)in(int,float)and math.isfinite(x)
def vec(v,n):return isinstance(v,(list,tuple))and len(v)==n and all(num(x)for x in v)
def maximum(v):return max(abs(x)for x in v)if isinstance(v,(list,tuple))and v and all(num(x)for x in v)else None
def main():
 global OPENS,ROWS
 assert not(D/'SOURCE_PREEXEC.json').exists(),'Once only: preserve partial reads, never reopen'
 err=load(B/'ERROR.json');cfg=load(B/'config.json');cachep=T/'STARTUP_STAND_V1/front_admission001/FINAL_ENTRY_REVIEW_002.json';cache=load(cachep)
 assert err['controls']==601 and err['physics_steps']==12020 and err['partial_trial_passed']is False
 assert cfg['case_id']==B.name and cfg['nominal']is True and cfg['seed']==0 and cfg['duration_s']==10.
 expected_core='e0f8105b32f69738b681a0d442da07e07021b22cbae7f1f993d33e1643aa7c52'
 assert cache['controller_review_reused']['SHA']==expected_core
 p=B/'trace.jsonl';claim=err['trace_prefix'];assert Path(claim['path']).resolve()==p.resolve()and p.stat().st_size==claim['bytes']==2741033
 before=[{'path':str(q),'bytes':q.stat().st_size,'SHA':sha(q)}for q in(D/'METHOD_PREDECLARED.md',D/'analyze.py',B/'ERROR.json',B/'config.json',cachep)]
 new(D/'SOURCE_PREEXEC.json',{'kind':'ONE_CONTROL_TRACE_ONLY_LOCKED_BEFORE_RAW_OPEN','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'small_inputs':before,'cached_controller_SHA':expected_core,'cached_review_record_not_current_controller_body_rehash':True,'permitted_trace':claim,'unread_physics_producer_reference':err['physics_prefix'],'limits':{'trace_opens':1,'trace_rows':601,'physics_opens':0},'no_raw_rehash_project_model_FK_PHY_QA_Git_agents':True,'PH10pending':True})
 rows=[];OPENS+=1;assert OPENS==1
 with p.open('rb')as f:
  for raw in f:
   ROWS+=1;assert ROWS<=601,'Control read budget exceeded'
   z=json.loads(raw);rows.append(z)
 assert ROWS==601
 for i,z in enumerate(rows):assert abs(z['command_time_s']-i*.01)<1e-8
 def snap(z):
  ph=z['phase'];assert isinstance(ph,dict)
  be=pick(z,('grade_before','before','ground_truth_before'));af=pick(z,('grade_after','after','ground_truth'));be=be if isinstance(be,dict)else{};af=af if isinstance(af,dict)else{}
  state=z['estimated14'];assert vec(state,14)
  enc=pick(z,('encoder_q4','encoder4','joint_pos4'));ref=pick(ph,('reference_q4','q_ref4','qref4','reference_q4_rad'))
  if ref is None:
   candidates={k:v for k,v in ph.items()if 'ref'in k.lower()and 'qd'not in k.lower()and 'vel'not in k.lower()and vec(v,4)}
   if len(candidates)==1:ref=next(iter(candidates.values()))
  gyro=pick(z,('raw_gyro','gyro_body','raw_gyro_body','omega_body'));tau=z.get('requested_tau6')
  je={k:v for k,v in z.items()if('joint'in k.lower()and'error'in k.lower())or'qerr'in k.lower()}
  return {'command_time_s':z['command_time_s'],'sensor_source_s':pick(z,('sensor_time_s','sensor_timestamp_s')),'root_post_s':pick(z,('root_post_s','time_s','time')),'phase':ph.get('phase'),'phase_log':ph,'actual_pitch_rad_PRE':be.get('pitch_true'),'actual_pitch_rad_POST':af.get('pitch_true'),'actual_roll_rad_POST':af.get('roll_true'),'estimated_pitch_rad':state[2],'estimated_roll_rad':z.get('estimated_roll'),'gyro_sensor_rad_s3':gyro,'gyro_sensor_norm_rad_s':math.sqrt(sum(v*v for v in gyro))if vec(gyro,3)else None,'root_Z_PRE_m':be.get('xyz',[None,None,None])[2],'root_Z_POST_m':af.get('xyz',[None,None,None])[2],'encoder_q4_sensor':enc,'current_reference_q4':ref,'encoder_minus_current_reference_q4_rad':[a-b for a,b in zip(enc,ref)]if vec(enc,4)and vec(ref,4)else None,'logged_private_joint_error_fields':je,'joint_error_epoch_boundary':'Private post-step target error versus nominal standing target is distinct from sensor-epoch encoder/current startup-reference error. No actual2k joint pose reconstructed.','requested_leg_Nm4':[tau[i]for i in(0,1,3,4)]if vec(tau,6)else None,'requested_wheel_Nm2':[tau[i]for i in(2,5)]if vec(tau,6)else None,'main_mean_N2':z.get('main_contact_mean_N2'),'main_min_N2':z.get('main_contact_min_N2'),'both_support_every_2k_sample':z.get('both_support_every_2k_sample'),'no_other_contact_in_control':z.get('no_other_contact_in_control'),'logged_stable_s':z.get('end_stable_s'),'private_grade_POST':af}
 phases={};trans=[];last=None
 for i,z in enumerate(rows):
  phase=z['phase'].get('phase');phases[phase]=phases.get(phase,0)+1
  if phase!=last:trans.append({'control_index':i,'command_time_s':z['command_time_s'],'from':last,'to':phase,'event':snap(z)});last=phase
 selected=[]
 for t in TIMES:
  i=min(range(len(rows)),key=lambda k:abs(rows[k]['command_time_s']-t));selected.append({'requested_epoch_s':t,'selected_index':i,'observed':snap(rows[i])})
 final=snap(rows[-1]);reasons={k:v for k,v in final['phase_log'].items()if any(a in k.lower()for a in('reason','fault','inhibit','static','ready'))}
 maxima=[max(abs(z['requested_tau6'][i])for z in rows)for i in range(6)]
 events={'status':'BOUNDED_SAVED_STARTUP_CONTROL_DIAGNOSIS_NOT_REPLACEMENT_RESULT','original_error_receipt':err,'config':cfg,'control_schema_keys':sorted(rows[0]),'phase_counts':phases,'phase_transitions':trans,'requested_timepoints':selected,'final':final,'observed_final_fault_or_ready_fields':reasons,'requested_abs_peak_tau6_Nm':maxima,'no_BALANCE_command_observed':phases.get('BALANCE',0)==0,'observed_controls':601,'producer_saved_consumed_physics_steps':12020,'planned_controls_not_imputed':1000,'raw_reads':{'trace_opens':OPENS,'trace_rows':ROWS,'physics_opens':0,'raw_hash_recomputed':False},'actual_control_fault_vs_reporting_error':'Final phase log records controller outcome before the saved post-processing FullDR.runtime_receipt AttributeError. No result.json or completed10s/0of1 robot-success statistic manufactured.','limits':'Only100Hz truth snapshots/ref/request and logged2k-bin force minima/noOther available. No contacts/2k posture/actual torque reconstructed from unread physics; no parameter choice or unique-cause claim.','PH10pending':True}
 new(D/'EVENTS.json',events)
 def fmt(v):
  if v is None:return 'UNKNOWN'
  if isinstance(v,float):return f'{v:.7g}'
  return json.dumps(v,ensure_ascii=False,separators=(',',':'))
 lines=['# 首次front启动：已保存控制轨迹诊断（不是重构result）','只读该新case的601行trace一次；68.9MB physics未打开；不重跑/不择gain，PH10pending。',f"原ERROR保存消耗601 controls /12020 physics steps；planned1000/20000不当作实际完成。后处理API错误：`FullDR.runtime_receipt`不存在，提示`queue_receipt`；原ERROR保留。",f"相位计数：`{fmt(phases)}`；末相位`{final['phase']}`；末fault/static/ready字段`{fmt(reasons)}`。",f"有BALANCE命令={not events['no_BALANCE_command_observed']}；因此本报告不给完整robot0/1成功率、不生成替代result。",'时间列为command/POST，两种q误差与PRE/POST保持分开；完整phase_log、qref/encoder及私有grade见EVENTS。','|目标t / 实际command / POST s|phase|实际pitchPOST / estimated rad|gyro rad/s3|rootZPOST m|encoder−currentref max rad|private joint error(站姿目标)|leg requestNm4 / wheel requestNm2|FnminN2 / noOther|','|---|---|---|---|---|---|---|---|---|']
 for e in selected:
  z=e['observed'];lines.append('|'+f"{e['requested_epoch_s']}/{fmt(z['command_time_s'])}/{fmt(z['root_post_s'])}"+'|'+str(z['phase'])+'|'+fmt(z['actual_pitch_rad_POST'])+'/'+fmt(z['estimated_pitch_rad'])+'|'+fmt(z['gyro_sensor_rad_s3'])+'|'+fmt(z['root_Z_POST_m'])+'|'+fmt(maximum(z['encoder_minus_current_reference_q4_rad']))+'|'+fmt(z['logged_private_joint_error_fields'])+'|'+fmt(z['requested_leg_Nm4'])+'/'+fmt(z['requested_wheel_Nm2'])+'|'+fmt(z['main_min_N2'])+'/'+fmt(z['no_other_contact_in_control'])+'|')
 lines+=['相位边界：'+fmt([{k:z[k]for k in('control_index','command_time_s','from','to')}for z in trans]),'请求六轴绝对峰值Nm（非实际电机力矩/电功率）：'+fmt(maxima),'接触信息仅是V2逐control保存的2k样本最小值/全bin noOther标记；没有geom/峰值/2k姿态推断。encoder/currentref为传感器与命令epoch；private误差字段是post-step模型对nominal目标，二者不混用。','自然落稳初始化不等站起；合成499帧通过不等实际接管。输入/限幅/相位关联只描述所保存一案，不选新策略/参数，也不由API后处理错误抹去原物理消耗。','[锁](<SOURCE_PREEXEC.json>) / [bounded事件](<EVENTS.json>) / [收据](<RECEIPT.json>)']
 assert len(lines)<=80
 (D/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
 assert all(sha(Path(z['path']))==z['SHA']for z in before),'Small input/source changed'
 receipt={'status':'COMPLETE_ONCE_STARTUP_FRONT_CONTROL_TRACE_ONLY_DIAGNOSIS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report_lines':len(lines),'report_SHA':sha(D/'REPORT.md'),'events_bytes':(D/'EVENTS.json').stat().st_size,'events_SHA':sha(D/'EVENTS.json'),'source_preexec_SHA':sha(D/'SOURCE_PREEXEC.json'),'small_sources_before_after_equal':True,'trace_opens':OPENS,'trace_rows':ROWS,'physics_opens':0,'producer_controls':601,'producer_physics_steps':12020,'no_replacement_result_or_robot_rate':True,'source_gain_gate_score_modified':False,'model_FK_PHY_QA_Git_agents_rawhash_calls':0,'PH10pending':True}
 new(D/'RECEIPT.json',receipt)
 print(json.dumps({'receipt':receipt,'phase_counts':phases,'transitions':[{k:z[k]for k in('control_index','command_time_s','from','to')}for z in trans],'final_fault_fields':reasons,'last_selected':{k:final[k]for k in('command_time_s','phase','actual_pitch_rad_POST','estimated_pitch_rad','root_Z_POST_m')},'schema_keys':sorted(rows[0]),'first_phase_keys':sorted(rows[0]['phase'])},ensure_ascii=True,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  tb=traceback.format_exc();n=1
  while(D/f'FAILURE_{n:03d}.txt').exists():n+=1
  (D/f'FAILURE_{n:03d}.txt').write_text(tb,encoding='utf-8');(D/f'FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());new(D/f'FAILURE_RECEIPT_{n:03d}.json',{'trace_opens':OPENS,'trace_rows':ROWS,'physics_opens':0,'stop_no_automatic_raw_reopen':True,'new_physics':0,'traceback':tb});raise
