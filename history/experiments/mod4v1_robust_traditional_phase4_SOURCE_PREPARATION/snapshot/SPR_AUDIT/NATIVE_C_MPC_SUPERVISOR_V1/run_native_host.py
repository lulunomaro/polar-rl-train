"""Run exactly the new host test and C++ binaries, preserving all raw output."""
from pathlib import Path
import subprocess,hashlib,json
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=json.loads((HERE/'HOST_BUILD_01.json').read_text());assert receipt['success'];records=[]
 for n,log in [('nm1_host_tests.exe','host_run_01.log'),('nm1_cpp_smoke.exe','cpp_run_01.log')]:
  p=HERE/n;old=next(x for x in receipt['commands']if x['artifact']==str(p));assert p.is_file()and sha(p)==old['sha256'];out=HERE/log;assert not out.exists()
  with out.open('wb')as f:r=subprocess.run([str(p)],cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
  rows=dict(executable=str(p),sha256=sha(p),exit_code=r.returncode,log=str(out),bytes=out.stat().st_size);records.append(rows);(HERE/'HOST_RUN_01.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows))
  if r.returncode:raise RuntimeError('NEW_NATIVE_TEST_FAILURE; preserve output and inspect')
if __name__=='__main__':main()
