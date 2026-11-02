from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800';remote=job+'/reader_w35_own32s_cpu_v1.py';c=connect72();s=c.open_sftp();record={'purpose':'NEW_OWN32S_BOUNDED_CPU_READER_ONEPASS','remote_job':job,'expected_raw_bytes':46099917,'PT_reads':0,'SDK_or_canonical_access':False}
try:
 try:s.stat(remote)
 except FileNotFoundError:pass
 else:raise RuntimeError('CPU reader already staged: preserve once/no automatic rerun')
 s.put(str(R/'analyze_w35_own32s_telemetry.py'),remote)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(remote)+' '+shlex.quote(job),timeout=180);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();record.update(returncode=rc,stderr=err)
 if rc==0:record['result']=json.loads(text)
 else:record['original_stdout']=text
finally:s.close();c.close()
p=R/'reports'/('W35_own32s_cpu_analysis_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p)
if 'result'in record:
 q=record['result'];print(json.dumps({k:v for k,v in q.items() if k!='route_samples'},ensure_ascii=False,indent=2))
else:print(json.dumps(record,ensure_ascii=False,indent=2))
assert record['returncode']==0
