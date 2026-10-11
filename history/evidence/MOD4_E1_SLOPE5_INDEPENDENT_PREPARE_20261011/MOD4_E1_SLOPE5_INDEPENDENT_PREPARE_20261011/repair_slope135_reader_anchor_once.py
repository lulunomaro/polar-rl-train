"""Finish unexecuted reviewer after pre-review literal guard; preserve first builder."""
from slope_io import *
def main():
 save('SLOPE135_READER_BUILDER_LITERAL_REJECTED.json',dict(epoch=time.time(),trial_id='SLOPE135-READER-BUILDER-ANCHOR-LITERAL-REJECTION-01',original_source_SHA=H((D/'build_slope135_readers_once.py').read_bytes()),error='AssertionError: anchor literal still contained132-e1-curb after partial case-sensitive replacement',collector_created_but_reviewer_not_written=True,no_review_or_GPU_or_runtime_budget_mutation=True))
 old=(PRE/'review_slope134_actual.py').read_text();start=old.index("  s=p['route_scope'];");end=old.index('  reviews[jid]=',start)
 body=old[start:end].replace("R/'cases'/jid","folder");body='\n'.join(' '+x for x in body.splitlines())
 header='''from slope_io import *
import numpy as np,traceback
sys.path.insert(0,str(PRE));from review_slope134_actual import terrain
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
read=lambda p:json.loads(p.read_bytes())
def audit(p,folder):
'''
 audit=header+body+"\n   return dict(base_review=base,groups=summary,rows=rows,all_valid_prefixes_retained=True,standing_not_required_to_cross=True)\n"
 schema=(P/'review_formal_reviewed_curb133_schema_actual.py').read_text();a=schema.index('def main():');z=schema.index("if __name__=='__main__':")
 m=schema[a:z].replace('CURB133','SLOPE135').replace('curb133','slope135').replace('CURB132','SLOPE134').replace('curb132','slope134').replace('CURB20','SLOPE5')
 m=m.replace('b91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d','f94fc989a1dd8a02a7b535aa7974a8172a9441762563518970a756a46fcb8bc9')
 line=next(x for x in m.splitlines() if 'anchor=read(' in x)
 m=m.replace(line,"   anchor=read(PRE/'reports/cases/clk2500-closure-episode-d3-134-e1-slope5-source364-mirrored-fullroute-flat/probe.json')")
 assert '132-e1-curb' not in m and 'slope5-source364' in m
 m=m.replace('no_gate_or_RM002_or_full_E1_graduation','no_gate_or_actual_RM_slope_or_full_E1_graduation')
 text=audit+m+'''if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE135_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,original_results_not_relabelled=True));raise
'''
 p=D/'review_slope135_actual.py';assert not p.exists();compile(text,str(p),'exec');p.write_bytes(text.encode())
 save('SLOPE135_READERS_PREPARED.json',dict(epoch=time.time(),collector_SHA=H((D/'collect_slope135_actual.py').read_bytes()),reviewer_SHA=H(text.encode()),reader_literal_fixed_before_any_review=True,no_eval_replay=True,actual_fullsave_PASSED_and_complete_errorfree_only=True,baseline134_same_geometry_initial_and115_129_skill_contracts=True,original_tolerances_unchanged=True))
if __name__=='__main__':main()
