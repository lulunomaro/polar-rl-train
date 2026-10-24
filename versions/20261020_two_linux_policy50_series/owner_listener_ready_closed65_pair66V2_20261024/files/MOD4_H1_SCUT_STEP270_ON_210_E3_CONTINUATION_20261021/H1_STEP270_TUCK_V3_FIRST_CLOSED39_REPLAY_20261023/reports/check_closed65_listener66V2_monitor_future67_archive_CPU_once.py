from pathlib import Path
import ast,copy,hashlib,json,subprocess,time,tomllib
O=Path(__file__).resolve().parent.parent;R=O/'reports';T=O.parent;W=T.parent;G=W/'polar-rl-train';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024';OLD=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_20261024';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V67_20261024'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=read(R/'CURRENT66_LISTENER_V2_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json');a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for key in ('name','prompt','status','rrule','kind'):assert a[key]==args[key],key
assert a['target_thread_id']==args['targetThreadId'] and a['status']=='ACTIVE' and not a['prompt'].endswith('\n') and '22:03:08.964437' in a['prompt'] and 'same_authorized_session_compressed_transport_v47.py' in a['prompt']
proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');active=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');race=read(N/'reports/LISTENER_READY_RACE_SOURCE_AND_SYNTHETIC_CPU_ACTUAL.json');failure=read(OLD/'reports/FAILED66_LISTENER_V2_NO_NODES_NO_GO_TWOHOST_ALL_OUT_ACTUAL.json');future=read(R/'NEXT67_CURRENT_CLEARANCE_V4_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json')
assert failure['passed'] and failure['no_actual_GO_or_fee'] and failure['canonical_unchanged_no_new_segment_or_charge'] and active['passed'] and active['actual_finite_returned']
for key in ('h1','recovery'):assert active['source210']['current']['go'][key]['source_SHA']==proof['models'][key]['final']['SHA']
oldtree=ast.parse((OLD/'deploy_selected_pair_unused_once.py').read_text('utf8').replace('H1step270_reward_tuckclear4_2410v66','H1step270_reward_tuckclear4_2410v66listenerv2'));newtree=ast.parse((N/'deploy_selected_pair_unused_once.py').read_text('utf8'))
class Restore(ast.NodeTransformer):
 def visit_Constant(self,node):
  if node.value==race['exact_new_remote_ready_code']:return ast.copy_location(ast.Constant(value=race['exact_old_remote_ready_code']),node)
  return node
assert ast.dump(oldtree,include_attributes=False)==ast.dump(Restore().visit(copy.deepcopy(newtree)),include_attributes=False)
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):
 for p in (OLD/folder).rglob('*'):
  if p.is_file():assert p.read_bytes()==(N/folder/p.relative_to(OLD/folder)).read_bytes()
for part in ('payloads','controllers','current_pair_closed_models','job0'):assert not (F/part).exists()
for p in F.glob('*.py'):ast.parse(p.read_text('utf8'))
assert future['paired_predecessor']==N.name and future['E_equals_P'] and future['bounded_paired_listener_readiness_wait_inherited']
assert H(P/'collect_selected_pair_finals_unused_once.py')==H(N/'collect_selected_pair_finals_unused_once.py')==H(F/'collect_selected_pair_finals_unused_once.py')
prep=(F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8');assert f"P=T/'{N.name}';E=T/'{N.name}'" in prep and '720000' not in prep
helper=C/'archive_closed65_listener66V2_unique_once.py';s=helper.read_text('utf8');ast.parse(s);assert 'read_capture_index(p,G)' in s and 'write_capture_index' in s and 'len(tags.splitlines())==1432' in s and s.count('rec.main()')==1
ordinary=(C/'append_current_clearance_v4_closed65_pair66_ordinary_once.py').read_text('utf8');assert 'len(tags.splitlines())==1433' in ordinary
cfg=read(C/'reports/LISTENER66V2_UNIQUE_CONFIG.json');head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert head==cfg['base_HEAD']=='3d8cf5e76e2e781ad92aff81b3fb0ef133e97e9d'
assert not subprocess.check_output(['git','-C',str(G),'status','--porcelain'],text=True).strip()
report=dict(epoch=time.time(),passed=True,monitor_prompt_status_rrule_target_exact=True,no_terminal_LF=True,latest_complete65_source_SHA_match66V2_actual_GO=True,deployer_AST_only_bounded_readiness_wait_and_unused_namespace_paths=True,all_original_owner_controller_node_repair_source_bytes_unchanged=True,future67_source_only_dynamic66V2_sources_and_bounded_wait=True,no_first_grant_compensation=True,collector_byteexact=True,part_aware_unique_archive_1432_old_tags_and_once_record=True,unused_future_ordinary_1433_tags=True,helper=str(helper),helper_SHA=H(helper),base_HEAD=head,no_PT_raw_GPU_hostquery_or_budget_write=True)
with (R/'CLOSED65_LISTENER66V2_MONITOR_FUTURE67_ARCHIVE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,monitor_exact=True,only_listener_wait_AST_change=True,future67_source_only=True,unique_archive_ready=True)))
