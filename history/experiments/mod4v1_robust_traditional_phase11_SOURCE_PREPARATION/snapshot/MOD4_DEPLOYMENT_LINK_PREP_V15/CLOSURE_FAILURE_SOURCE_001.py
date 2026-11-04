from pathlib import Path
import datetime,json,hashlib,re
D=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102\MOD4_DEPLOYMENT_LINK_PREP_V15')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))
r=load(D/'MINIMUM_INPUT_REGISTRY.json');a=load(D/'FIRST_LINK_UNEXECUTED_DRAFT.json');q=load(D/'LINKER_QUERY_LEDGER.json');pins=load(D/'SOURCE_INPUT_PINS.json')
assert len(r['objects'])==163 and len(r['libraries'])==2 and [x['source_id']for x in r['objects']]==list(range(163))and r['payload_reads']==r['payload_hashes']==0
assert q['native_queries']==1 and q['returncode']==0 and a['first_link_executed']is False and len(a['expanded_literal_argv'])==len(r['objects'])+len(r['libraries'])+13
assert all(sha(Path(x['path']))==x['SHA']for x in pins['files'])
report=D/'REPORT.md';n=len(report.read_text(encoding='utf-8').splitlines())+1;assert n<=30
for link in re.findall(r'\]\(<([^>]+)>\)',report.read_text(encoding='utf-8')):assert(report.parent/link).exists()
files=['MINIMUM_INPUT_REGISTRY.json','PROJECT_MEMORY_SELECTION.json','PROJECT_MEMORY_EXCERPT.txt','diagnostic_IROM1_IRAM1_DRAFT.sct','FIRST_LINK_UNEXECUTED_DRAFT.json','first_link_UNEXECUTED.via','LINKER_QUERY_INTENT.json','LINKER_QUERY_LEDGER.json','armlink_help.stdout.txt','armlink_help.stderr.txt','SOURCE_INPUT_PINS.json','prepare_metadata_once.py','REPORT.md']
x=dict(status='COMPLETE_V15_STATIC_163OBJECT_2LIB_MEMORY_AND_OWNHELP_LINK_NOT_EXECUTED',created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),objects_stat_checked=163,user_libraries_stat_checked=2,total_object_producer_file_bytes_not_ROM_usage=sum(z['object']['bytes']for z in r['objects']),object_and_library_payload_reads_or_hashes=0,ARM_native_invocations=dict(armlink_own_help=1,armlink_link=0,compile=0,assembly=0,fromelf=0,armar=0,UV=0,version_query=0),ownhelp_returncode=0,ownhelp_stdout_bytes=(D/'armlink_help.stdout.txt').stat().st_size,ownhelp_stderr_bytes=(D/'armlink_help.stderr.txt').stat().st_size,complete_unexecuted_literal_expanded_argv=True,project_memory_from_explicit_selected_config_not_guessed_board=True,oldscatter_and_old_gates_and_producer_receipts_unchanged=True,scope_is_old_BSP_Stage1_not_latest_MOD4_firmware_or_single_build=True,model_FK_PHY_oldQA_Git_newagents_Goal_flash=0,V5_core_proof_or_admission_files_touched=False,report_plus_receipt_lines=n,all_small_input_before_after_SHA_equal=True,artifacts=[meta(D/f)for f in files],unknowns=a['unknowns'],firstlink_or_flash_permission=False,PH11pending=True)
p=D/'RECEIPT.json';assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(dict(status=x['status'],counts=x['ARM_native_invocations'],objects=163,libs=2,report_and_receipt_lines=n,report_SHA=sha(report),receipt_SHA=sha(p),registry_SHA=sha(D/'MINIMUM_INPUT_REGISTRY.json'),draft_SHA=sha(D/'FIRST_LINK_UNEXECUTED_DRAFT.json'),unexecuted=True),ensure_ascii=False))
