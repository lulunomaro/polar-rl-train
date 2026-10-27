from pathlib import Path
import importlib.util,runpy,sys,json,time
HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
READ_C=r"""from pathlib import Path
import json,hashlib,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==554499.7579419613 and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
assert c['remaining_training_seconds']>86412.86069250107
print(json.dumps(dict(passed=True,epoch=time.time(),canonical_SHA=hashlib.sha256(raw).hexdigest(),active_segment_None=True,authority_generation=c['authority_generation'],mode=c.get('budget_mode',c.get('mode')),remaining_training_seconds=c['remaining_training_seconds'],authorized_training_seconds=c['authorized_training_seconds'],historical_budget_extension_count=9,new_authority_budget_extensions_empty=True,read_only_no_ledger_copy_or_write=True)))
"""
def main():
 target=HERE/'install_W35_existing72_frozen_source_and_initial_SDK_CPU_once_v2_postcopy.py';assert len(sys.argv)==1
 path=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
 sp=importlib.util.spec_from_file_location('same_authorized_zstd_memory_W35_readC_V3',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 original=d.connect72
 def connect(secret):
  c=original(secret)
  try:
   row=d.code(c,d.PY72,READ_C,{},timeout=20)
   with (HERE/'reports/W35_FRESH_C72_CLOSED_NONE_READONLY_ACTUAL_V3.json').open('x') as f:json.dump(row,f,indent=2)
   return c
  except BaseException:c.close();raise
 d.connect72=connect
 try:sys.argv=[str(target)];runpy.run_path(str(target),run_name='__main__')
 finally:d.connect72=original;transport.SESSION=previous
if __name__=='__main__':main()
