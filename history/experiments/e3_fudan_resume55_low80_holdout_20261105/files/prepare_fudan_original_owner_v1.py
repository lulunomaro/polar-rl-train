"""Prepare a NEW source-only owner adapter; no SSH, SDK, models, GO or budget writes."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;P=D/'source_original_owner_v1';assert not P.exists();P.mkdir();S=D.parent/'mod4v1_supermimic_bptt_20261102/source_runtime/supermimic_original_owner.py';source=S.read_text(encoding='utf8');tree=ast.parse(source);lines=source.splitlines(keepends=True)
verify='''def verify_sources(plan):
 require(b.C.resolve()==C.resolve() and plan['H1_excluded'] and len(plan['entries'])==1 and plan['entries'][0]['role']=='E3','Original canonical and exactly one E3 warm branch')
 for e in plan['entries']:
  J=Path(e['job_root']);require(J.resolve().is_relative_to(B/'roles')and not(J/'GO_PRODUCTION.json').exists(),'Unused own job')
  require(e['num_envs']==4096 and e['steps_per_env']==48 and 1<=e['max_iterations']<=300,'Declared finite Fudan PPO cohort')
  m=b.read(J/'INSTALL_MANIFEST.json');require(m['source_PT_copied']is False and m['kind']==KIND,'Only sealed sources/assets, not a copied selected model')
  for f in m['files']:
   p=J/f['path'];require(p.resolve().is_relative_to(J)and p.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors'),'No selected weights in install verification')
   require(p.stat().st_size==f['bytes']and b.H(p)==f['sha256'],'Pinned own source dependency')
  require(e['teacher']['SHA']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'and e['teacher']['bytes']==14715029,'Selected E3 mother mean/value warm start only')
  require(m['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and m['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','Unchanged native asset identity')
'''
admit='''def admit(e,u,c,run,locks,private,finite,resource):
 J=Path(e['job_root']);now=time.time();binding=dict(path=str(C),generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True);fds=[f.fileno()for f in locks]+[private.fileno(),finite.fileno()]
 ad=dict(kind=KIND,epoch=now,role='E3',role_key=e['role_key'],run_id=run,parent_pid=os.getpid(),owner_parent_pid=os.getpid(),gpu_uuid=u,GPU_UUID=u,canonical_binding=binding,inherited_lock_fds=fds,actual_original_authority_EX_private_GPU_EX_finite_SH=True,original_canonical_owner_admitted=True,authority_two_EX=True,private_GPU_EX=True,finite_SH=True,actual_resource=resource)
 put(J/'ROOT_ADMISSION_ACTUAL.json',ad);put(J/'ACTUAL_RESOURCE_LEASES.json',dict(**resource,inherited_lock_fds=fds,owner_parent_pid=os.getpid(),authority_two_EX=True,private_GPU_EX=True,finite_SH=True));put(J/'ACTUAL_CANONICAL_READ.json',dict(epoch=now,path=str(C),SHA=b.H(C),remaining_seconds=c['remaining_training_seconds'],charged_seconds=c['charged_training_seconds'],strict_reserve_seconds=RESERVE,binding=binding))
 task=dict(kind=KIND,role='E3',family='e0_e2_e3',run_id=run,role_key=e['role_key'],gpu_uuid=u,num_envs=e['num_envs'],seed=e['seed'],max_iterations=e['max_iterations'],steps_per_env=48,teacher=e['teacher']['path'],teacher_sha256=e['teacher']['SHA'],teacher_bytes=e['teacher']['bytes'],teacher_iter=43090,owner_parent_pid=os.getpid(),inherited_lock_fds=fds,root_admission_sha256=b.H(J/'ROOT_ADMISSION_ACTUAL.json'),install_manifest_sha256=b.H(J/'INSTALL_MANIFEST.json'),original_protocol=plan_protocol(),asset_sha256='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_sha256='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')
 put(J/'TASK.json',task)
 go=dict(kind=KIND,role='E3',run_id=run,role_key=e['role_key'],gpu_uuid=u,learning_started_epoch=now,max_parent_seconds=3900,save_deadline=now+3600,save_deadline_epoch=now+3600,nominal_end_epoch=now+3900,shutdown_headroom_seconds=300,exit_headroom_seconds=300,task_sha256=b.H(J/'TASK.json'),root_admission_sha256=task['root_admission_sha256'],install_manifest_sha256=task['install_manifest_sha256'],canonical_binding=binding,teacher_sha256=e['teacher']['SHA'])
 return task,go
'''
protocol="""def plan_protocol():return dict(physics_dt=.0025,policy_hz=50,feedback_hz=100,TGS=[32,4],gas_N=400,stiffness_N_m=2000,damping_Ns_m=3,closure_m=.01,mimic_rad=.01,full_D0_D7=True,algorithm='PPO_plus_five_frame_supervised_velocity_encoder',warm_start_only=True,source_Adam_iteration_or_DR_not_resumed=True,new_lowrise_curriculum=True,original_frozen_74_grader_unchanged=True,whole_leg_same_end_video_pose_covered=False)
"""
replace={'verify_sources':verify,'admit':admit,'plan_protocol':protocol}
for n in sorted([n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in replace],key=lambda n:n.lineno,reverse=True):lines[n.lineno-1:n.end_lineno]=[replace[n.name]]
out=''.join(lines);out=out.replace("UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')","UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842',)").replace("KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'","KIND='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1'").replace("Linux_MOD4V1_SUPERMIMIC_BPTT_","Linux_MOD4V1_E3_FUDAN_SEQUENCE_PPO_").replace('actualGOthroughload-model-WM-BPTT-fullsave-SDKclose-parentwait','actualGOthroughload-warm-sequence-PPO-fullsave-SDKclose-parentwait').replace('SUPERMIMIC_FULL_STDOUT_STDERR.log','FDN_FULL_STDOUT_STDERR.log').replace('worker_supermimic_bptt.py','worker_fudan_sequence_ppo_native_v1.py').replace('target_per_expert=3000','max_policy_iterations=300')
# The semantic wait hook is supplied by the new worker's explicit stdlib closure contract.
needle="rc=p.wait();J=Path(e['job_root']);final=b.read(J/'production/FINAL.json');rows[key]="
assert out.count(needle)==1
out=out.replace(needle,"rc=p.wait();J=Path(e['job_root']);final=b.read(J/'production/FINAL.json');qualified=qualify_waited(J,rc,final);rows[key]=").replace('original_error=rc!=0);put(J/','original_error=not qualified);put(J/').replace('if rc!=0:\n      errors.append','if not qualified:\n      errors.append')
hook='''def qualify_waited(J,rc,final):
 # Actual child.wait has occurred before this hook. New FDN metadata is never sent to a SM gate.
 sys.path.insert(0,str(J/'worker_sources'))
 from fudan_worker_close_contract_v1 import qualify_actual_wait
 return bool(qualify_actual_wait(J,rc,final))

'''
out=out.replace('def main():',hook+'def main():',1).replace('production/FINAL.json','production/FDN_FINAL.json')
out=out.replace('Finite original-canonical two-GPU SuperMimic BPTT owner','Finite original-canonical E3 Fudan-sequence PPO owner').replace('Worker algorithm changes are explicitly newhuman requested, not PPO20 relabel.','New warm branch, no legacy SuperMimic or PPO20 continuation claim.')
def functions(s):
 t=ast.parse(s);ln=s.splitlines(keepends=True);return{n.name:''.join(ln[n.lineno-1:n.end_lineno])for n in t.body if isinstance(n,ast.FunctionDef)}
a,bf=functions(source),functions(out)
for name in('gpu','account','environment'):assert a[name]==bf[name],name
ast.parse(out);(P/'fudan_original_owner_v1.py').write_text(out,encoding='utf8');(P/'SOURCE_ADAPTER_NOTE.json').write_text(json.dumps(dict(kind='SOURCE_ONLY_NOT_ACTUAL_ADMISSION',original_owner=str(S),unchanged_function_bytes=['gpu','account','environment'],original_authority_private_and_finite_lock_loop_retained=True,original_1800_3900_3600_300_bounds_retained=True,single_GPU0_and_E3_only=True,task_and_manifest_schema_changed_for_new_PPO_warm_branch=True,new_actual_wait_semantic_gate=True,models_SDK_GO_ledger_operations=0),indent=2),encoding='utf8');print(str(P/'fudan_original_owner_v1.py'))
