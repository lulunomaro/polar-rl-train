from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'TEACHER286_REPLAY_EVAL_V288_20261101';D=N/'postround297';D.mkdir(exist_ok=False)
S=D/'eval298_source';S.mkdir()
def write(p,s):p.write_bytes(s.encode());ast.parse(s,filename=str(p))
worker=(O/'source/evaluate288.py').read_text('utf8').replace('288','298')
worker=worker.replace("ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE' and ck['actual_new_Pi_updates']==2336", "ck['kind']=='REFERENCE_TRACKING_BPTT297_COMPLETE' and ck['actual_new_Pi_updates']==TASK['expected_Pi_updates']")
worker=worker.replace('torch.nn.Linear(44,128)','torch.nn.Linear(103,128)')
worker=worker.replace(" real.reset();cue();obs=", " from tracking_reference297 import Reference297\n reference=Reference297(P/'reference297.npz',TASK['reference'],list(robot.joint_names),real.device,real.hip_anchors194)\n def goal_state():\n  root=tensor(robot.data.root_state_w);q=root[:,3:7];x,y,z,w=q.unbind(-1)\n  R=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)\n  return(root[:,:3]-real.scene.env_origins,R,root[:,7:10],root[:,10:13],tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),torch.zeros(80,151,device=real.device))\n real.reset();cue();obs=")
worker=worker.replace("  with torch.inference_mode():action=actor(x)", "  goal=reference.goals(goal_state(),torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target297)\n  with torch.inference_mode():action=actor(torch.cat((x,goal),-1))")
worker=worker.replace('import terrain298 as sdk','import terrain297 as sdk').replace('sdk.Teacher286Env','sdk.Teacher297Env').replace('real.target286','real.target297')
worker=worker.replace('seconds=(int(counts[i])+1)*.02','seconds=int(counts[i])*.02')
worker=worker.replace('previous_air=torch.zeros_like(active);physics_counts=', 'previous_air=torch.zeros_like(active);support_seen=torch.zeros_like(active);physics_counts=')
worker=worker.replace('previous,previous_air,phys_calls','previous,previous_air,support_seen,phys_calls')
worker=worker.replace('  first_air+=(airborne&~previous_air&active).long();first=first_air==1', '  support_seen|=(torch.linalg.vector_norm(wf,dim=-1)>1).all(-1)&active\n  first_air+=(airborne&~previous_air&active&support_seen).long();first=(first_air==1)&support_seen')
worker=worker.replace("source_run=normal['run_id']", "source_run=normal['run_id']")
worker=worker.replace('jump_cases=72','jump_cases=80').replace('seed=9137,controls=current_control','seed=9137,planned_reference_conditioned=True,autonomous_depth_student=False,controls=current_control')
write(S/'evaluate298.py',worker)
contract='''def validate_task(t):
    assert t['kind']=='FROZEN297_REFERENCE_TRACKING_EVAL298' and t['num_envs']==80
    assert len(t['model_SHA'])==64 and t['model_bytes']>0 and t['expected_Pi_updates']>0
    assert t['seed']==9137 and t['max_controls']==400 and t['closure_m']==.01 and t['mimic_rad']==.01
    assert t['optimizer_steps']==t['account_writes']==0 and t['model_byte_reads']==t['model_decodes']==1
    return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
    assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
    assert c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
    return True
'''
write(S/'contract298.py',contract)
runner=(O/'run288_eval_once.py').read_text('utf8').replace('288','298')
runner=runner.replace("    taskbytes=json.dumps(task,indent=2).encode();", "    p=N/'reference297.npz';files.append(dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))\n    taskbytes=json.dumps(task,indent=2).encode();")
runner=runner.replace("patterns='run298_eval|", "patterns='collect297_|launch297_|run298_eval|")
write(D/'run298_eval_once_template.py',runner)
viewer=(O/'view288_actual_final286_replay.py').read_text('utf8').replace('288','298').replace('286','297')
viewer=viewer.replace('Final297 / actual PhysX298 replay / evaluation failed','Final297 / reference tracking / recorded PhysX298')
viewer=viewer.replace('original Fudan reward + separate teacher loss','reference tracking BPTT / matching tracking critic')
write(D/'view298_actual_final297_replay_template.py',viewer)
print(json.dumps(dict(passed=True,path=str(D),worker_SHA=hashlib.sha256((S/'evaluate298.py').read_bytes()).hexdigest())))
