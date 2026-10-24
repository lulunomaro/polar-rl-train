from pathlib import Path
import ast,hashlib,json,subprocess,time,tomllib
O=Path(__file__).resolve().parent.parent;T=O.parent;W=T.parent;R=O/'reports';G=W/'polar-rl-train';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_NINTH_V2_20261024';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_20261024'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=read(R/'CURRENT65_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json');a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for key in ('name','prompt','status','rrule','kind'):assert a[key]==args[key],key
assert a['target_thread_id']==args['targetThreadId'] and a['status']=='ACTIVE' and not a['prompt'].endswith('\n')
assert '2268000s630h/9extensions' in a['prompt'] and 'same_authorized_session_compressed_transport_v44.py' in a['prompt'] and '20:51:59.229161' in a['prompt']
proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');active=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');future=read(R/'NEXT66_CURRENT_CLEARANCE_V4_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json')
assert future['paired_predecessor']==N.name and future['E_equals_P'] and future['no_future_payload_model_Task_GO_or_fee']
for key in ('h1','recovery'):assert active['source210']['current']['go'][key]['source_SHA']==proof['models'][key]['final']['SHA']
for part in ('payloads','controllers','current_pair_closed_models','job0'):assert not (F/part).exists()
for p in F.glob('*.py'):ast.parse(p.read_text('utf8'))
for p in (N/'repair_sources').rglob('*'):
 if p.is_file():assert p.read_bytes()==(F/'repair_sources'/p.relative_to(N/'repair_sources')).read_bytes()
assert H(N/'collect_selected_pair_finals_unused_once.py')==H(P/'collect_selected_pair_finals_unused_once.py')==H(F/'collect_selected_pair_finals_unused_once.py')
prep=(F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8');assert f"P=T/'{N.name}';E=T/'{N.name}'" in prep and '720000' not in prep
helper=C/'append_current_clearance_v4_closed64_pair65_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s);assert 'read_capture_index(p,G)' in s and 'write_capture_index' in s and 'len(tags.splitlines())==1432' in s
assert 'MOD4_MOE_PLAYER_SPEED_TIMEBASE_20261024/REPORT_CAPTURE_INDEX.json' in s
cfg=read(C/'reports/CURRENT_CLEARANCE_V4_CLOSED64_PAIR65_ORDINARY_CONFIG.json');head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert head==cfg['base_HEAD']=='7180cc5218062548e7a67ba5e11a58465612e3c5'
assert not subprocess.check_output(['git','-C',str(G),'status','--porcelain'],text=True).strip()
report=dict(epoch=time.time(),passed=True,monitor_exact_prompt_status_rrule_target=True,monitor_prompt_SHA=hashlib.sha256(args['prompt'].encode()).hexdigest(),no_terminal_LF=True,latest_complete64_sources_match65_actual_GO=True,future66_source_only_dynamic_paired65_sources=True,no_first_grant_compensation=True,repair_sources_byteexact=True,collector_byteexact=True,part_aware_ordinary_index_and_1432_old_tags=True,ordinary_helper=str(helper),ordinary_helper_SHA=H(helper),base_HEAD=head,no_PT_raw_GPU_hostquery_or_budget_write=True)
with (R/'CLOSED64_MONITOR_FUTURE66_ORDINARY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,monitor_exact=True,future66_source_only=True,ordinary_ready=True,base_HEAD=head)))
