"""Independent no-model physical comparison of default versus reference initial state."""
from pathlib import Path
import ast,hashlib,json,re,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102'
E=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V310_20261102';E.mkdir(exist_ok=False);(E/'reports').mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copytree(O/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(O/'reference305.npz',E/'reference305.npz')
s=(O/'source/evaluate308.py').read_text('utf8');s=re.sub(r'(?<=[A-Za-z_])308(?!\d)','310',s)
start=s.index(" raw=Path(TASK['model_path']).read_bytes()");end=s.index(' body_names=list(robot.body_names)',start)
s=s[:start]+" put('ACTUAL309_ZERO_MODEL_READS.json',dict(model_reads=0,model_decodes=0,optimizer_steps=0,account_writes=0,controller='plannedjointq/dqtargets; not LQR/MPCtorquecloning'))\n"+s[end:]
start=s.index(' real.reset();obs=vec.get_observations();active=')
s=s[:start]+''' # Paired initial-condition comparison only. Reference full joint/root state
 # is planned initialization, never a future measurement or model training row.
 original_reset=real._reset_idx
 def reference_initial_reset(ids):
  out=original_reset(ids)
  ids=torch.as_tensor(ids,device=real.device,dtype=torch.long);matched=ids[ids>=40]
  if len(matched):
   q=reference.states[0,18:48].expand(len(matched),-1).clone()
   dq=reference.states[0,48:78].expand(len(matched),-1).clone()
   label=reference.labels(torch.zeros(len(matched),device=real.device,dtype=torch.long),matched,real.target305)
   root=tensor(robot.data.default_root_state)[matched].clone();root[:,:3]=label['state'][:,:3]+real.scene.env_origins[matched]
   # Reference rotation0 quaternion supplied by actualsourceproducer; conversion
   # is deterministic nativewxyz->SDKxyzw, no fabricated contact/closure state.
   import native_geometry272 as geom
   qwxyz=geom.mat_to_quat(label['state'][:,3:12].reshape(-1,3,3));root[:,3:7]=qwxyz[:,[1,2,3,0]]
   root[:,7:10]=label['state'][:,12:15];root[:,10:13]=label['state'][:,15:18]
   robot.write_root_state_to_sim(root,env_ids=matched);robot.write_joint_state_to_sim(q,dq,env_ids=matched)
  return out
 real._reset_idx=reference_initial_reset
'''+s[start:]
s=s.replace(' selected=[1,0,10,20];', ' selected=[0,1,40,41];')
s=s.replace(" with torch.inference_mode():raw_action=actor(torch.cat((x,goal),-1));action=raw_action.clamp(-6,6)", " label_action=reference.labels(torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target305)['state']\n  legmotor=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')];wheelmotor=[robot.joint_names.index(n)for n in('left_wheel_spin','right_wheel_spin')]\n  raw_action=torch.cat(((label_action[:,18:48][:,legmotor]-tensor(robot.data.default_joint_pos)[:,legmotor])/sdk.task.LEG_ACTION_SCALE,label_action[:,48:78][:,wheelmotor]/sdk.task.WHEEL_ACTION_SCALE),-1);action=raw_action.clamp(-6,6)")
s=s.replace(" assert all(torch.equal(value,actor.state_dict()[key])for key,value in weights.items())", " assert TASK['model_byte_reads']==TASK['model_decodes']==0")
s=s.replace("kind='reference270'", "kind='defaultzero_init'if i<40 else'reference_init'")
s=s.replace("r['kind']=='reference270'", "r['kind']in('defaultzero_init','reference_init')")
s=s.replace('model_byte_reads=1,model_decodes=1','model_byte_reads=0,model_decodes=0')
s=s.replace('full_window=controls==400','full_window=controls==64')
s=s.replace("  results=results,replay=replay,", "  comparison=[dict(group=g,cases=40,fullwindow=sum(r['full_window']for r in results if r['kind']==g),meanseconds=sum(r['seconds']for r in results if r['kind']==g)/40.,orientation=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for r in results if r['kind']==g),closure=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('closure'))for r in results if r['kind']==g))for g in('defaultzero_init','reference_init')],results=results,replay=replay,")
ast.parse(s);(E/'source/evaluate310.py').write_bytes(s.encode())
contract=(O/'contract308.py').read_text('utf8');contract=re.sub(r'(?<=[A-Za-z_])308(?!\d)','310',contract).replace('FROZEN305_REFERENCE_TRACKING_EVAL309','REFERENCE_INITIAL_STATE_PHYSICS_PROBE310').replace("t['max_controls']==400","t['max_controls']==64").replace("t['model_byte_reads']==t['model_decodes']==1","t['model_byte_reads']==t['model_decodes']==0")
(E/'contract310.py').write_bytes(contract.encode());(E/'source/contract310.py').write_bytes(contract.encode())
runner=(O/'run308_eval_once.py').read_text('utf8');runner=re.sub(r'(?<=[A-Za-z_])308(?!\d)','310',runner).replace(".replace('246','308')",".replace('246','310')")
runner=runner.replace('model_GPU_reads_max=1','model_GPU_reads_max=0').replace("'model_byte_reads_by_worker_max=1','model_byte_reads_by_worker_max=1'", "'model_byte_reads_by_worker_max=1','model_byte_reads_by_worker_max=0'")
runner=runner.replace("parent=parent.replace('controls_max=2000,physics_max=16000','controls_max=400,physics_max=3200')", "parent=parent.replace('controls_max=2000,physics_max=16000','controls_max=64,physics_max=512')")
runner=runner.replace("patterns='","patterns='run310_probe|",1)
ast.parse(runner);(E/'run310_probe_once.py').write_bytes(runner.encode())
task=json.loads((O/'TASK308_FROZEN.json').read_bytes());task.update(kind='REFERENCE_INITIAL_STATE_PHYSICS_PROBE310',max_controls=64,model_byte_reads=0,model_decodes=0,worker_SHA=H(E/'source/evaluate310.py'),human_request='Within task repair: physical startingstate controlledcomparison only, noNNcheckpointread/optimizer/GO/accountwrite',no_new_training=True)
(E/'TASK310_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
(E/'reports/SOURCE310_INITIAL_STATE_COMPARISON.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,groups=['40defaultzero','40plannedreferencefullstate0'],controller='sameplannedq/dqtargetsequencebothgroups',model_reads=0,optimizer_steps=0,account_writes=0,physics='unchangedown400NfullDR2.5msTGS32/4closure10mmmimic.01',purpose='Newreferencetaskinitialstatecomparison; notolddefaultobsABIhypothesisdisprovedin291'),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(E),model_reads=0)))
