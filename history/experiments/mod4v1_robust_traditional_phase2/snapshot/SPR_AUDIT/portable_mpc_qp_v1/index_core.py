"""Hash/link validation only; never executes parent or sealed source/test code."""
from pathlib import Path
import hashlib,json,re,traceback
HERE=Path(__file__).resolve().parent
NAMES=['boxqp.h','boxqp.c','bqp_selftest.c','cpp_smoke.cpp','generate_vectors.py','index_core.py',
 'python_vectors.json','bqp_fixtures.h','provenance.json','vector_generation_01.log',
 'build_attempt_01.log','selftest_attempt_01.log','cpp_toolchain_probe.log','toolchain_version.log',
 'c_object_build_01.log','boxqp_host.o','cpp_link_01.log','cpp_smoke_01.log','cpp_smoke_host.exe',
 'bqp_selftest_host.exe','README.md','ERROR_REPORT.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def manifest():
 names=['boxqp.h','boxqp.c','bqp_selftest.c','README.md','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in names]})
def main():
 old=[]
 for p,key in [(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables'),(HERE.parent/'portable_core_v2_kinematics/MANIFEST.json','deliverables')]:
  for item in load(p)[key]:
   target=p.parent/item['path'];assert target.stat().st_size==item['bytes'] and sha(target)==item['sha256']
   old.append({'path':str(target),'sha256':item['sha256'],'unchanged':True})
 text=(HERE/'selftest_attempt_01.log').read_text(encoding='utf-8-sig')
 line=next(x for x in text.splitlines() if x.startswith('BQP_SELFTEST '))
 metrics=dict(re.findall(r'([A-Za-z_]+)=([0-9.eE+-]+)',line));assert int(metrics['failures'])==0
 assert 'FLT_EVAL_METHOD=0' in text and 'exit_code=0' in text
 for n in ['build_attempt_01.log','c_object_build_01.log','cpp_link_01.log','cpp_smoke_01.log']:
  assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig')
 assert 'pass=1' in (HERE/'cpp_smoke_01.log').read_text(encoding='utf-8-sig')
 provenance=load(HERE/'provenance.json');assert sha(HERE/'generate_vectors.py')==provenance['sha256']
 files=[]
 for n in NAMES:
  p=HERE/n;assert p.is_file();r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix not in ('.exe','.o'):
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count
   if count:r['citation']=f'{n}#L1-L{count}'
  r['role']='host_artifact_not_firmware' if p.suffix in ('.exe','.o') else 'source_fixture_log_or_document';files.append(r)
 core=(HERE/'boxqp.c').read_text(encoding='utf-8')
 assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(',core)
 assert not re.search(r'\bdouble\b',core)
 api=[]
 for n in ['boxqp.h','boxqp.c']:
  for no,line in enumerate((HERE/n).read_text(encoding='utf-8').splitlines(),1):
   m=re.match(r'(?:bqp_status|bqp_problem)\s+(bqp_\w+)\s*\(',line)
   if m:api.append({'symbol':m[1],'path':n,'line':no,'citation':f'{n}#L{no}'})
 index={'name':'portable_mpc_qp_v1','status':'SEALED_NUMERICAL_HOST_TESTED_NOT_ROBOT_MPC','write_scope':str(HERE),
  'files':files,'entry_points':api,'fixture_provenance':provenance,'sealed_old_primary_files_unchanged':old,
  'QP':{'maximum_n':16,'objective':'.5 z^T H z + f^T z','constraints':'finite componentwise box only',
   'symmetric':'exact float-value equality','SPD':'f32 Cholesky, positive pivots, no hidden regularization',
   'algorithm':'cyclic exact scalar minimization and projection; fresh full gradient/cost each sweep',
   'KKT':'tangent-projected gradient infinity norm, absolute gradient-unit tolerance',
   'workspace_host_bytes':2448,'heap':False,'VLA':False},
  'tests':{'assertions':int(metrics['checks']),'failures':0,'progress_events':int(metrics['progress_events']),
   'max_solution_error':float(metrics['max_solution_error']),'max_cost_error':float(metrics['max_cost_error']),
   'max_double_recomputed_KKT':float(metrics['max_double_KKT']),
   'float_storage_bytes':4,'mantissa_bits':24,'FLT_EVAL_METHOD':0,
   'tolerance':'per fixture: 2e-5 for 1D/2D; 2e-4 for n15/n16',
   'cpp_extern_C_separate_object_link_and_smoke_passed':True,'not_robot_episodes':True},
  'toolchain':{'gcc':r'C:\MinGW\bin\gcc.exe','gpp':r'C:\MinGW\bin\g++.exe','version':'6.3.0 MinGW.org GCC-6.3.0-1','target':'mingw32',
   'C_flags':'-std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse',
   'host_only_SSE2_not_ARM':True},
  'deadline_contract':'sampled at sweep checkpoints and after progress; no hard preemption; final returned status authoritative; rollback discards candidate',
  'not_implemented':['state/general linear constraints','coupled power constraints','robot Hessian/model','closed-loop MPC','LQR fallback/control application','electrical/thermal model','ARM WCET/BSP/board'],
  'scope_exclusions':['parent/sealed source edits','old unit replay for naming','simulation/plant','CAN/board/SSH/flashing','training/RL','Git','new packages/subagents'],
  'error_report':'ERROR_REPORT.md; all build/test attempts exit0, no source correction was needed',
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST and index stdout log excluded to avoid recursion; primary hashes in MANIFEST'}
 dump('INDEX.json',index)
 validation={'old_primary_hashes_unchanged':len(old),'files_indexed':len(files),'assertions_passed':int(metrics['checks']),
             'assertions_failed':0,'cpp_extern_C_link_pass':True,'ARM_or_robot_tested':False}
 dump('VALIDATION.json',validation);manifest();links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   filename,_,frag=target.partition('#');p=(HERE/filename).resolve();assert p.is_file(),target
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation);manifest()
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
