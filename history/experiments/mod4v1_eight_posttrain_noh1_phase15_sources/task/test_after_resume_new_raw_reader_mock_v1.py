"""Syntheticone-row telemetry only: modelSHA dynamic/lineagebinding andwrongrowrejection. No actualraw/PT/SDK."""
from pathlib import Path
import json,hashlib,sys,runpy,contextlib,io,ast
R=Path(__file__).resolve().parent;D=R/'mock_after_resume_new_raw_reader_v1';assert not D.exists();D.mkdir();reader=R/'analyze_after_resume89aca_w35_own_telemetry_v1.py';model='a'*64;parent='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f';rows=[]
for name,rowmodel,par,expected in [('matching_dynamic_model',model,parent,True),('wrong_row_model','b'*64,parent,False),('wrong_parent_lineage',model,'c'*64,False)]:
 B=D/name;O=B/'actual_latest32';O.mkdir(parents=True);raw=O/'RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl';schema=O/'RM70_SAME_UID_COMMAND_AND_ROUTE_SCHEMAS227.json';raw.write_bytes(b'[0,[]]\n');header={'format':'mod4.227.lossless_fieldset_positional_jsonl.v1','schemas':[{'schema_id':0,'fields':['record_type','source_SHA'],'constants':{'record_type':'SYNTHETIC_MOCK_METADATA_ONLY_NOT_RM70','source_SHA':rowmodel},'positional_fields':[]}]};schema.write_text(json.dumps(header),encoding='utf-8');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();plan={'job':str(B),'source_model_SHA':model,'source_parent_SHA':par,'actual_saved_source_producer_metadata':{'SHA':model,'source_SHA':par},'producer':{'bytes':raw.stat().st_size,'SHA':h(raw),'rows':1,'rows_by_schema':[1],'path':str(raw),'schema_path':str(schema),'schema_bytes':schema.stat().st_size,'schema_SHA':h(schema),'retention_limited':False,'dropped_rows':0},'actual_eval_passed_execution':True,'actual_eval_complete32s':True,'actual_parent_all_children_waited_released':True};p=B/'MOCK_PLAN.json';p.write_text(json.dumps(plan),encoding='utf-8');old=sys.argv;sys.argv=[str(reader),str(B),str(p)];okay=False;err=None
 try:
  with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(reader),run_name='__main__')
  okay=True
 except AssertionError:err='EXPECTED_ASSERTION_FOR_WRONG_LINEAGE_OR_ROW'
 finally:sys.argv=old
 assert okay==expected;rows.append({'case':name,'passed':okay,'expected':expected,'error':err})
v={'kind':'SYNTHETIC_MOCK_ONLY_DYNAMIC_NEW_MODEL_SHA_AND_LINEAGE_BINDING','rows':rows,'actual_telemetry_or_model_reads':0,'actual_SDK_or_budget_actions':0};out=R/'reports/W35_AFTER_RESUME_NEW_RAW_READER_MOCK_V1.json';assert not out.exists();out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
