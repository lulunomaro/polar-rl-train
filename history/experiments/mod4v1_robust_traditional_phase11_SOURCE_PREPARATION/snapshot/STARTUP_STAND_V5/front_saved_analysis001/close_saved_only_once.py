"""ONLY saved minimum/small refs/stat. No control/physics stream open, no project module import."""
from pathlib import Path
import json,hashlib,collections
O=Path(__file__).resolve().parent
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,x):
 with (O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def link(n):return '['+n+'](<'+(O/n).as_posix()+'>)'
def main():
 m=json.loads((O/'MINIMUM_001.json').read_bytes());c=json.loads((O/'READCOUNTS_001.json').read_bytes());n=m['counts'];r=m['original_result_selected'];old=m['old_V4_saved_only_selected'];events=m['events'];slots=m['first_and_last_event_rows']
 assert m['error']is None and m['status']=='SAVED_ONE_V5_CONTROL_TRACE_MINIMUM_BEFORE_PROSE' and m['event_count']==len(events)==11
 assert c['trace_opens']==1 and c['trace_rows_read']==c['valid_rows']==188 and c['physics_raw_opens']==c['old_V4_trace_opens']==c['raw_hashes_recomputed']==0
 assert n['valid_LIFT']==n['LIFT_REQUEST_formula_verified']==156 and n['LIFT_pose_request_branch_TRUE']==n['LIFT_pose_REQUEST_differs_quiet']==38 and n['LIFT_gate_FALSE']==118
 assert m['max_REQUEST_formula_error_Nm']==0 and m['source_small_SHA_unchanged']and m['trace_stat_unchanged']
 pat=collections.Counter()
 for x in m['control_phase_gate_reason_intervals']:
  if x['phase']=='LIFT_WORLD_SUPPORT' and x['gate']is False:pat[tuple(x['reason_terms'])]+=x['last_row']-x['first_row']+1
 assert sum(pat.values())==118
 last_on=max(x['PRE_end']for x in m['control_phase_gate_reason_intervals']if x['phase']=='LIFT_WORLD_SUPPORT'and x['pose']is True)
 def event(label):return next(e for e in events if label in e['tags'])
 on=event('first_pose_REQUEST');off=event('first_current_gate_FALSE_after_pose');qd=event('first_LIFT_qd_above_point4');speed=event('first_logged_softspeed_guard');goal=event('first_goal_clip');gamma=event('first_gamma_limit');valid=event('last_valid');fault=event('last_guard_or_no_current')
 compact=[dict(tags=e['tags'],PRE_s=e['PRE_command_s'],POST_s=e['POST_root_s'],phase=e['phase'],gate=e['logged_gate'],pose_REQUEST=e['logged_pose_branch_request'],gate_metrics=e['gate_component_metrics'],failure_terms=e['measured_exclusion_terms'],estimate_PRE_pitch_rate=[e['estimated_PRE_pitch_rad'],e['estimated_PRE_pitch_rate_sourceheld_rad_s']],true_POST_pitch=e['true_POST_pitch_rad'],root_POST_XYZ=e['true_POST_rootXYZ_m'],REQUESTwheel=[e['actual_REQUEST6'][2],e['actual_REQUEST6'][5]],source_wheel_mean=e['source_wheel_mean2'],proxy_m=e['wheel_rotation_proxy_m'],goal_h=[e['goal_unclipped_h'],e['goal_clipped_h']],gamma=e['reference_gamma'],publication_s=e['published_reference_time_s'],support_both20=e['private_bin_both_main_all20'])for e in events]
 facts=dict(status='SAVED_ONLY_FEATURE_ACTED_EARLY_BUT_MOST_MOVING_LIFT_QUIET_NOT_UNIQUE_CAUSE',minimum=rec(O/'MINIMUM_001.json'),counts=n,LIFT_measured_exclusion_patterns=[dict(reasons=list(k),rows=v)for k,v in pat.items()],pose_REQUEST_percent_LIFT=100*38/156,last_pose_REQUEST_command_s=last_on,continuous_late_quiet_interval_s=[.84,1.86],continuous_late_quiet_rows=103,fresh_not_independently_logged=True,all_observed_sensor_age_zero=n['source_age_zero']==188,other_measured_terms_pass_but_gate_FALSE=n.get('LIFT_other_measured_terms_pass_but_gate_FALSE',0),REQUEST_formula_max_error_Nm=m['max_REQUEST_formula_error_Nm'],events=compact,ranges=m['ranges'],old_V4_saved_summary_only=old,new_V5_original_result=r,actual_DC_applied_tau_contact_identity_unknown=True,no_next_parameter_or_case_decision=True)
 save('FACTS_001.json',facts)
 lines=['# V5 首案：实际pose REQUEST与quiet gate的单流诊断','',
 f'- 原结果不改：188 control/3760 physics，OBSERVE31/LIFT156/INHIBIT1；stop={r["stop"]}，原门False、BALANCE无、末stable0。',
 '- '+link('READCOUNTS_001.json')+'先保留，再'+link('MINIMUM_001.json')+'：唯一新trace一次188行/1201204B，11 bounded事件；physics/旧V4raw/其他raw/rawSHA均0，随后只读saved minimum。',
 '- feature timing flag188/188=True不等于力矩起用：LIFT真正pose REQUEST38/156=24.36%，quiet118/156=75.64%；全部156条按logged common/轮mean/softguard复核REQUEST，maxerror0，38条都与quiet不同。',
 f'- 首次gate/latch/pose={on["PRE_command_s"]:.2f}s：估计pitch={on["estimated_PRE_pitch_rad"]:.9f}、源rate={on["estimated_PRE_pitch_rate_sourceheld_rad_s"]:.9g}，common={on["wheel_pose_common_before_damping_Nm"]:.9f}Nm→轮REQUEST[3,3]；该20子采样bin双主轮并非全时>1N，gate不是支撑证书。',
 f'- latch在156条LIFT都True但current gate仍控制输出；最后pose={last_on:.2f}s，.84–1.86连续103条quiet。可见失格分区：proper-only11、qd-only37、qd+qerror70=118；不是未激活，也不是整个LIFT持续body-feedback。',
 f'- first-off={off["PRE_command_s"]:.2f}s先因proper norm{off["gate_component_metrics"]["proper_norm_m_s2"]:.9f}>11.772，qd仅{off["gate_component_metrics"]["qd_max_rad_s"]:.9f}；首次qd失格{qd["PRE_command_s"]:.2f}s/max|qd|={qd["gate_component_metrics"]["qd_max_rad_s"]:.9f}。qd>.4共107/156（70同时qerr>.08），是moving LIFT中充分的排除项，不推唯一动态原因。',
 '- fresh本身未独立log：188条sensor_age均0，38条AND-gate True证明其fresh；other可见项全过却gateFalse=0。其余118已有可见失格项，fresh仍UNKNOWN，失格总项数107+70+11不能直接相加。',
 f'- 12rad/s softguard首次{speed["PRE_command_s"]:.2f}s，源轮mean=[12.174674439,11.818714195]→REQUEST[-.052402332,3]；logged guard5条，mean轮>12共9条，峰[{m["ranges"]["max_abs_source_wheel2"][0]:.9f},{m["ranges"]["max_abs_source_wheel2"][1]:.9f}]；非物理速度/actual DC限制证明。',
 f'- 轮转proxy首次≥.1在.58s/≥.25在.80s，末max={m["ranges"]["max_wheel_rotation_proxy_m"]:.9f}m<.50；不是true路程，.50/6s未触发。目标h首clip={goal["PRE_command_s"]:.2f}s：{goal["goal_unclipped_h"]:.9f}→{goal["goal_clipped_h"]:.9f}；clip96条，gamma limit35条/首次{gamma["PRE_command_s"]:.2f}s。',
 f'- 末valid PRE={valid["PRE_command_s"]:.2f}s：估计pitch/rate={valid["estimated_PRE_pitch_rad"]:.9f}/{valid["estimated_PRE_pitch_rate_sourceheld_rad_s"]:.9f}，qerr={valid["gate_component_metrics"]["qerror_max_rad"]:.9f}、maxqd={valid["gate_component_metrics"]["qd_max_rad_s"]:.9f}，轮REQUEST[-.157653817,-.161616938]。',
 f'- guard PRE={fault["PRE_command_s"]:.2f}s估计pitch={fault["estimated_PRE_pitch_rad"]:.9f}>1→INHIBIT，REQUEST6全0；true POST={fault["POST_root_s"]:.2f}s/pitch={fault["true_POST_pitch_rad"]:.9f}；last published ref仍1.86，fault的current gate/common/gamma是null，不能当新reference或零applied。',
 f'- private grade：双主轮全部20采样承重115/188，nonwheel全部≤1N=0，两者同时0；whole guide3710/hard0。只用原bin/小result，不猜接触身份或作用阶段。',
 f'- 仅对照旧V4 saved摘要：193条/capture eligibleFalse、轮REQUEST峰.188839/.188061与轮mean峰.629465/.626869；V5峰3/3、13.046208/13.334728。true最大XY .076305426→.352945073m、高度增量.068776234→.068183005m，旧/新原门仍False；非固定qref/唯一wheel因果或泛化结论。',
 '- PRE command/年龄view估计pitch、源window-held rate/gyro/encodermean，与true POST+10ms以及该20×.5ms private支撑bin单列；'+link('FACTS_001.json')+'及11完整事件保留q/qd/ref/vref/common/REQUEST6/epochs。',
 '- actual2k applied/电流/DC mask/instant drive速度、接触身份/impact/唯一失效原因UNKNOWN；不从±3请求推actual saturation，不把quiet传感gate当可信接触或源rate当瞬时。',
 '- 本轮0新控制/调参/新case/模型/FK/PHY/DR/旧QA/solver/compile/link/Git/agent/Goal/Mnemon；C15文件未碰；PH11pending，停交父，不作下一增益/门限/病例决定。']
 assert len(lines)<=20
 with (O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
 sources_after=[rec(Path(x['path']))for x in m['source_small_before']];assert sources_after==m['source_small_before']
 stat=Path(m['source_trace']['path']).stat();assert stat.st_size==m['source_trace']['bytes']and stat.st_mtime_ns==m['source_trace']['mtime_ns']
 save('RECEIPT.json',dict(status='SEALED_ONE_V5_SAVED_CONTROL_TRACE_FEATURE_GATE_DIAGNOSIS_NOT_UNIQUE_CAUSE_OR_PHYSICAL_QUALIFICATION',artifacts=[rec(O/x)for x in ['REPORT.md','FACTS_001.json','MINIMUM_001.json','READCOUNTS_001.json','extract_control_once.py','close_saved_only_once.py']],source_small_after=sources_after,source_small_before_after_SHA_equal=True,read_counts=c,trace_post_stat_stable_not_raw_hash=True,raw_source_producer_SHA_not_recomputed=m['source_trace']['producer_SHA_NOT_RECOMPUTED'],report_lines=len(lines),bounded_events=len(events),first_extraction_exit0_no_retry=True,saved_only_prose_close_no_raw_reopen=True,original_result_gate_and_old_V4_scores_unchanged=True,independent_fresh_not_logged_unknown=True,actual_applied_DC_contact_identity_unknown=True,no_next_control_parameter_or_case_decision=True,PH11pending=True,C15_files_touched=0))
 print(json.dumps(dict(status='SAVED_DIAGNOSIS_SEALED',REPORT=rec(O/'REPORT.md'),FACTS=rec(O/'FACTS_001.json'),RECEIPT=rec(O/'RECEIPT.json'),trace_opens=1,trace_rows=188,physics_raw=0,raw_hash=0,report_lines=len(lines)),ensure_ascii=False))
if __name__=='__main__':main()
