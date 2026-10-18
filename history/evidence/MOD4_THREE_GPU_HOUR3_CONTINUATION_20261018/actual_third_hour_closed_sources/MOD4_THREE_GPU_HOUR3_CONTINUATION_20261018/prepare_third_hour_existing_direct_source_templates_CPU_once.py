"""Prepare unchanged three-expert continuation from the now-closed second hour."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True);U=B.parent/'MOD4_THREE_GPU_HOUR2_CONTINUATION_20261018'
def write(name,s):
 ast.parse(s)
 with (B/name).open('x',encoding='utf8') as f:f.write(s)
def main():
 f=json.loads((U/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free']
 s=(U/'closed_production_continuation_CPU_v2.py').read_text('utf8');start=s.index(" if p['key']=='recovery':\n");end=s.index(' return text\n',start);s=s[:start]+s[end:];write('closed_production_continuation_CPU_v2.py',s)
 s=(U/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8').replace("T=W/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018'","T=W/'MOD4_THREE_GPU_HOUR2_CONTINUATION_20261018'").replace('THREE_REAL_GPU_ONE_HOUR_NATIVE_REUSE_AND_LEARNING_DETACHED_ACTUAL.json','THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').replace("T/'controllers_v2'","T/'controllers'").replace("T/'controllers_v2/three_slot_common_v1.py'","T/'controllers/three_slot_common_v1.py'").replace("T/'controllers_v2/three_slot_finite_owner_v1.py'","T/'controllers/three_slot_finite_owner_v1.py'").replace("T/'controllers_v2/three_slot_finite_node_v1.py'","T/'controllers/three_slot_finite_node_v1.py'")
 a="assert \"row.get('key')=='h1'\" in txt;txt=txt.replace(\"row.get('key')=='h1'\",\"row.get('key')==spec['key']\")";assert a in s;s=s.replace(a,"assert \"row.get('key')==spec['key']\" in txt")
 s=s.replace("('e2_paid' if key=='e2' else key)",'key');a="name={'h1':'H1_closed_hour73.pt','e2':'E2_closed_hour241.pt','recovery':'E3_closed_hour95.pt'}[key]";assert a in s;s=s.replace(a,"name=key.upper()+'_closed_hour'+str(r['updates'])+'.pt'")
 start=s.index("  if key=='recovery':\n");end=s.index('  (dest/worker)',start);s=s[:start]+s[end:];s=s.replace('T3h2_1810v2/','T3h3_1810v3/').replace('THREE_GPU_CLOSED_HOUR2_','THREE_GPU_CLOSED_HOUR3_');write('prepare_next_three_closed_sources_one_hour_CPU_once.py',s)
 s=(U/'deploy_three_next_closed_source_hours_once.py').read_text('utf8').replace("SOURCE='/mnt/mod4_linux_durable_20261013/T3h2_1810v2/owner'","SOURCE='/mnt/mod4_linux_durable_20261013/T3h3_1810v3/owner'").replace("A=Path('/mnt/mod4_linux_durable_20261013/T3h_1810v1/owner')","A=Path('/mnt/mod4_linux_durable_20261013/T3h2_1810v2/owner')").replace('137670','150567');write('deploy_three_next_closed_source_hours_once.py',s)
 write('collect_next_three_actual_learning_metadata_finite_once.py',(U/'collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf8'))
 with (R/'THIRD_HOUR_EXISTING_DIRECT_SOURCE_TEMPLATE_BINDING_CPU_ACTUAL.json').open('x',encoding='utf8') as h:json.dump(dict(epoch=time.time(),template_AST_passed=True,previous_actual_owner=150567,all_three_previous_finals_CPU_passed=True,E3_already_direct_source_only_filename_Adam_normalization=True,no_remote_or_GPU_or_account_mutation=True),h,indent=2)
if __name__=='__main__':main()
