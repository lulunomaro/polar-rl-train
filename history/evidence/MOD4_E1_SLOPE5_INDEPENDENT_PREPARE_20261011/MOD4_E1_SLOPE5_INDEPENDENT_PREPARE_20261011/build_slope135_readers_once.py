from slope_io import *
import ast
def main():
 collector=(PRE/'collect_slope134_actual.py').read_text()
 collector=collector.replace('from review133_io import *','from slope_io import *\nsys.path.insert(0,str(W/"MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011"))')
 collector=collector.replace(" published=json.loads((R/'SLOPE134_PUBLISHED.json').read_bytes());cases={};pending=[];files=[];n,w=connect_both()"," cases={};pending=[];files=[];n,w=connect_both()")
 collector=collector.replace("   actual=worker_actual(w,wf)","   actual=worker_actual(w,wf)\n   try:\n    published=json.loads(nf.open(NEW+'/reports/E1_SLOPE135_ASYNC_PUBLISHED.json').read());passed=json.loads(nf.open(NEW+'/reports/e1_SLOPE5_independent_observation_PASSED.json').read())\n   except FileNotFoundError:\n    p=save('SLOPE135_COLLECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),cases={},pending=[dict(phase='own_formal_final_and135publication_not_yet_generated')],actual_worker=actual,no_replay=True));print(json.dumps(dict(report=str(p),pending=True,attention=actual['attention'])));return")
 collector=collector.replace("actual_worker=actual,published=published,","actual_worker=actual,published=published,passed=passed,").replace('134','135')
 p=D/'collect_slope135_actual.py';assert not p.exists();compile(collector,str(p),'exec');p.write_bytes(collector.encode())
 old=(PRE/'review_slope134_actual.py').read_text();start=old.index("  s=p['route_scope'];");end=old.index('  reviews[jid]=',start)
 body=old[start:end];body=body.replace("R/'cases'/jid","folder")
 body='\n'.join(' '+x for x in body.splitlines())
 header='''from slope_io import *
import numpy as np,traceback
sys.path.insert(0,str(PRE));from review_slope134_actual import terrain
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
read=lambda p:json.loads(p.read_bytes())
def audit(p,folder):
'''
 audit=header+body+"\n   return dict(base_review=base,groups=summary,rows=rows,all_valid_prefixes_retained=True,standing_not_required_to_cross=True)\n"
 # Reuse the proven legacy skill result binding (not a nonexistent terrain SHA field).
 schema=(P/'review_formal_reviewed_curb133_schema_actual.py').read_text();a=schema.index('def main():');z=schema.index("if __name__=='__main__':")
 main=schema[a:z].replace('CURB133','SLOPE135').replace('curb133','slope135').replace('CURB132','SLOPE134').replace('curb132','slope134').replace('CURB20','SLOPE5')
 main=main.replace("b91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d","f94fc989a1dd8a02a7b535aa7974a8172a9441762563518970a756a46fcb8bc9")
 old_anchor="read(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/cases/clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat/probe.json')"
 main=main.replace(old_anchor,"read(PRE/'reports/cases/clk2500-closure-episode-d3-134-e1-slope5-source364-mirrored-fullroute-flat/probe.json')")
 assert old_anchor not in main and '132-e1-curb' not in main
 main=main.replace('no_gate_or_RM002_or_full_E1_graduation','no_gate_or_actual_RM_slope_or_full_E1_graduation')
 text=audit+main+'''if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE135_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,original_results_not_relabelled=True));raise
'''
 p=D/'review_slope135_actual.py';assert not p.exists();compile(text,str(p),'exec');p.write_bytes(text.encode())
 save('SLOPE135_READERS_PREPARED.json',dict(epoch=time.time(),collector_SHA=H(collector.encode()),reviewer_SHA=H(text.encode()),no_eval_replay=True,actual_fullsave_PASSED_and_complete_errorfree_only=True,baseline134_same_geometry_initial_and115_129_skill_contracts=True,original_tolerances_unchanged=True))
if __name__=='__main__':main()
