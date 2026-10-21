from pathlib import Path
import ast,hashlib,json,shutil,subprocess,time,tomllib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';C=W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021';G=W/'polar-rl-train';P=W/'MOD4_TWO_LINUX_POLICY50_COHORT_48_20261021';F=W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021'
args=json.loads((R/'V83_EXISTING_MONITOR_FINAL_UPDATE_ARGS.json').read_bytes());raw=(Path.home()/'.codex/automations/mod4-10/automation.toml').read_bytes();monitor=tomllib.loads(raw.decode());assert monitor['prompt']==args['prompt'] and monitor['status']=='ACTIVE' and monitor['target_thread_id']==args['targetThreadId'] and monitor['rrule']==args['rrule']
with (R/'V83_PREARCHIVE_EXACT_MONITOR_READBACK_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,automation_id='mod4-10',status=monitor['status'],rrule=monitor['rrule'],target=monitor['target_thread_id'],prompt=monitor['prompt'],TOML_SHA=hashlib.sha256(raw).hexdigest(),app_receipt='V83_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json'),f,ensure_ascii=False,indent=2)
source=(P/'archive_authorized_two_slot_budget_repair_V81_unique_once.py').read_text('utf8')
source=source.replace("for base in (P,B,N)","for base in (P,B,N,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021')")
source=source.replace("'e2-e3-scheduled-two-slot-budget-guard-approved-v81'","'budget-add100h-cleanup-shared-eval-two50-v83'")
source=source.replace("str(B/'ACTUAL_TWO50_CLOSED_AND_NEXT_LEARNING_V81_STAGE_NOTE.md')","str(W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/ACTUAL_BUDGET8_STORAGE_AND_SHARED_EVAL_V83_STAGE_NOTE.md')")
source=source.replace('Human explicitly approved scheduled E2/E3 caps; 10 CPU budget cases; target full source CPU; remote owner SHA exact; both actual GO/PPO/UUID/createargv and original writer locks verified; no skill qualification.','Explicit eighth100h extension under original two fcntl; charge/history unchanged; authorized exact96 closed intermediate cleanup; failed49 disk guard retained; new50 both actual GO/PPO/UUID/createargv and remote full owner SHA; shared13 native60/480 with all-row CPU and full13 started; NTFS999 read-only hibernation refusal; no skill graduation.')
source=source.replace("kind='explicitly_approved_two_slot_budget_guard_repair_deployment'","kind='explicit_budget8_closed_checkpoint_cleanup_two50_continuation_and_shared_frozen_diagnostics'")
needle=" sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact"
addition=""" for suffix,local in (('', 'shared_H1_native13_actual'),('_V2','shared_H1_native13_V2_actual'),('_V3','shared_H1_native13_V3_actual')):
  rp=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports'/('SHARED_H1_NATIVE13'+suffix+'_FINITE_RETURNED_ACTUAL.json')
  if rp.exists():
   for row in json.loads(rp.read_bytes()).get('raw',[]):known[str((W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'/local/row['relative']).resolve())]=row['SHA']
""";assert needle in source;source=source.replace(needle,addition+needle)
ast.parse(source);dest=C/'archive_budget8_cleanup_shared_eval_two50_V83_unique_once.py';dest.open('x',encoding='utf8').write(source)
head=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();status=subprocess.check_output(['git','-C',str(G),'status','--porcelain'],text=True);assert not status
cfg=dict(base_HEAD=head,destination='budget8_cleanup_shared_eval_V83_20261021',title='Explicit eighth100h original-ledger extension, verified closed-checkpoint cleanup, isolated two50 continuation and shared-H1 frozen diagnostics; preserve all original failures and NTFS hibernation refusal')
with (C/'reports/V83_UNIQUE_ARCHIVE_CONFIG.json').open('x',encoding='utf8') as f:json.dump(cfg,f,indent=2)
for root in (C,N):
 p=root/'append_two50_closed_and_learning_ordinary_TEMPLATE.py';s=p.read_text('utf8');shutil.copy2(p,root/'append_two50_ordinary_before_budget8_eval_capture_UNUSED_RETAINED.py');s=s.replace("for base in (P,B,N)","for base in (P,B,N,W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021')");ast.parse(s);p.write_text(s,encoding='utf8')
with (R/'V83_ARCHIVE_READY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,base_HEAD=head,source_archive_helper=str(dest),helper_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),scope=[str(p) for p in (P,F,C,N,B)],all_saved_new_sources_errors_and_reports_in_capture_scope=True,known_new_native_raw_producer_SHA_reused=True,no_binary_rehash_for_Git=True,unique_trial_not_yet_recorded=True,same_monitor_readback_exact=True),f,indent=2)
print(json.dumps(dict(ready=True,base_HEAD=head,helper=str(dest),argument='V83_UNIQUE_ARCHIVE_CONFIG.json')))
