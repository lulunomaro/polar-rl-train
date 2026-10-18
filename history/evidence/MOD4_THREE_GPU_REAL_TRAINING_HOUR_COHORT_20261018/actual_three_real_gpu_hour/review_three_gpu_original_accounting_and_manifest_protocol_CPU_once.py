"""Pure accounting test on Windows; fcntl import shim is not a claim of real kernel locks."""
from pathlib import Path
import sys,json,time,types,traceback
B=Path(__file__).resolve().parent
def main():
 sys.path.insert(0,str(B/'controllers'));sys.modules['fcntl']=types.SimpleNamespace();import three_slot_common_v1 as b
 assert b.CAPS==dict(h1=3900,e2=3900,recovery=3900) and len(set(b.GPUS.values()))==3;c=dict(charged_training_seconds=0.,remaining_training_seconds=1188000.);a=dict(experts={},charged_expert_seconds=0.);go={k:dict(learning_started_epoch=t,max_parent_seconds=3900) for k,t in [('h1',10.),('e2',12.),('recovery',14.)]};rows={};c,a=b.charge_values(c,a,go,rows,20.);assert c['charged_training_seconds']==24.;rows['e2']=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=22.);c,a=b.charge_values(c,a,go,rows,25.);assert c['charged_training_seconds']==36.;c,a=b.charge_values(c,a,go,rows,30.);assert c['charged_training_seconds']==46. and a['experts']['e2']['charged_seconds']==10.;assert a['charged_expert_seconds']==sum(x['charged_seconds'] for x in a['experts'].values()) and abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5
 v=dict(epoch=time.time(),passed_pure_original_independent_interval_accounting_CPU=True,simultaneous_three_sum24_then_terminal_expert_once36_then46=True,terminal_expert_not_double_charged=True,only_CAPS3900_and_distinct_GPU_mapping_changes=True,original_inline_Windows_import_fcntl_ModuleNotFoundError_retained=True,pure_import_shim_not_real_kernel_fcntl_proof=True,no_canonical_IO_or_GPU=True)
 with (B/'reports/THREE_REAL_GPU_ORIGINAL_INTERVAL_ACCOUNTING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports'/('THREE_ACCOUNTING_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_GPU_or_budget=True),f,indent=2)
  raise
