from pathlib import Path
import os,time,json,traceback
F=Path(__file__).resolve().parent;R=F/'reports'
from deploy_recovered_three_finals_new_native_then_original_owner_once import a,ROOTS
CODE=r'''
from pathlib import Path
import sys,json,time,hashlib,subprocess,psutil,shutil,os
B=Path(sys.argv[1]);A=Path(sys.argv[2]);source_SHA=sys.argv[3];gpu=sys.argv[4];v=json.loads((A/'job0/production/FINAL.json').read_bytes());p=Path(v['final']['path']);lines=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],timeout=20).decode();line=next(x for x in lines.splitlines() if gpu in x);disk=shutil.disk_usage('/mnt/mod4_linux_durable_20261013');ram=psutil.virtual_memory().available;df=subprocess.check_output(['df','-PT'],timeout=20).decode();print(json.dumps(dict(epoch=time.time(),new_root_exists=B.exists(),previous_NODE_EXIT=json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes()),previous_FINAL_passed=v['passed'],actual_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),expected_source_SHA=source_SHA,GPU_line=line,GPU_free_over7000=int(line.split(',')[-1])>7000,RAM_available=ram,RAM_over8GiB=ram>8*1024**3,owned_durable_free=disk.free,durable_over25GiB=disk.free>25*1024**3,df_PT_readonly=df,source_own_uid=os.getuid(),no_GPU_or_new_directory_or_file_or_budget_mutation=True)))
'''
def main():
 prep=json.loads((R/'RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());s=prep['specs']['h1'];conn=None
 try:conn=a.t.connect();v=a.code(conn,a.t.PY,CODE,ROOTS['h1'],s['previous_runtime_root'],s['source_SHA'],s['GPU_UUID'])
 finally:a.t.close(conn)
 p=R/'SOURCE_PRECREATE_COMBINED_RESOURCE_ASSERTION_INDEPENDENT_READONLY_DIAGNOSIS_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE_RESOURCE_DIAGNOSTIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_mutation=True),f,indent=2)
  raise
