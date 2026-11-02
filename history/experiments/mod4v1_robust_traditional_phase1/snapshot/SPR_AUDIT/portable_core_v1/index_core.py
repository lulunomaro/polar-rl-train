"""Metadata/hashes/line-link validation only; no source import or code execution."""
from pathlib import Path
import hashlib,json,re,traceback
ROOT=Path(__file__).resolve().parent
NAMES=['ct_core.h','ct_core.c','ct_selftest.c','generate_vectors.py','index_core.py',
 'python_vectors.json','ct_test_vectors.h','provenance.json','vector_generation_01.log',
 'build_attempt_01.log','build_attempt_02.log','build_attempt_03.log','build_attempt_04.log',
 'selftest_attempt_01.log','selftest_attempt_02.log','selftest_attempt_03.log',
 'toolchain_target.log','ct_selftest_host.exe','README.md','ERROR_REPORT.md',
 'revisions/ct_core_attempt_01.c','revisions/ct_core_attempt_02.c','revisions/ct_core_attempt_03.c',
 'revisions/ct_core_attempt_03.h','revisions/ct_selftest_attempt_01.c','revisions/ct_selftest_attempt_02.c']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 provenance=json.loads((ROOT/'provenance.json').read_text(encoding='utf-8'))
 frozen=Path(provenance['source']);hal=Path(provenance['hal_header'])
 assert frozen.stat().st_size==provenance['bytes'] and sha(frozen)==provenance['sha256']
 assert sha(hal)==provenance['hal_sha256']
 old=json.loads((ROOT.parent/'deliverable_manifest.json').read_text(encoding='utf-8'))
 old_checked=[]
 for item in old['files']:
  p=ROOT.parent/item['path'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
  old_checked.append(item['path'])
 final_log=(ROOT/'selftest_attempt_03.log').read_text(encoding='utf-8-sig')
 match=re.search(r'checks=(\d+) failures=(\d+) maximum_numeric_absolute_error=([0-9.eE+-]+)',final_log)
 assert match and int(match[2])==0 and 'FLT_EVAL_METHOD=0' in final_log and 'exit_code=0' in final_log
 for name in ['build_attempt_02.log','build_attempt_03.log','build_attempt_04.log']:
  assert 'exit_code=0' in (ROOT/name).read_text(encoding='utf-8-sig')
 assert 'exit_code=1' in (ROOT/'build_attempt_01.log').read_text(encoding='utf-8-sig')
 files=[]
 for name in NAMES:
  path=ROOT/name;assert path.is_file();record={'path':name,'bytes':path.stat().st_size,'sha256':sha(path)}
  if path.suffix!='.exe':
   lines=path.read_text(encoding='utf-8-sig').splitlines();record['line_count']=len(lines)
   if lines:record['citation']=f'{name}#L1-L{len(lines)}'
  record['role']='historical_source' if name.startswith('revisions/') else ('host_test_binary_not_firmware' if name.endswith('.exe') else 'source_fixture_log_or_document')
  files.append(record)
 core=(ROOT/'ct_core.c').read_text(encoding='utf-8')
 assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(',core)
 assert not re.search(r'\bdouble\b',core)
 assert not re.search(r'#include\s*[<\"](mujoco|torch|cuda|stm32)',core,re.I)
 api=[]
 for name in ['ct_core.h','ct_core.c','ct_selftest.c']:
  for line_no,line in enumerate((ROOT/name).read_text(encoding='utf-8').splitlines(),1):
   m=re.match(r'(?:ct_status|void|int)\s+(ct_\w+|main)\s*\(',line)
   if m:api.append({'symbol':m[1],'path':name,'line':line_no,'citation':f'{name}#L{line_no}'})
 index={'version':'portable_core_v1','status':'HOST_C99_BINARY32_ALGEBRA_PASS_NOT_ARM_OR_HARDWARE',
 'provenance':provenance,'old_audit_manifest_entries_unchanged':old_checked,
 'write_scope':str(ROOT),'files':files,'entry_points':api,
 'tests':{'assertion_checks':int(match[1]),'failed':int(match[2]),'maximum_scalar_absolute_error':float(match[3]),
          'float_storage_bytes':4,'mantissa_bits':24,'FLT_EVAL_METHOD':0,'raw_final_log':'selftest_attempt_03.log',
          'fixture_counts':provenance['vector_counts'],
          'spin_fixture':'4*pi rad/s 2 seconds forward + 2 seconds reverse, dt=.001s; math only',
          'not_independent_robot_episodes':True},
 'compiler':{'path':'C:/MinGW/bin/gcc.exe','version':'MinGW GCC 6.3.0','target':'mingw32',
             'command':'gcc -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse ct_core.c ct_selftest.c -lm -o ct_selftest_host.exe'},
 'error_history':{'failed_build':'build_attempt_01.log','reason':'9 misleading-indentation diagnostics promoted to errors; corrected before retry',
                 'original_source':'revisions/ct_core_attempt_01.c','report':'ERROR_REPORT.md','passing_builds':['build_attempt_02.log','build_attempt_03.log','build_attempt_04.log']},
 'static_checks':{'no_dynamic_allocation_calls_in_core':True,'no_double_type_in_core':True,'no_hardware_or_simulation_include':True},
 'not_implemented':['CAD linkage frontend','LQR/MPC control law','full behavior FSM','complete electrical/thermal power model','DM3519 protocol codec','board BSP/RTOS','physical output gate implementation'],
 'never_performed':['MuJoCo/plant simulation','RL/training','ARM firmware build','board I/O or flashing','SSH','Git modification','parent running-task operation'],
 'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST excluded from files to avoid recursive hashes; MANIFEST holds primary deliverable hashes.'}
 dump('INDEX.json',index)
 link_count=0
 for name in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(ROOT/name).read_text(encoding='utf-8')):
   filename,_,fragment=target.partition('#');p=(ROOT/filename).resolve();assert p.is_file(),target
   if fragment:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   link_count+=1
 validation={'source_and_hal_unchanged':True,'old_audit_files_unchanged':len(old_checked),'file_hashes_indexed':len(files),
             'local_markdown_links_checked':link_count,'assertions_passed':int(match[1]),'assertions_failed':0,'target_board_tested':False}
 dump('VALIDATION.json',validation)
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)} for n in ['ct_core.h','ct_core.c','ct_selftest.c','README.md','INDEX.json','VALIDATION.json','ERROR_REPORT.md']]})
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
