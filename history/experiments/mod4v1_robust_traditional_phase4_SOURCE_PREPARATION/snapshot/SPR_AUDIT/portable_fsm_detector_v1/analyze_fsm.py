"""Read-only validation of existing new-port runs and new ARM objects. No rerun."""
from pathlib import Path
import json,hashlib,math,re,struct,csv,traceback
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):
 p=HERE/n;assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def undef(raw):
 off=struct.unpack_from('<I',raw,32)[0];size,num=struct.unpack_from('<HH',raw,46);sections=[struct.unpack_from('<IIIIIIIIII',raw,off+i*size)for i in range(num)];names=[]
 for s in sections:
  if s[1]!=2:continue
  st=sections[s[6]];strings=raw[st[4]:st[4]+st[5]]
  for pos in range(s[4],s[4]+s[5],s[9]):
   name,_,_,_,_,index=struct.unpack_from('<IIIBBH',raw,pos)
   if index==0 and name:names.append(strings[name:strings.index(b'\0',name)].decode('utf-8'))
 return sorted(set(names))
def main():
 registry=load('REASON_REGISTRY.json')['ids'];ref=[json.loads(s)for s in (HERE/'REFERENCE_FRAMES.jsonl').read_text().splitlines()];runs={};native_counts={}
 for attempt in [1,2,3]:
  text=(HERE/f'host_run_{attempt:02d}.log').read_text(encoding='utf-8-sig');rows=[json.loads(s)for s in text.splitlines()if s.startswith('{')];summary=rows[-1];assert summary['kind']=='summary'and summary['reference_rows']==1042 and summary['replay_failures']==0 and summary['native_failures']==0;assert 'exit_code=0'in text;native=re.search(r'FD1_NATIVE checks=(\d+) failures=(\d+)',text);native_counts[str(attempt)]={'checks':int(native[1]),'failures':int(native[2])};runs[str(attempt)]=summary
 actual=[r for r in rows if r['kind']=='frame'];assert len(actual)==len(ref)==1042
 errors=[];cases={};maxerr=0.;bit_equal=True
 for i,(r,a)in enumerate(zip(ref,actual)):
  o=r['expected'];p=o['contact'];case=cases.setdefault(r['scenario'],{'scenario':r['scenario'],'rows':0,'mismatches':0,'maximum_numeric_absolute':0.});case['rows']+=1
  want={'row':i,'context':r['context'],'mode':o['mode'],'profile':o['profile'],'phase':o['phase'],'inhibit':int(o['hard_inhibit']),'q_valid':int(o['expected_q4']is not None),'support':p['support'],'wheel':p['wheel_state2'],'source':{'unobserved':0,'external_motor_force_proxy':1,'declared_COM_freefall_model_only':2}[p['source']],'com_known':int(p['com_freefall_like']is not None),'com_like':int(bool(p['com_freefall_like'])),'no_slip':[int(x)for x in o['wheel_no_slip_allowed2']],'jump':int(o['jump_accepted']),'recovery':int(o['recovery_accepted']),'reasons':[registry[x]for x in o['reasons']],'faults':[registry[x]for x in o['latched_faults']],'contact_reasons':[registry[x]for x in p['reasons']],'status':2 if o['mode']==10 else 1 if o['mode']==3 else 0}
  for field,value in want.items():
   if a[field]!=value:errors.append({'row':i,'field':field,'got':a[field],'expected':value});case['mismatches']+=1
  numeric=[('fraction',o['phase_fraction']),('entered',o['state_entered_s']),('confidence',p['confidence'])]+[(f'q4.{k}',v)for k,v in enumerate(o['expected_q4']or[0.,0.,0.,0.])]
  for field,value in numeric:
   got=a['q4'][int(field[3:])]if field.startswith('q4.')else a[field];err=abs(got-value);maxerr=max(maxerr,err);case['maximum_numeric_absolute']=max(case['maximum_numeric_absolute'],err);bit_equal &=struct.pack('<d',float(got))==struct.pack('<d',float(value))
   if not math.isfinite(got)or err>(0. if field=='entered'else 1e-12+1e-12*abs(value)):errors.append({'row':i,'field':field,'got':got,'expected':value});case['mismatches']+=1
 generation=load('REFERENCE_GENERATION.json')
 for n in generation['cases_with_no_step_require_native_typed_config_tests']:cases[n]={'scenario':n,'rows':0,'mismatches':0,'maximum_numeric_absolute':0.,'note':'C typed config/representation tests; no per-step parity claim'}
 dump('COMPARISON.json',{'scope':'NEW_NATIVE_C_INTERFACE_QUALIFICATION_NOT_OLD_PYTHON_SCORE','source_scenarios':63,'contexts':61,'reference_rows':1042,'mismatches':errors,'maximum_numeric_absolute':maxerr,'all_numeric_fields_binary64_bit_equal':bit_equal,'per_attempt_host_summary':runs,'native_checks':native_counts,'source_only_methods_with_zero_step':generation['cases_with_no_step_require_native_typed_config_tests'],'native_extension_revision':'01NULL-context unknown-state omission found by inspection;02fix+strict flags/context guards;03nested braces only','budgets_unchanged':all(sha(HERE/'NUMERICAL_BUDGET.json')==sha(HERE/f'revisions/host_attempt_{n:02d}/NUMERICAL_BUDGET.json')for n in [1,2,3]),'new_physics_steps':0,'old_score_updated':False})
 with(HERE/'SCENARIO_COMPARISON.csv').open('w',newline='',encoding='utf-8')as fp:
  w=csv.DictWriter(fp,fieldnames=['scenario','rows','mismatches','maximum_numeric_absolute','note']);w.writeheader();w.writerows(cases[n]for n in sorted(cases))
 assert not errors
 receipt=load('ARM_BUILD_02.json');assert receipt['success']and len(receipt['objects'])==2;objects=[]
 for r in receipt['objects']:
  p=Path(r['object']);raw=p.read_bytes();assert sha(p)==r['sha256']and len(raw)==r['bytes'];assert raw[:6]==b'\x7fELF\x01\x01';typ,machine=struct.unpack_from('<HH',raw,16);assert typ==1 and machine==40
  folder=HERE/r['target'];text=(folder/'target_macros_02.log').read_text();macros=dict(re.findall(r'^#define\s+(\S+)\s+(.*)$',text,re.M));selected={n:macros[n]for n in ['__ARM_FP','__ARM_PCS_VFP','__ARM_ARCH_7EM__','FLT_EVAL_METHOD','DBL_MANT_DIG','DBL_MAX_EXP','__SIZEOF_DOUBLE__']};assert selected=={'__ARM_FP':'0x6','__ARM_PCS_VFP':'1','__ARM_ARCH_7EM__':'1','FLT_EVAL_METHOD':'0','DBL_MANT_DIG':'53','DBL_MAX_EXP':'1024','__SIZEOF_DOUBLE__':'8'}
  attrs=(folder/'fromelf_02.log').read_text();assert f'Tag_CPU_name = "{r["cpu"]}"'in attrs and 'Tag_CPU_arch = ARM v7E-M'in attrs and re.search(r'Tag_ABI_VFP_args[^\n]*\(=1\)',attrs)
  imports=undef(raw);objects.append({**r,'ELF_type':'ET_REL','ELF_machine':'EM_ARM','ELF_class':'ELF32','endianness':'little','macros':selected,'VFP_args':1,'HardFP_use_original':re.search(r'Tag_ABI_HardFP_use[^\n]+',attrs)[0],'FP_arch_original':re.search(r'Tag_FP_arch[^\n]+',attrs)[0],'undefined_symbols':imports,'software_double_dependencies':[n for n in imports if n.startswith('__aeabi_d')or n.startswith('__aeabi_c')]})
 dump('OBJECT_SUMMARY.json',{'scope':'NEW_MODULE_COMPILE_ONLY_NO_TARGET_EXECUTION','objects':objects,'BSP_link_or_soft_double_library_resolution':False,'target_numerics_FPSCR_FTZ_and_WCET':False,'SP_hard_ABI_is_not_SP_arithmetic':True})
 print(json.dumps({'new_C_rows':len(actual),'new_C_mismatches':len(errors),'max_numeric_error':maxerr,'bit_equal':bit_equal,'native':native_counts['3'],'ARM_objects':len(objects),'undefined_symbols':{r['target']:r['undefined_symbols']for r in objects}}))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'analysis_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
