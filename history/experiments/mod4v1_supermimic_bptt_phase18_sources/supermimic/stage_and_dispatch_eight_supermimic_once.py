"""FreshnativeSuperMimicBPTT8source-staging+originalownerdispatch.
Nevercopies/opensmodelsorraw, noSDKbeforeoriginalparentactualGO.
"""
from pathlib import Path
import sys,json,time,datetime,hashlib,ast,zipfile,shlex
R=Path(__file__).resolve().parent;T=R.parent/'mod4v1_experts_fulldr_rm70_20261101';D=T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';sys.path.insert(0,str(T));from project_connector import connect72
marker=R/'SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json';assert not marker.exists();P=R/'payload_supermimic_eight_v1';assert not P.exists();P.mkdir();src=R/'source_runtime';core=R/'source_core_review/ctx_reward_learner.py';assert core.exists();vendor=R.parent/'supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2';assert vendor.is_dir();reg=json.loads((T/'EXPERT_NORMALIZATION_REGISTRY_v12.json').read_bytes());best={r['role']:r for r in reg['posttrain_assessed_finite_windows']['scope_assessment_rows']};cat=json.loads((T/'MOD4V1_EIGHT_POSTTRAIN_CHECKPOINT_CATALOG_V1.json').read_bytes());cand={r['role']:r['candidate_complete_checkpoint']for r in cat['rows']};mbytes={'E2':14615089,'E3':14715029,'W35':17620037,'SLOPE_INDEPENDENT50':17955663};order=['E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'];pairs={'E0':1,'CURB_PROTECTED878':1,'E2':2,'CURB_INDEPENDENT113':2,'E3':3,'SLOPE135':3,'W35':4,'SLOPE_INDEPENDENT50':4};stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());run='MOD4V1_SUPERMIMIC_BPTT8_V1_'+stamp;root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;entries=[]
for role in order:
 n=pairs[role];pointer=D/('PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json'if n==1 else'PAIR'+str(n)+'_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json');old=json.loads(Path(json.loads(pointer.read_bytes())['path']).read_bytes())['root'];teacher=dict(best[role]['selected_source']);teacher['bytes']=cand[role]['bytes']if teacher['SHA']==cand[role]['SHA']else mbytes[role];family='formal'if role in('E0','E2','E3')else'w35'if role=='W35'else'e1';entries.append(dict(role=role,family=family,base_root=old+'/roles/'+role,job_root=root+'/roles/'+role,role_key='supermimic_'+role.lower()+'_72',teacher=teacher,num_envs=1024,target_bptt_steps=3000,seed=20261102+order.index(role)))
plan=dict(kind='NEW_HUMAN_EIGHT_SUPERMIMIC_BPTT_AT_LEAST_3000_TRUE_POLICY_STEPS_AND_90_PERCENT_SKILL_GOAL',run_id=run,goal_id='goal-1c14ef7d-c888-4287-83bf-c008d54545fb',H1_excluded=True,entries=entries,final_success_per_expert=.9,intermediate_floor=.8,no_PPO_updates_or_native_PhysX_autograd_claim=True,not_3000PPO_equivalent=True)
files={'supermimic_original_owner.py':src/'supermimic_original_owner.py','worker_sources/worker_supermimic_bptt.py':src/'worker_supermimic_bptt.py','worker_sources/native_supermimic_bridge.py':src/'native_supermimic_bridge.py','worker_sources/ctx_reward_learner.py':core}
for p in vendor.rglob('*.py'):files['worker_sources/supermimic_vendor_v2/'+p.relative_to(vendor).as_posix()]=p
# Originalauthorityhelpersbyte-identical; metadataonly,nocanonicalcopy.
for name in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):
 matches=list((D/'parent_source').glob(name))
 if not matches:matches=list(D.rglob(name))
 assert matches;p=matches[0];expected={'three_slot_common_v1.py':'eaf6aa1a06d2a49570eff54af5447395210c6de9f3a9c43d566d1adad4e53044','single_writer72_authority_V85M_source.py':'ceba8067ceaffa8f2a978a0165b1ef06fc28b980d5f9da29ba03c760d9c1d98c'};assert hashlib.sha256(p.read_bytes()).hexdigest()==expected[name];files[name]=p
assets=T.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets'
for p in assets.rglob('*'):
 if p.is_file():files['pinned_assets/'+p.relative_to(assets).as_posix()]=p
bundle=P/'SOURCE_NONPT.zip';fm=[]
with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED)as z:
 for rel,p in sorted(files.items()):
  assert p.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.pyc');raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
  z.writestr(rel,raw);fm.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(P/'SOURCE_PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(P/'UPLOAD_SOURCE_INDEX.json').write_text(json.dumps(fm,indent=2),encoding='utf-8');code=r'''from pathlib import Path
import os,json,hashlib,shutil,zipfile,ast
B=Path(%r);P=json.loads((B/'SOURCE_PLAN.json').read_bytes());assert P['H1_excluded']and len(P['entries'])==8 and not(B/'STAGE_COMPLETE.json').exists()
with zipfile.ZipFile(B/'SOURCE_NONPT.zip')as z:
 for x in z.namelist():assert not x.startswith('/')and'..'not in Path(x).parts
 z.extractall(B/'software')
S=B/'software';NO={'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.partial'};JSONS={'original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_DERIVATION_INDEX.json','MOD4V1_ASSET_DIFF.json','E1_CANONICAL_SOURCE_METADATA.json','VARIANT_SOURCE_METADATA.json','CPU_FOUR_LEAF_ACTUAL_COMPLETE.json','CPU_FULL_NESTED_OWNER_AUDIT.json','NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json'}
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def ignore(path,names):return[n for n in names if n=='__pycache__'or Path(n).suffix.lower()in NO or n.endswith(('.jsonl','.log'))]
rows=[]
for e in P['entries']:
 src=Path(e['base_root']);dst=Path(e['job_root']);assert dst.is_relative_to(B/'roles')and not dst.exists();dst.mkdir(parents=True)
 for name in('runtime','lib','original_field','new_assets','assets','producer'):
  if(src/name).is_dir():shutil.copytree(src/name,dst/name,ignore=ignore)
 for p in src.iterdir():
  if(p.suffix=='.py'or p.name in JSONS)and p.is_file():shutil.copy2(p,dst/p.name)
 shutil.copytree(S/'worker_sources',dst/'worker_sources')
 dep=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/sm_deps')
 if dep.is_dir():shutil.copytree(dep,dst/'worker_sources/sm_deps',ignore=ignore)
 for target in(dst/'runtime/assets',dst/'new_assets'):
  target.mkdir(parents=True,exist_ok=True)
  for p in(S/'pinned_assets').rglob('*'):
   if p.is_file():q=target/p.relative_to(S/'pinned_assets');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 assert H(dst/'runtime/assets/robot.usd')=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and H(dst/'runtime/assets/import_contract.json')=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
 files=[]
 for p in sorted(dst.rglob('*')):
  assert p.suffix.lower()not in NO
  if p.is_file():
   raw=p.read_bytes()
   if p.is_relative_to(dst/'worker_sources')and p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
   assert not p.name.upper().startswith('TRAINING_BUDGET');files.append(dict(relative=p.relative_to(dst).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 put(dst/'INSTALL_MANIFEST.json',dict(kind='ACTUAL_SUPERMIMIC_NONPT_SOFTWARE_INSTALL_NOT_SDK_ADMISSION',source_PT_copied=False,asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',teacher_metadata=e['teacher'],files=files));rows.append(dict(role=e['role'],files=len(files),manifest_SHA=H(dst/'INSTALL_MANIFEST.json')))
for name in('supermimic_original_owner.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):shutil.copy2(S/name,B/name)
put(B/'OWNER_PLAN.json',P);put(B/'STAGE_COMPLETE.json',dict(rows=rows,source_model_stat_read_or_copy_SDK_C_GO=0));print(json.dumps(dict(root=str(B),staged=True,roles=rows,PT_SDK_C_GO=0)))
'''%root
c=connect72();s=c.open_sftp();report=dict(root=root,run_id=run,roles=order,source_PT_copies_or_opens=0,stage_only_until_original_owner_checks=True,goal_id=plan['goal_id'])
try:
 s.mkdir(root);s.put(str(bundle),root+'/SOURCE_NONPT.zip');s.put(str(P/'SOURCE_PLAN.json'),root+'/SOURCE_PLAN.json');s.put(str(P/'UPLOAD_SOURCE_INDEX.json'),root+'/UPLOAD_SOURCE_INDEX.json');stage=R/'remote_stage_supermimic_eight_v1.py';assert not stage.exists();stage.write_text(code,encoding='utf-8');s.put(str(stage),root+'/stage_nonpt_source.py');cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/stage_nonpt_source.py');i,o,e=c.exec_command(cmd,timeout=300);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_returncode=rc,stage_stdout=stdout,stage_stderr=stderr);(R/'reports/SUPERMIMIC_NONPT_STAGE_V1_RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert rc==0,(rc,stderr)
 launch="from pathlib import Path;import subprocess,json,psutil;B=Path(%r);assert not(B/'OWNER_STARTED.json').exists();f=(B/'OWNER_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'supermimic_original_owner.py')],cwd=B,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);f.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_not_yet_actualGO':True}))"%root;i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(launch),timeout=30);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);report.update(parent=json.loads(txt),owner_original_authority_gates_not_lowered=True);marker.write_text(json.dumps(report,indent=2),encoding='utf-8');print(marker);print(json.dumps(report,indent=2))
finally:s.close();c.close()
