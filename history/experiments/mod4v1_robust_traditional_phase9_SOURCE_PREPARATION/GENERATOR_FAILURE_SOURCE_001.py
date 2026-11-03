"""Derive a new PH9 bounded capture from PH8 without editing/executing old preparation."""
from pathlib import Path
import ast,hashlib,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
def main():
 base=WT/'history/experiments/mod4v1_robust_traditional_phase8_SOURCE_PREPARATION/prepare_source.py';raw=base.read_bytes();text=raw.decode('utf-8');changes=[]
 def change(old,new):
  nonlocal text
  assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new);changes.append(old)
 tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PRIOR'for t in n.targets));prior=ast.literal_eval(node.value)
 prior.append(('mod4v1_robust_traditional_phase8_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','662204600bf79ace36815db569a5d02f3b327981'))
 change(ast.get_source_segment(text,node),'PRIOR='+repr(prior))
 text=text.replace('PH8','PH9').replace('prior_PH1_to_PH7_saved_SHA','prior_PH1_to_PH8_saved_SHA');changes.append('PH8 labels->PH9 and inherited-reference label')
 change("PH9_ARCHIVE_CUTOFF_R62_INSIGHT.json","PH9_ARCHIVE_CUTOFF_R63.json")
 change("authority['status']=='PARENT_EXPLICIT_CLOSED_SOURCE_SNAPSHOT_ONLY_NOT_GIT_APPROVAL'","authority['status']=='CLOSED_R63_SOURCE_SNAPSHOT_ONLY_NOT_GIT_APPROVAL'")
 change(next(l for l in text.splitlines()if l.lstrip().startswith('closed_batches=sorted('))," closed_batches=[(S/x).resolve()for x in authority['actual_closed_batch_dirs']];assert len(closed_batches)==4 and all(p.is_dir()and p.is_relative_to(S/'batches')for p in closed_batches)")
 change("modules=[(S/x).resolve()for x in authority['included_closed_root_dirs']];root_names={p.name for pattern in authority['included_root_filename_families_if_actual_files_exist']for p in S.glob(pattern)if p.is_file()}|{authority_path.name}","modules=[(S/x).resolve()for x in authority['included_closed_dirs']];root_names={Path(x).name for x in authority['root_files_if_existing']if Path(x).parent==Path('.')}|{authority_path.name}")
 change("if any(int(x)>=63 for x in ROUND.findall(low)):return 'R63plus_future_excluded'","if any(int(x)>=64 for x in ROUND.findall(low)):return 'R64plus_future_excluded'")
 change(next(l for l in text.splitlines()if "return 'explicit_active_R63_workflow_excluded'"in l),"  if any(x in low for x in ('takeoff_momentum_capture_method_v1','phase10_pending')):return 'active_momentum_method_or_PH10_postcut_excluded'")
 change("for name in authority['included_result_reports']:","for name in [x for x in authority['root_files_if_existing']if Path(x).parent!=Path('.')]:")
 change("receipt=WT/authority['included_prior_postcommit_receipt']","receipt=WT/'history/experiments/mod4v1_robust_traditional_phase9_PENDING/ARCHIVE_PHASE8_RECEIPT.json'")
 change("'prior_commit':'223577994e0f750e0ae062ce9ffee204273c90a2'","'prior_commit':'662204600bf79ace36815db569a5d02f3b327981'")
 text=text.replace('not_actual_closed_R62_PROTOCOL_case_no_result_sweep','not_actual_closed_R63_PROTOCOL_case_no_result_sweep').replace('postcut_phase9_pending','postcut_phase10_pending')
 ast.parse(text);dest=P/'prepare_source.py';assert not dest.exists();dest.write_text(text,encoding='utf-8',newline='\n')
 print('PH9_NEW_CAPTURE_DERIVATION_AST_OK',hashlib.sha256(raw).hexdigest(),hashlib.sha256(dest.read_bytes()).hexdigest(),len(changes))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(P/f'GENERATOR_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'GENERATOR_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'GENERATOR_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
