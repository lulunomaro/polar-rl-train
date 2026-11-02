"""Strict MinGW32 builds; snapshots/logs every attempt, no old source writes."""
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys
HERE=Path(__file__).resolve().parent;SEALED=HERE.parent/'ACTIVE_BOX_QP_V3';GCC=Path(r'C:\MinGW\bin\gcc.exe')
FLAGS=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=int(sys.argv[1]) if len(sys.argv)==2 else 1;tag=f'{attempt:02d}';revision=HERE/'revisions'/('build_attempt_'+tag);revision.mkdir(parents=True,exist_ok=False)
 files=['build_io.py','active_qp_host.c','aq_clock.c','aq_clock.h','aq_io_build.h','clock_selftest.c','clock_vectors.h','sdk_fault_fixture.c','PROTOCOL_SCHEMA.json','SCOPE.md']
 for n in files:shutil.copy2(HERE/n,revision/n)
 freeze=json.loads((HERE/'SOURCE_FREEZE.json').read_text());assert sha(SEALED/'active_box_qp.c')==freeze['core']['sha256'];assert sha(SEALED/'active_box_qp.h')==freeze['header']['sha256']
 if attempt>1:
  previous=HERE/'revisions'/f'build_attempt_{attempt-1:02d}'
  for n in ['active_qp_host.exe','active_qp_clock_harness.exe','clock_selftest.exe','sdk_fault_fixture.exe']:
   if (HERE/n).exists() and not (previous/n).exists():shutil.copy2(HERE/n,previous/n)
 common=[str(GCC),*FLAGS,'-I','../ACTIVE_BOX_QP_V3'];commands=[]
 jobs=[('compiler_version',[str(GCC),'--version']),('production',common+['active_qp_host.c','aq_clock.c','../ACTIVE_BOX_QP_V3/active_box_qp.c','-lm','-o','active_qp_host.exe']),('test_clock_only',common+['-DAQ_TEST_CLOCK','active_qp_host.c','aq_clock.c','../ACTIVE_BOX_QP_V3/active_box_qp.c','-lm','-o','active_qp_clock_harness.exe']),('clock_selftest',common+['clock_selftest.c','aq_clock.c','-lm','-o','clock_selftest.exe']),('SDK_lifecycle_fixture_not_solver',common+['sdk_fault_fixture.c','-o','sdk_fault_fixture.exe'])]
 for phase,argv in jobs:
  path=HERE/(phase+'_'+tag+'.log')
  if path.exists():raise FileExistsError(path)
  with path.open('w',encoding='utf-8') as out:
   out.write(json.dumps(argv)+'\n');out.flush();result=subprocess.run(argv,cwd=HERE,stdout=out,stderr=subprocess.STDOUT);out.write(f'\nexit_code={result.returncode}\n')
  artifact_ok=('-o' not in argv) or (HERE/argv[argv.index('-o')+1]).is_file()
  commands.append({'phase':phase,'arguments':argv,'exit_code':result.returncode,'artifact_exists':artifact_ok,'log':str(path)})
  if result.returncode or not artifact_ok:break
 objects=[]
 for n in ['active_qp_host.exe','active_qp_clock_harness.exe','clock_selftest.exe','sdk_fault_fixture.exe']:
  p=HERE/n
  if p.exists():
   data=p.read_bytes();offset=struct.unpack_from('<I',data,0x3c)[0];assert data[:2]==b'MZ' and data[offset:offset+4]==b'PE\0\0';machine=struct.unpack_from('<H',data,offset+4)[0];magic=struct.unpack_from('<H',data,offset+24)[0];assert machine==0x14c and magic==0x10b;objects.append({'path':str(p),'bytes':len(data),'sha256':sha(p),'machine':machine,'optional_magic':magic,'format':'PE32 x86'})
 receipt={'attempt':attempt,'commands':commands,'binaries':objects,'compiler':str(GCC),'flags':FLAGS,'sealed_core':freeze['core'],'sealed_header':freeze['header'],'scope':'host stdio/QPC only; test harness/fixture separately named, no board/runtime'}
 (HERE/('BUILD_RECEIPT_'+tag+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'attempt':attempt,'commands':len(commands),'all_exit0':all(r['exit_code']==0 for r in commands),'PE32_binaries':len(objects)}));return 0 if len(commands)==len(jobs) and len(objects)==4 and all(r['exit_code']==0 and r['artifact_exists'] for r in commands) else 1
if __name__=='__main__':sys.exit(main())
