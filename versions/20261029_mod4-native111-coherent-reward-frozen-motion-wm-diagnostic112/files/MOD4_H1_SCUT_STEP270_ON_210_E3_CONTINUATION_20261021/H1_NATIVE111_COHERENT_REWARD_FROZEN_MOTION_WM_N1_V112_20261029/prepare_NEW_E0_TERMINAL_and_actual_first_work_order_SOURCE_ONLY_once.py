from pathlib import Path
import ast,json,hashlib,time,datetime
S=Path(__file__).resolve().parent
old=S/"run_NEW_E0_V1_FIRST360_AST_RECOVER_ONLY_secure_ingress_UNUSED_once.py";s=old.read_text(encoding="utf8")
pairs=[
("read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py","collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py"),
("448a54f54285add3c804af2af0aee3b1e861075a72dd2ea05c9558cc02edf097","f67c381a254f729ed860a4becd87cb449fb3864808efc88799a7c8d90714a6f3"),
("E0_V4_FIRST_DISTINCT_READ_CONSUMED_BEFORE_STDIN.json","E0_V4_TERMINAL_DISTINCT_READ_CONSUMED_BEFORE_STDIN.json"),
("ROOT_E0_V1_FIRST_","ROOT_E0_V1_TERMINAL_"),
("NEW_E0_V1_FIRST_SECURE_SAME_HANDLE","NEW_E0_V1_TERMINAL_SECURE_SAME_HANDLE"),
("SAME_FINITE_NEW_E0_V1_FIRST","SAME_FINITE_NEW_E0_V1_TERMINAL"),
("time.time()-start>470","time.time()-start>950")]
for a,b in pairs:assert a in s,a;s=s.replace(a,b)
assert 'run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py' in s
compile(s,"E0_TERMINAL_NEW","exec")
p=S/"run_NEW_E0_V1_TERMINAL_AST_RECOVER_ONLY_secure_ingress_UNUSED_once.py"
with p.open("x",encoding="utf8",newline="\n") as f:f.write(s)
D=S.parent/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1"
start=D/"reports/NEW86_E0_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json"
first=D/"reports/E0_V4_FIRST_ORIGINAL_RETURNED_ACTUAL.json"
j=json.loads(start.read_bytes());f=json.loads(first.read_bytes())
assert j["passed_source_CPU_and_detached_only"] and f["passed_first_actual_E0_CUDA_fullrestore_native24_queue"] and not f["original_errors"] and not f["integrity"]
creation=j["detached"]["identity"]["creation"];tz=datetime.timezone(datetime.timedelta(hours=8))
value=dict(epoch=time.time(),actual_startup_report=str(start),startup_SHA=hashlib.sha256(start.read_bytes()).hexdigest(),actual_first_report=str(first),first_SHA=hashlib.sha256(first.read_bytes()).hexdigest(),actual_initial_GPU_fullrestore_native24_queue=True,first_identity_snapshot_not_continuousalive=True,supervisor=f["supervisor_state"]["expected"],worker=f["worker_state"]["expected"],source_model_SHA="a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a",original_Adam=641200,original_LR=.00038443359375000017,actual_target_CPU_model_decodes=0,full1000_not_yet_proven=True,no_learner_or_GO_Cwrite=True,normal_exact_entry=str(p),normal_entry_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),normal_UNUSED=True,normal_earliest_epoch=creation+900,normal_earliest_BJT=datetime.datetime.fromtimestamp(creation+900,tz).isoformat(),original_supervisor_nominal_BJT=datetime.datetime.fromtimestamp(creation+1800,tz).isoformat(),normal850_max_wait=True,local_remote900_gate_retained=True,all_root_local_finite_handles_returned_leasefree=True,original_source_V1_consumer_names_E0_V4_historical_only=True)
with (S/"reports/ACTUAL_NEW86_E0_V1_INITIAL_NATIVE24_AND_UNUSED_NORMAL_WORK_ORDER.json").open("x",encoding="utf8") as f:json.dump(value,f,indent=2)
print(json.dumps({k:value[k] for k in ["actual_initial_GPU_fullrestore_native24_queue","normal_exact_entry","normal_entry_SHA","normal_earliest_BJT","original_supervisor_nominal_BJT"]}))

