"""ROOT run after full32 completed+original parent scope released. One own-new-raw read only."""
from pathlib import Path
import json,shlex,datetime,hashlib
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_after_resume89aca_eval_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];c=connect72();s=c.open_sftp();stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');receipt={'kind':'ROOT_AFTER_RESUME89ACA_NEW_OWN32S_CPU_READER_ONEPASS','job':job,'PT_opens':0,'SDK_or_canonical_access':False}
try:
 def read_json(rel):
  with s.open(job+'/'+rel,'rb')as f:return json.loads(f.read())
 end=read_json('PARENT_EXIT_SCOPE.json');final=read_json('FINAL.json');facts=final['rows']['ACTUAL227_CLOSED_RM70_SKILL_FACTS.json'];producer=facts['facts']['producer']
 assert end['all_own_children_waited'] and end['owned_private_validation_locks_released'] and end['error']is None and final['passed_execution'] and final['bounded32s_complete'] and final['returncode']==0
 source=d['new_source_model'];assert source['source_SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f' and source['saved_iteration']==32561+source['actual_new_PPO_updates'] and source['Adam_min']==source['Adam_max']==652860+20*source['actual_new_PPO_updates']
 assert facts['source_SHA']==d['new_source_model']['SHA'] and facts['controls']==1600 and facts['bounded_window_complete'] and facts['optimizer_steps']==0 and facts['core_and_17Adam_unchanged'] and final['optimizer_updates']==0
 assert producer['path']==job+'/actual_latest32/RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl' and not producer['retention_limited'] and producer['dropped_rows']==0 and producer['rows']==sum(producer['rows_by_schema'])
 plan={'job':job,'source_model_SHA':facts['source_SHA'],'source_parent_SHA':d['new_source_model']['source_SHA'],'actual_saved_source_producer_metadata':d['new_source_model'],'producer':producer,'actual_eval_passed_execution':True,'actual_eval_complete32s':True,'actual_parent_all_children_waited_released':True,'raw_read_purpose':'One complete declared actualnewcheckpointafter89acaresume owncase telemetry read; old89aca/baseline/raw/PT nottouched'}
 for name,v in [('CPU_OWN_RAW_PURPOSE_CONSUMED.json',{'bytes':producer['bytes'],'SHA':producer['SHA'],'schema_bytes':producer['schema_bytes'],'schema_SHA':producer['schema_SHA'],'raw_opens_permitted':1,'schema_opens_permitted':1,'PT_opens_permitted':0}),('CPU_OWN_RAW_PLAN.json',plan)]:
  with s.open(job+'/'+name,'wx')as f:f.write(json.dumps(v,indent=2))
 p=R/'analyze_after_resume89aca_w35_own_telemetry_v1.py';remote=job+'/reader_after_resume89aca_own_raw_cpu_v1.py'
 with s.open(remote,'wx')as f:f.write(p.read_text(encoding='utf-8'))
 receipt['reader_SHA']=hashlib.sha256(p.read_bytes()).hexdigest();receipt['declared']=plan
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(remote)+' '+shlex.quote(job)+' '+shlex.quote(job+'/CPU_OWN_RAW_PLAN.json');i,o,e=c.exec_command(command,timeout=180);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();receipt.update(returncode=rc,stderr=err)
 if rc==0:receipt['analysis']=json.loads(text);receipt['status']='ACTUAL_OWN_BYTES_SHA_ROWS_VERIFIED'
 else:receipt.update(status='FAILED_PRESERVED_NO_AUTOMATIC_REPLAY',stdout=text)
finally:s.close();c.close()
p=R/'reports'/('W35_after_resume89aca_own_raw_CPU_'+stamp+'.json');p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);brief={k:v for k,v in receipt.items()if k not in('analysis','declared')}
if 'analysis'in receipt:brief['analysis']={k:v for k,v in receipt['analysis'].items()if k not in('route_samples','distributions')}
print(json.dumps(brief,ensure_ascii=False,indent=2))
