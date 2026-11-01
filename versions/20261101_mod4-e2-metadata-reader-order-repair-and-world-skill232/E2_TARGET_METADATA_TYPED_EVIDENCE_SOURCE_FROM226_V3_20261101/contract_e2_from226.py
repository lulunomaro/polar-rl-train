"""JSON-only ROOT receipt joins. No model,asset,process,SDK or network APIs."""
from pathlib import Path
import hashlib
import json

MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
MODEL_PATH='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt'
WORKER='91f7e30febee3f4f8910cdedb4739d87f19b01c131f79d4396d335598b1ca6ab'
EXPECTED='4e2b124c315853e4a4b44317bfe38d2825eebc7ca47d0ddb2a42c57b5ed11cd0'
PENDING_TASK='f40e765e8ed300800c0bb898faf3dff18515e7f1854146601746fe578c2fddcd'
PROBE='229657f7d579fc7dca90f761f4b3cacaa35e8649ddab3f129229bb4269e9a122'
KIND='NEW_E2_FROM226_V3_LEXICAL_SOURCE_SDK_METADATA'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GLOBAL='/home/lc01/Zonglin Li/zonglin2'


def require(value,reason):
 if not value:raise ValueError(reason)


def read_metadata(path):
 p=Path(path);require(p.suffix=='.json' and not p.name.endswith(('.partial','.active')),'Complete JSON metadata only')
 b=p.read_bytes();return json.loads(b),dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())


def refs(value):
 require(isinstance(value,list) and value,'Actual producer receipt references required')
 for r in value:require(r['path'] and type(r['bytes']) is int and r['bytes']>0 and len(r['SHA'])==64,'Actual report identity')


def authority(value,purpose_id,job):
 require(value['kind']=='ROOT_E2_FROM226_CURRENT_AUTHORITY_ACTUAL','Current authority kind')
 require(value['purpose_id']==purpose_id and value['job_root']==str(job),'Current purpose/job binding')
 require(value['passed'] is True and value['fresh_actual_read'] is True and not value.get('synthetic_fixture_only'),'Actual ROOT fresh checks only')
 refs(value['actual_report_refs'])
 c=value['canonical']
 require(c['path']==CANONICAL and c['generation']=='MOD4_SINGLE_WRITER72_20261026' and c['total_authorized_seconds']==2268000,'Original authority identity')
 require(value['no_new_writer_budget_GO_or_account_write'] is True,'Read-only authority scope')
 mode=value['mode']
 if mode=='FRESH_CNONE':
  require(c['active_segment'] is None and value['all_prior_learning_owners_and_control_clients_closed'] is True,'Actual closed-owner fresh CNone')
  return dict(mode=mode,checked_epoch=value['checked_epoch'],active_GPU_UUIDs=[],no_account_write=True)
 require(mode=='EXACT227D_ACTIVE','Only current227D or fresh closed CNone;old219 is historical')
 expected=value['expected227D'];current=value['current227D']
 require('227D' in expected['run_id'] and expected['owner']['cwd']==GLOBAL,'Expected current227D binding')
 keys=('pid','creation','exe','argv','cwd')
 require(current['run_id']==expected['run_id'] and all(current['owner'][k]==expected['owner'][k] for k in keys) and current['go']==expected['go'],'Fresh exact owner identity/run/GO join')
 require(c['active_segment'] is not None and c['active_segment']['owner_parent_pid']==expected['owner']['pid'],'Canonical actual owner match')
 require(set(current['go'])=={'w35_72'},'Original current one-role owner')
 go=current['go']['w35_72']
 require(go['run_id']==expected['run_id'] and go['role_key']=='w35_72' and go['one_original_writer'] is True,'Exact current original GO')
 require(go['source_model_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd' and go['source_iteration']==32404 and go['input_Adam']==649720,'Current227D W35 lineage')
 require(go['original_owner_pid']==expected['owner']['pid'] and go['original_owner_creation']==expected['owner']['creation'],'Original owner creation binding')
 require(go['source_CPU_SHA'] and go['manifest_SHA'],'Current original Ready/manifest binding')
 return dict(mode=mode,checked_epoch=value['checked_epoch'],run_id=expected['run_id'],owner=expected['owner'],
             GO=go,active_GPU_UUIDs=[go['GPU_UUID']],no_account_write=True)


def metadata_admission(value,purpose_id,job,authority_sha,launcher):
 require(value['kind']=='ROOT_E2_FROM226_CPU_METADATA_ADMISSION_ACTUAL','Metadata-only admission kind')
 require(value['purpose_id']==purpose_id and value['job_root']==str(job) and value['authority_report_SHA']==authority_sha,'New ROOT receipt join')
 require(value['passed'] is True and value['original_global_serial_control_admitted'] is True,'ROOT serial source-CPU admission')
 require(value['target_host']=='72' and value['actual_SDK_python_launcher']==str(launcher),'Actual selected target/Python')
 require(value['model_asset_GPU_App_access']==0 and value['no_training_GO_or_budget_writer'] is True,'CPU metadata only')
 refs(value['actual_report_refs'])


def runtime_admission(value,purpose_id,job,authority_sha,current,wait_finished):
 require(value['kind']=='ROOT_E2_FROM226_ACTUAL_RUNTIME_ADMISSION','Actual later runtime kind')
 require(value['purpose_id']==purpose_id and value['job_root']==str(job) and value['authority_report_SHA']==authority_sha,'Runtime current-authority join')
 require(current['checked_epoch']>=wait_finished,'New authority check after metadata wait,not the earlier snapshot')
 require(value['passed'] is True and value['source_SHA']==MODEL and value['worker_SHA']==WORKER and value['num_envs']==20000,'Exact E2 original worker/source')
 for k in ('original_private_EX_held','original_shared_guard_passed','original_resources_passed'):
  require(value[k] is True,'Actual held runtime condition: '+k)
 require(value['GPU_UUID'] not in current['active_GPU_UUIDs'],'Selected evaluation GPU differs from active W35')
 p=value['actual_holding_parent']
 require(type(p['pid']) is int and p['pid']>0 and p['creation']>0 and p['exe'] and p['cwd'],'Actual own holding parent identity')
 require(len(value['selected_private_lock_receipt_SHA'])==64 and value['no_new_training_GO_or_account_write'] is True,'Original runtime lock receipt / no learning')
 refs(value['actual_report_refs'])
 link=value['selected_source_materialization']
 require(link['actual_completed'] is True and link['selected_formal_SHA']==MODEL and link['selected_formal_bytes']==14615089,'Actual source materialization metadata')
 require(link['selected_target_path']==MODEL_PATH and link['job_relative']=='source/E2_ADAPTED93_FINAL92.pt','Qualified same-host E2 formal,never historical initial typed PT')
 require(link['method']=='same_host_symlink' and link['model_byte_reads_or_copies']==0,'This interface selects the original0byte symlink plan;copy requires separate source purpose')
 return True
