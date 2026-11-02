"""Data-driven exactlytwo frozen candidates fromACTUALclosedfullPPO FINAL.
OriginalV8factory/DR/physics/predicates/capacity/2EX eval gate preserved.
No oldrolecode stringreplacement, modelcopy/readbyparent, ornewPPO/Cwriter.
"""
from pathlib import Path
import argparse,json,sys,datetime,time,hashlib,ast,zipfile,shlex
D=Path(__file__).resolve().parent;R=D.parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(R));from project_connector import connect72
q=argparse.ArgumentParser();q.add_argument('--pair',type=int,required=True,choices=(2,3,4));a=q.parse_args();tag='PAIR'+str(a.pair)+'_FROZEN_RETENTION_V1';marker=D/(tag+'_DISPATCH_ONCE.json');reportfile=D/'reports'/(tag+'_STAGE_DISPATCH.json');assert not marker.exists()and not reportfile.exists();loc=json.loads((D/('PAIR'+str(a.pair)+'_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json')).read_bytes());closed=json.loads(Path(loc['path']).read_bytes());assert closed['parent_exit']['original_cost_settled']and closed['parent_exit']['all_own_children_waited']and closed['parent_exit']['original_private_finite_authority_leases_released']and not closed['parent_exit']['errors'];rr=closed['cohort']['rows'];assert all(r['returncode']==0 and r['terminal_all_own_children_waited']for r in rr.values());finals={r['role']:r['final']for r in closed['rows']};roles=list(finals);G=D/'source_eval_generic_pair_v1';sys.path.insert(0,str(G));from generic_eval_metadata import build_eval_metadata
E=R/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR';basecontracts=json.loads((E/'ROLE_CONTRACTS.json').read_bytes());meta=build_eval_metadata(roles,finals,basecontracts,provenance={'actual_closed_source':loc['path'],'original_scope_from_actual_V8':True});stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());group='MOD4V1_'+tag+'_'+stamp;root='/home/lc01/Zonglin Li/zonglin2/tasks/'+group;S=D/(tag+'_SOURCE');assert not S.exists();S.mkdir();parentbase=D/'PAIR1_RETENTION_EVAL_SOURCE_V3'
for p in parentbase.glob('*.py'):(S/p.name).write_bytes(p.read_bytes())
observation_overlay=[]
if a.pair==4:
 O=D/'source_assess_pair4_v1/observer_w35_split_v1';idx=json.loads((O/'FINAL_W35_SPLIT_OBSERVER_SOURCE_INDEX_V1.json').read_bytes());proof=json.loads(Path(idx['proof']['path']).read_bytes());assert proof['all_passed']and proof['original_close_kinematic_acceptance_and_group_label_AST_unchanged']and proof['original_emitted_rows_before_writer_identical']
 for row in(idx['original_book'],idx['original_worker']):
  raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA']
 for row in idx['overlay_sibling_files']:
  p=Path(row['path']);raw=p.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];ast.parse(raw.decode('utf-8'));(S/p.name).write_bytes(raw);observation_overlay.append(dict(relative=p.name,bytes=len(raw),SHA=row['SHA']))
 (S/'OBSERVATION_ONLY_OVERLAY_PROVENANCE.json').write_text(json.dumps({'source_index':str(O/'FINAL_W35_SPLIT_OBSERVER_SOURCE_INDEX_V1.json'),'same_original_writer_original_row_booleans_only':True,'original_methods_AST_and_emitted_rows_unchanged':True,'overlay':observation_overlay,'no_replay_or_current_training_changes':True,'not_hardware_or_fullskill_qualification':True},indent=2),encoding='utf-8')
(S/'single_gpu_group_supervisor.py').write_bytes((G/'single_gpu_group_supervisor.py').read_bytes());(S/'CANDIDATE_ROLE_CONTRACTS.json').write_text(json.dumps(meta['ROLE_CONTRACTS'],indent=2),encoding='utf-8');(S/'ACTUAL_CANDIDATE_SOURCE_METADATA.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');baseline=json.loads((R/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json').read_bytes());oldroot=baseline['root'];rows=[]
for r in meta['roles']:
 role=r['role'];r.update(runtime_origin=oldroot+'/runtimes/'+role,runtime_root=root+'/runtimes/'+role,asset_dir=root+'/runtimes/'+role+('/new_assets'if r['family']=='e1'else'/runtime/assets'));rows.append(r)
GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';sys.path[:0]=[str(S),str(E)];from task_contract import make_task;from e1_group_scope import validate_group_task
plan=dict(kind='EXACT_TWO_POSTTRAIN_CANDIDATE_FROZEN_ORIGINAL_SCOPE_PLAN',group_id=group,GPU_UUID=GPU,asset_SHA=USD,contract_SHA=CONTRACT,eval_members=meta['eval_members'],roles=rows,copy_models=False,PPO_BPTT_newledger=False);cross=[]
for r in rows:
 t=make_task(r,plan,time.time()+3600,[41,42]);t['eval_members']=meta['eval_members']
 if r['family']=='e1':assert validate_group_task(t,r['role'],root,root+'/cases/'+r['role'],meta['ROLE_CONTRACTS'],environment={'CUDA_VISIBLE_DEVICES':GPU},fd_check=lambda fd:None);cross.append(r['role'])
entries={'single_gpu_group_supervisor.py':S/'single_gpu_group_supervisor.py'}
if observation_overlay:entries['worker_sources/parent/OBSERVATION_ONLY_OVERLAY_PROVENANCE.json']=S/'OBSERVATION_ONLY_OVERLAY_PROVENANCE.json'
for p in S.glob('*.py'):
 if p.name!='single_gpu_group_supervisor.py':entries['worker_sources/parent/'+p.name]=p
child=json.loads((R/'E1_N80_FEEDBACK_DESCRIPTOR_ACTUAL_API_HANDOFF_V5.json').read_bytes())
for row in child['runtime_files_to_stage_same_directory']:
 p=Path(row['path']);raw=p.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];entries['worker_sources/e1/'+p.name]=p
entries['worker_sources/e1/ROLE_CONTRACTS.json']=S/'CANDIDATE_ROLE_CONTRACTS.json';assets=R.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets'
for p in assets.rglob('*'):
 if p.is_file():entries['pinned_assets/'+p.relative_to(assets).as_posix()]=p
archive=D/(tag+'_NONPT_SOURCE.zip');files=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=2)as z:
 for rel,p in sorted(entries.items()):
  assert p.suffix.lower()not in{'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc'};raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
  z.writestr(rel,raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
plan['worker_files']=files;tree=ast.parse((R/'stage_and_dispatch_nine_single_gpu_eval_v8_once.py').read_text(encoding='utf-8'));template=next(n.value.left.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets)and isinstance(n.value,ast.BinOp)and isinstance(n.value.op,ast.Mod));stagecode=template%root;c=connect72();s=c.open_sftp();report=dict(kind='GENERIC_FROZEN_PAIR_EVAL_STAGE_DISPATCH_NOT_RESULTS',pair=a.pair,root=root,group_id=group,roles=roles,GPU_UUID=GPU,actual_training_closed=loc['path'],source_model_copies_or_opens_byparent=0,source_schema_crossvalidated=cross,observation_only_W35_samewriter_overlay=observation_overlay)
try:
 s.mkdir(root);s.put(str(archive),root+'/NONPT_GROUP_SOURCE.zip')
 with s.open(root+'/GROUP_PLAN.json','wx')as z:z.write(json.dumps(plan,indent=2))
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(stagecode),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_returncode=rc,stage_stdout=text,stage_stderr=err);assert rc==0,(rc,err)
 code="import pathlib,subprocess,json,psutil;B=pathlib.Path("+repr(root)+");assert not(B/'PARENT_STARTED.json').exists();f=(B/'GROUP_SUPERVISOR_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(["+repr('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+",'-u','-B',str(B/'single_gpu_group_supervisor.py')],cwd=B,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);f.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'parent_dispatched_not_actualadmission':True}))";i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);report.update(status='ORIGINAL_TWO_EX_EVAL_PARENT_DISPATCHED_NO_PPO',parent=json.loads(text));marker.write_text(json.dumps(report,indent=2),encoding='utf-8')
finally:s.close();c.close();reportfile.write_text(json.dumps(report,indent=2),encoding='utf-8');print(reportfile);print(json.dumps(report,indent=2))
