"""Prepare source-bound future closing/evaluation helpers, no transport or execution."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'paid_mean_public4_v2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 files=[]
 text=(P/'collect_existing_public4_V2_final_cost_exit_once.py').read_text('utf8')
 text=text.replace('from deploy_public4_repair_V2_new_native_then_original_finite1800_once import a,SOURCE,TARGET','from deploy_human_approved_ce3_new_native_then_one_finite1800_once import a,SOURCE,TARGET')
 text=text.replace('PUBLIC4_V2_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json','CE3_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json').replace('public4_v2','ce3_approved_segment')
 files.append(('collect_existing_ce3_final_original_cost_exit_once.py',text))
 text=(P/'review_public4_V2_full_final_model_original_cost_CPU_once.py').read_text('utf8')
 text=text.replace('PUBLIC4_V2_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json','CE3_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json').replace('PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json','CE3_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json')
 text=text.replace("src=B/'payload/h1/job0/source/H1_final10_protected.pt'","src=B/'payload/h1/job0/source/H1_ce3_public4_closed24.pt'").replace('b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce','ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90').replace('645620','646100').replace("==16363","==81434")
 text=text.replace("ledger=v['account']['original_canonical'];go=", "dispatch=json.loads((R/'HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json').read_bytes());assert dispatch['owner']['detached_pid']==81434;ledger=v['account']['original_canonical'];go=")
 files.append(('review_ce3_closed_final_whole_model_original_cost_CPU_once.py',text))
 old=B.parent/'prepare_public4_V2_complete_final_Linux_GPU1_frozen_CPU_once.py'
 text=old.read_text('utf8')
 text=text.replace("X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018'","X=B.parent.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018'")
 text=text.replace("B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json'","B/'reports/CE3_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json'")
 text=text.replace('step==645620+20*updates','step==646100+20*updates')
 text=text.replace('frozen_public4_final_linux_v1','frozen_ce3_continued_final_linux_v1')
 text=text.replace('H1_PUBLIC4_FINAL','H1_CQ3_FINAL').replace('h1_public4_finite_final','h1_cq3_finite_final').replace('PUBLIC4_V2_FINAL','CQ3_CLOSED_FINAL')
 text=text.replace("sourceguard9", "sourceguard9")
 # Source guard is built from b326 as before; its step substitution remains 645620 -> actual final.
 files.append(('prepare_ce3_closed_final_Linux_GPU1_frozen_CPU_once.py',text))
 out=[]
 for name,text in files:
  ast.parse(text);p=B/name
  with p.open('x',encoding='utf8') as f:f.write(text)
  out.append(dict(path=str(p),SHA=H(p),prepared_only_not_executed=True))
 with (R/'CE3_FUTURE_CLOSING_AND_NEW_SOURCE_FROZEN_HELPERS_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),helpers=out,original_source_Adam646100_expected_final646100_plus20updates=True,original_owner81434_bound=True,new_final_full_CPU_required_before_own_new_frozen_package=True,no_host_or_GPU_or_account_mutation=True),f,indent=2)
 print(json.dumps(dict(prepared_helpers=len(out),no_execution=True)))

if __name__=='__main__':main()
