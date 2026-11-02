"""Read-only provenance and local-output hash/link validation. No source exec."""
from pathlib import Path
import hashlib,json,re,traceback
HERE=Path(__file__).resolve().parent
NAMES=['ct_kinematics.h','ct_kinematics.c','ctk_selftest.c','generate_vectors.py','index_core.py',
 'selected_inputs.json','python_vectors.json','ctk_fixtures.h','provenance.json','vector_generation_01.log',
 'build_attempt_01.log','build_attempt_02.log','selftest_attempt_01.log','selftest_attempt_02.log',
 'toolchain_version.log','revisions/ctk_selftest_attempt_01.c','README.md','ERROR_REPORT.md','ctk_selftest_host.exe']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_json(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def dump(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def manifest():
 names=['ct_kinematics.h','ct_kinematics.c','ctk_selftest.c','README.md','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in names]})

def main():
 provenance=read_json(HERE/'provenance.json')
 for item in provenance['sources']:
  p=Path(item['path']);assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
 previous=[]
 for file,key in [(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables')]:
  old=read_json(file)
  for item in old[key]:
   p=file.parent/item['path'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
   previous.append({'path':str(p),'unchanged':True})
 text=(HERE/'selftest_attempt_02.log').read_text(encoding='utf-8-sig')
 line=next(s for s in text.splitlines() if s.startswith('CTK_SELFTEST '))
 numbers=dict(re.findall(r'([A-Za-z_]+)=([0-9.eE+-]+)',line))
 assert int(numbers['failures'])==0 and 'FLT_EVAL_METHOD=0' in text and 'exit_code=0' in text
 assert 'PURE_4PI_SPIN forward_cancellation=PASS' in text
 scans=[{'epsilon_rad':float(a),'max_J_absolute_error':float(b),'max_forward_error_m_s':float(c)} for a,b,c in re.findall(r'EPS_SWEEP epsilon=([0-9.eE+-]+) max_J_absolute_error=([0-9.eE+-]+) max_forward_absolute_error=([0-9.eE+-]+)',text)]
 for n in ['build_attempt_01.log','build_attempt_02.log','selftest_attempt_01.log']:
  assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig')
 records=[]
 for n in NAMES:
  p=HERE/n;assert p.is_file();r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix!='.exe':
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count
   if count:r['citation']=f'{n}#L1-L{count}'
  r['role']='host_algebra_binary_not_board_firmware' if p.suffix=='.exe' else ('historical_test_source' if n.startswith('revisions/') else 'source_input_fixture_log_or_document')
  records.append(r)
 core=(HERE/'ct_kinematics.c').read_text(encoding='utf-8')
 assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(',core)
 assert not re.search(r'\bdouble\b',core)
 api=[]
 for n in ['ct_kinematics.h','ct_kinematics.c']:
  for no,s in enumerate((HERE/n).read_text(encoding='utf-8').splitlines(),1):
   m=re.match(r'ctk_status\s+(ctk_\w+)\s*\(',s)
   if m:api.append({'symbol':m[1],'path':n,'line':no,'citation':f'{n}#L{no}'})
 index={'name':'portable_core_v2_kinematics','status':'HOST_C99_BINARY32_MATH_PASS_NOT_CURRENT_DYNAMIC_ESTIMATOR',
  'write_scope':str(HERE),'source_provenance':provenance,'old_deliverables_unchanged':previous,
  'files':records,'entry_points':api,
  'compiler':{'path':r'C:\MinGW\bin\gcc.exe','version':'MinGW.org GCC-6.3.0-1 6.3.0','target':'mingw32',
   'command':'gcc -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse ct_kinematics.c ctk_selftest.c -lm -o ctk_selftest_host.exe',
   'SSE2_is_host_only_not_ARM':True},
  'tests':{'assertion_checks':int(numbers['checks']),'failures':int(numbers['failures']),
   'not_independent_robot_episodes':True,'metrics':{k:float(v) for k,v in numbers.items() if k not in ['checks','failures']},
   'epsilon_sweep':scans,'fixture_counts':provenance['fixture_counts'],
   'pure_4pi_spin':'both sides cancel translation for +/-4*pi with internally consistent selected radius',
   'rigid_rotation_identity':'hip=crank=h => wheel=R(h)*neutral_W and knee_relative=0',
   'radius_mismatch':'using geometric radius on nominal-radius spin fixture gives -/+0.0527906418 m/s; algebra only',
   'float_storage_bytes':4,'float_mantissa_bits':24,'FLT_EVAL_METHOD':0},
  'parameter_scope':{'pins':'specified historical neutral_skeleton_xz_m; not physical calibration',
   'track_m':.4376,'radius':'mandatory external input; nominal and USD circumscribed radius kept separate, neither measured',
   'gain':'nominal_gain_v1 K/tau/q arrays only; root/frozen hashes equal',
   'actuator_rows':'opaque gain-file order; no silent mapping into v1 HAL wheel-first order',
   'lqr_equation':'tau_ff - K*(state-reference), explicit clipping, no yaw wrap'},
  'scope_exclusions':['new dynamic specific-force estimator','final control-architecture selection','ARM/BSP/CAN/board I/O','SSH or flashing','MuJoCo/plant simulation','RL/training','parent file/Git modifications','new subagents'],
  'error_record':'ERROR_REPORT.md; no nonzero build/test exit; original mixed-unit metric log retained and corrected in final test labels',
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST and index stdout log excluded to avoid recursion; MANIFEST hashes primary deliverables'}
 dump('INDEX.json',index)
 validation={'source_hashes_unchanged':len(provenance['sources']),'old_audit_and_v1_primary_files_unchanged':len(previous),
             'files_indexed':len(records),'assertions_passed':int(numbers['checks']),'assertions_failed':0,'ARM_or_board_tested':False}
 dump('VALIDATION.json',validation);manifest()
 links=0
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
