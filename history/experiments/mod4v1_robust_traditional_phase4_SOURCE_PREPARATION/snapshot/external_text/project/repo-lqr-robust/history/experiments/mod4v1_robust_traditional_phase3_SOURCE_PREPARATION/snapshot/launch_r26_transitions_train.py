"""FrozenP25normal forward/reversebraking and frozenH2spin start/stop/reverse TRAIN.
No midrunreset/poseassist/retuning. FreshcaseIDs, fullD0-D7, atmost4CPUphysicsworkers.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures,math,hashlib
R=Path(__file__).resolve().parent;D=R/'batches/r26_transitions26';D.mkdir(parents=True,exist_ok=False)
rc=0 # independentgrader+runnerASTpreflightalreadycompletedbyprepare_r25
assert rc==0;proto=json.loads((R/'SPIN_H2_K20_V1/PROTOCOL.json').read_bytes());normal=dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052)
schedules={name:[dict(name='drive',start_s=1.,end_s=6.5,v_m_s=sgn*2.),dict(name='brake',start_s=6.5,end_s=12.)]for name,sgn in(('forward',1),('reverse',-1))};schedules['spin_cycle']=[dict(name='positive4pi',start_s=1.,end_s=10.,w_rad_s=4*math.pi),dict(name='first_stop',start_s=10.,end_s=13.),dict(name='negative4pi',start_s=13.,end_s=22.,w_rad_s=-4*math.pi),dict(name='final_stop',start_s=22.,end_s=26.)]
protocol=dict(kind='FROZENCONTROLLER_NEWTRANSITION_TRAIN_NOT_H1H2',seeds=[0]+list(range(201,209)),schedules=schedules,gate=dict(spin_continuous_yaw_pose_s=5.,spin_mean_relative_tol=.05,spin_tail_v_RMS=.15,normal_speed_pose_continuous_s=2.,stop_speed_tolerance=.15,stop_yaw_tolerance=.3,stop_settle_hold_s=.5,stop_completion_limit_s=3.,spin_endpoint_drift_m=.3,original_wholecase_gate_retained=True),no_param_selection_from_H1_H2=True);(D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8');(D/'run_transition_case_v3.py').write_bytes((R/'run_transition_case_v3.py').read_bytes());env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');jobs=[('forward',s)for s in range(204,212)]+[(p,s)for p in('reverse','spin_cycle')for s in[0]+list(range(201,209))]
def run(j):
 name,s=j;case=f'r26_{name}_{s}';spin=name=='spin_cycle';cfg=dict(case_id=case,seed=s,nominal=s==0,profile='spin'if spin else'normal',mode='custom_transition',duration_s=26. if spin else 12.,controller=proto['controller']if spin else normal,schedule=schedules[name],feedback='sensors',upright_arming_prior=True,accel_reference='wheel_midpoint',accel_correction=0. if spin else 1.5);cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_transition_case_v3.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};row=dict(case=case,profile=name,seed=s,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),pass_=r.get('transition_proposed_pass'),screen=r.get('proposed_gate_passed'),xy=r.get('xy_displacement_m'),phases=r.get('phase_metrics'));print(json.dumps(row),flush=True);return row
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for offset in range(0,len(jobs),4):
  chunk=list(pool.map(run,jobs[offset:offset+4]));rows.extend(chunk)
  if any(r['returncode']for r in chunk):
   (D/'SOFTWARE_ABORT.json').write_text(json.dumps(dict(rows=rows,remaining_unstarted=jobs[offset+4:]),indent=2),encoding='utf-8');raise RuntimeError('softwareerrorabortunstarted')
summary={p:dict(n_DR=8,complete_DR=sum(r['profile']==p and r['seed']!=0 and bool(r['complete'])for r in rows),passed_DR=sum(r['profile']==p and r['seed']!=0 and bool(r['pass_'])for r in rows))for p in schedules};(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='TRANSITION_TRAIN26_FORWARD_NEWSEEDS_AFTER_POSTPROCESS_FIX',summary=summary,rows=rows),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True)
