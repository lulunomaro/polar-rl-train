"""Prepare same descriptive analysis for future new89aca own telemetry; SOURCE_ONLY."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;D=R/'analyze_postadapt_w35_own_telemetry.py';assert not D.exists();s=(R/'analyze_w35_own32s_telemetry.py').read_text(encoding='utf-8')
a="""assert str(B)=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800'
EXPECTED_BYTES=46099917;EXPECTED_SHA='7e6f3353b28010de6ba6f261fc778716dc763722b715eca361ac9271f7660608'
assert rawpath.stat().st_size==EXPECTED_BYTES
hb=schema.read_bytes();assert len(hb)==13731 and hashlib.sha256(hb).hexdigest()=='4c85e294562a42ac896d78cb3834b59c801c98af7f5f18defadac1a380daff31'
"""
b="""plan=json.loads(Path(sys.argv[2]).read_bytes());assert str(B)==plan['job'] and plan['source_model_SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f'
EXPECTED_BYTES=plan['producer']['bytes'];EXPECTED_SHA=plan['producer']['SHA']
assert plan['actual_eval_passed_execution'] and plan['actual_eval_complete32s'] and plan['actual_parent_all_children_waited_released']
assert not plan['producer']['retention_limited'] and plan['producer']['dropped_rows']==0 and plan['producer']['rows']==sum(plan['producer']['rows_by_schema'])
assert str(rawpath)==plan['producer']['path'] and rawpath.stat().st_size==EXPECTED_BYTES
hb=schema.read_bytes();assert str(schema)==plan['producer']['schema_path'] and len(hb)==plan['producer']['schema_bytes'] and hashlib.sha256(hb).hexdigest()==plan['producer']['schema_SHA']
"""
assert s.count(a)==1;s=s.replace(a,b).replace("r['source_SHA']=='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b'","r['source_SHA']==plan['source_model_SHA']").replace('rowcount==146381',"rowcount==plan['producer']['rows']").replace('MOD4V1_W35_OWN32S_NEW_TELEMETRY_CPU_ONEPASS_V1','MOD4V1_W35_POSTADAPT_OWN32S_NEW_TELEMETRY_CPU_ONEPASS_V1').replace("p=B/'CPU_OWN32S_TELEMETRY_ANALYSIS_V1.json'","p=B/'CPU_POSTADAPT_OWN32S_TELEMETRY_ANALYSIS_V1.json'")
ast.parse(s);D.write_text(s,encoding='utf-8');report={'kind':'POSTADAPT_NEW_OWN_TELEMETRY_ANALYZER_SOURCE_ONLY','SHA':hashlib.sha256(D.read_bytes()).hexdigest(),'status':'CPU_AST_ONLY_NO_RAW_READ','plan_required':'Actualcomplete32s parentexit scope + exact producer bytes/SHA/rowcount/schemaSHA; source89aca only','no_new_graduation_rate':True,'original_descriptive_stats_retained':True,'raw_opens':0,'PT_opens':0,'SDK_or_budget_access':False};p=R/'reports/POSTADAPT_CPU_ANALYZER_SOURCE_ONLY.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
