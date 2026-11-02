"""Newcommand-schedulequalification ofFROZENcontrollers; noreset/retunemidrun.
Allnewphasegradingisproposed/prospective TRAIN, notH1/H2reinterpretation.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;s=(R/'run_spin_torque_v2.py').read_text(encoding='utf-8');s=s.replace('from spin_center_torque_v2 import GroundController','from spin_center_torque_v2 import GroundController as SpinController\nfrom ground_controller_v4 import GroundController as NormalController');s=s.replace("controller=GroundController(g,cfg.get('controller',{}))", "controller=(SpinController if cfg['profile']=='spin'else NormalController)(g,cfg.get('controller',{}))")
tau_line=next(line for line in s.splitlines(keepends=True)if line.lstrip().startswith('tau=controller.command(estimate,forward,yaw_rate);'));prefix=tau_line[:len(tau_line)-len(tau_line.lstrip())]
statements=["if 'schedule'in cfg:"," forward=0.;yaw_rate=0."," for phase in cfg['schedule']:","  if phase['start_s']<=t<phase['end_s']:forward=float(phase.get('v_m_s',0.));yaw_rate=float(phase.get('w_rad_s',0.));break"]
extra=''.join(prefix+line+'\n'for line in statements);s=s.replace(tau_line,extra+tau_line,1).replace('spin_center=controller.center_log.copy()',"spin_center=getattr(controller,'center_log',{}).copy()")
needle="result['trace_artifact']=";assert needle in s
extra="""phase_metrics=[]
   for phase in cfg['schedule']:
    records=[rr for rr in rows if phase['start_s']<=rr['time']-.01<phase['end_s']];hold=longest=0.;targetw=float(phase.get('w_rad_s',0.));targetv=float(phase.get('v_m_s',0.));recent=[];stop_at=None
    for rr in records:
     gg=rr['ground_truth'];rl=gg['roll_true'];pr=gg['pitch_true'];om=gg['gyro_true'];ww=(om[1]*math.sin(rl)+om[2]*math.cos(rl))/max(math.cos(pr),.15);vv=gg['body_velocity'][0];pose=abs(pr)<math.radians(10)and abs(rl)<math.radians(10);speedok=abs(ww-targetw)<.1*abs(targetw) if targetw else abs(ww)<.3 and abs(vv-targetv)<.15;hold=hold+.01 if pose and speedok else 0.;longest=max(longest,hold)
     if targetw==0 and targetv==0 and hold>=.5 and stop_at is None:stop_at=rr['time']-.5-phase['start_s']
     if rr['time']>=phase['end_s']-2:recent.append((vv,ww))
    means=np.mean(recent,axis=0).tolist()if recent else[None,None];phase_metrics.append(dict(name=phase['name'],target_v=targetv,target_w=targetw,continuous_hold_s=longest,tail_mean_v_w=means,tail_v_RMS=float(np.sqrt(np.mean([(v-targetv)**2 for v,w in recent])))if recent else None,stop_after_command_s=stop_at,complete_to_end=elapsed+1e-8>=phase['end_s']))
   good=True
   for pm in phase_metrics:
    if pm['target_w']:good=good and pm['continuous_hold_s']>=5. and pm['tail_mean_v_w'][1]is not None and abs(pm['tail_mean_v_w'][1]-pm['target_w'])<=.05*abs(pm['target_w'])and pm['tail_v_RMS']<.15
    elif pm['target_v']:good=good and pm['continuous_hold_s']>=2.
    else:good=good and pm['stop_after_command_s']is not None and pm['stop_after_command_s']<=3.
   result['phase_metrics']=phase_metrics;result['transition_proposed_pass']=bool(complete and result['proposed_gate_passed']and good and(drift<.3 if cfg['profile']=='spin'else True));result['phase_gates_scope']='newTRAINengineeringgatesunratifiednotH1H2';"""
s=s.replace(needle,extra+needle);ast.parse(s);p=R/'run_transition_case_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');print('SCHEDULE_RUNNER_NEW_SOURCE_AST_OK')
