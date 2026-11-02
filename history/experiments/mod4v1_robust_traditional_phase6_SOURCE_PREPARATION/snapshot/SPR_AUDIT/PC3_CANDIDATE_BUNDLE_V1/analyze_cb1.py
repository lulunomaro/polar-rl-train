"""Read saved evidence once. NO executable/compiler/SDK/core/oracle reruns."""
from pathlib import Path
import csv,hashlib,json,re,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(v):return struct.unpack('<I',struct.pack('<f',float(v)))[0]
def dump(name,value):
 with (HERE/name).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,allow_nan=False)
def elf(p):
 b=p.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01';typ,machine=struct.unpack_from('<HH',b,16);assert (typ,machine)==(1,40)
 off=struct.unpack_from('<I',b,32)[0];step,n,strings=struct.unpack_from('<HHH',b,46);assert step==40
 sections=[struct.unpack_from('<IIIIIIIIII',b,off+i*step)for i in range(n)];s=sections[strings];names=b[s[4]:s[4]+s[5]]
 def name(buf,i):return buf[i:buf.find(b'\0',i)].decode('ascii')
 und=[];writable=[];exports=[]
 for s in sections:
  if s[2]&3==3 and s[5]:writable.append(dict(name=name(names,s[0]),bytes=s[5]))
  if s[1]==2:
   st=sections[s[6]];ss=b[st[4]:st[4]+st[5]];assert s[9]==16
   for j in range(0,s[5],16):
    nm,val,size,info,other,index=struct.unpack_from('<IIIBBH',b,s[4]+j)
    if nm:
     text=name(ss,nm)
     if index==0:und.append(text)
     elif info>>4==1:exports.append(text)
 assert not writable
 assert not any('pc3_cycle'in x or'enqueue'in x for x in und+exports)
 return dict(format='ELF32_LE_ET_REL_EM_ARM',undefined_symbols=sorted(set(und)),global_defined_symbols=sorted(set(exports)),allocated_writable_sections=writable)
def main():
 first=HERE/'host_attempt_01';second=HERE/'host_attempt_02';h1=json.loads((HERE/'HOST_BUILD_01.json').read_bytes());h2=json.loads((HERE/'HOST_BUILD_02.json').read_bytes());assert not h1['success']and h2['success']
 for n,v in h1['sources'].items():
  if n!='cb1_native_tests.c':assert sha(HERE/n)==v
 assert h2['cases_rerun']==0 and h2['reused_case_sha']==sha(first/'CANDIDATE_RUNS.jsonl')
 # Prove the ONLY test change is the approved raw-cache-before/after snapshot.
 old=(first/'cb1_native_tests.c').read_text();new=(HERE/'cb1_native_tests.c').read_text()
 inverse=new.replace('cb1_status code;unsigned j;float raw_saved[14];','cb1_status code;unsigned j;').replace('saved=out;memcpy(raw_saved,c.estimator.last_raw.state14,sizeof(raw_saved));next','saved=out;next').replace('CK(!memcmp(c.estimator.last_raw.state14,raw_saved,sizeof(raw_saved)));','CK(!memcmp(c.estimator.last_raw.state14,saved.candidate.state14,14*sizeof(float)));')
 assert inverse==old and new==(second/'cb1_native_tests.c').read_text()
 assert (first/'CLOCK_INSERTIONS.csv').read_bytes()==(second/'CLOCK_INSERTIONS.csv').read_bytes()
 v3=ROOT/'SPR_AUDIT/portable_control_v3_current';saved=[json.loads(s)['reply']for s in (ROOT/'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/ROUNDTRIP_01.jsonl').read_text().splitlines()]
 actual=[json.loads(s)for s in (first/'CANDIDATE_RUNS.jsonl').read_text().splitlines()];layout=json.loads((v3/'REFERENCE_LAYOUT.json').read_bytes())['offsets']
 with (v3/'REFERENCE_VECTORS.csv').open(newline='')as f:rows=list(csv.reader(f))[1:]
 assert len(rows)==len(saved)==len(actual)==3200
 errors=[];distinct=0;bycase={}
 for i,(raw,want,got)in enumerate(zip(rows,saved,actual)):
  def group(n):start,length=layout[n];return [float(x)for x in raw[start:start+length]]
  one=lambda n:int(group(n)[0]);case=one('SCENARIO')
  gold=want['STATE14']+want['REF14']+want['MATH_TAU']+want['GUARDED_TAU']+[want[n]for n in ('SHAPER_V','SHAPER_W','SHAPER_A','YAW_I')]+[want['REF14'][7],want['REF14'][8],want['SHAPER_A'],want['ROLL']]
  expected_bits=[bits(v)for v in gold];inputs=group('OFFSET')+group('ACC_CORR')+group('RADIUS')+sum((group(n)for n in ('GYRO','ACCEL','Q4','DQ4','SPIN2','FORWARD','YAW_COMMAND')),[])
  ok=got['row']==i and got['scenario']==case and got['status']==0 and got['valid']==1 and got['send']==0 and got['row_failures']==0 and got['polls']==5
  mismatch=sum(a!=b for a,b in zip(got['actual_bits48'],expected_bits));inputdiff=sum(a!=bits(b)for a,b in zip(got['input_bits23'],inputs));gyro=got['gyro_bits3']==[bits(v)for v in group('GYRO')]
  md={'source_us':one('STAMP'),'arrival_us':one('NOW'),'estimate_us':one('NOW'),'drive_us':one('STAMP'),'aperture_us':one('STAMP')-one('WINDOW_BEGIN'),'mean_count':one('MEAN_COUNT')}
  if not ok or mismatch or inputdiff or not gyro or any(got[k]!=v for k,v in md.items()):errors.append(dict(row=i,output_bit_mismatches=mismatch,input_bit_mismatches=inputdiff))
  distinct+=int(expected_bits[40]!=expected_bits[44]or expected_bits[41]!=expected_bits[45]);bycase[case]=bycase.get(case,0)+1
 def stats(p):m=re.search(r'checks=(\d+) failures=(\d+)',p.read_text());assert m;return dict(checks=int(m[1]),failures=int(m[2]))
 case_stats=stats(first/'run_cases.stderr.log');native1=stats(first/'run_native.stderr.log');native2=stats(second/'run_native.stderr.log')
 assert case_stats==dict(checks=268829,failures=0)and native1==dict(checks=1583,failures=1)and native2==dict(checks=1583,failures=0)
 assert 'PASS'in(second/'run_cpp.stdout.log').read_text()
 with (second/'CLOCK_INSERTIONS.csv').open(newline='')as f:clock=list(csv.DictReader(f))
 assert len(clock)==25 and all(r['candidate_valid']==r['send']=='0'for r in clock)
 for r in clock:
  phase=int(r['phase']);assert [int(r[n])for n in ('estimator_calls','p25_calls','dc_calls')]==[int(phase>=1),int(phase>=2),int(phase>=3)]
 assert not errors and distinct==238
 nm=(second/'new_core_undefined_symbols.stdout.log').read_text();assert 'pc3_cycle'not in nm and'enqueue'not in nm
 exes=[]
 for rec in (h1,h2):
  for c in rec['commands']:
   if c.get('artifact','').endswith('.exe'):
    p=Path(c['artifact']);assert sha(p)==c['sha256'];b=p.read_bytes();off=struct.unpack_from('<I',b,60)[0]
    assert b[:2]==b'MZ'and b[off:off+4]==b'PE\0\0'and struct.unpack_from('<H',b,off+4)[0]==0x14c and struct.unpack_from('<H',b,off+24)[0]==0x10b
    exes.append(dict(path=p.relative_to(HERE).as_posix(),sha256=sha(p),bytes=len(b),format='PE32_i386'))
 compare=dict(status='NEW_CANDIDATE_SAVED_EVIDENCE_PASS',rows=3200,scenarios=bycase,output_float_bit_comparisons=153600,compiled_fixture_float_bit_comparisons=73600,gyro_float_bit_comparisons=9600,bit_or_discrete_errors=errors,internal_effective_distinct_rows=distinct,case_host_checks=case_stats,native_attempt01=native1,native_attempt02=native2,accepted_host_checks=case_stats['checks']+native2['checks'],CPP_actual_pass=True,clock_insertions=25,cases_rerun=0,core_recompiled_after_attempt01=False,only_change='approved NEW test raw-cache-before/after oracle; old 1fail remains failed',no_send_symbol_inventory=nm.splitlines(),host_sizeof=dict(context=1280,workspace=720,output=416,input=272),host_executables=exes,physics_or_old_SDK_runs=0)
 dump('COMPARISON.json',compare)
 arm=json.loads((HERE/'ARM_BUILD_01.json').read_bytes());assert arm['success'];objects=[]
 for r in arm['objects']:
  p=Path(r['object']);assert sha(p)==r['sha256'];info=elf(p);folder=p.parent
  macros=dict(re.findall(r'^#define\s+(\S+)\s+(.+)$',(folder/'target_macros.log').read_text(),re.M))
  keys=['__ARM_ARCH_7EM__','__ARMEL__','__thumb__','__ARM_FP','__ARM_PCS_VFP','__FLT_MANT_DIG__','__FLT_EVAL_METHOD__','__SIZEOF_FLOAT__']
  assert all(macros[k]=='1'for k in keys[:3])and macros['__ARM_FP']=='0x6'and macros['__ARM_PCS_VFP']=='1'and macros['__FLT_MANT_DIG__']=='24'and macros['__FLT_EVAL_METHOD__']=='0'and macros['__SIZEOF_FLOAT__']=='4'
  attrs=dict(re.findall(r'^\s*(Tag_\S+)\s*=\s*(.*)$',(folder/'fromelf.log').read_text(),re.M))
  assert 'v7E-M'in attrs['Tag_CPU_arch']and attrs['Tag_ABI_VFP_args'].endswith('(=1)')and attrs['Tag_ABI_HardFP_use'].endswith('(=1)')
  objects.append(dict(**r,**info,macros={k:macros[k]for k in keys},attributes=attrs))
 dump('OBJECT_FACTS.json',dict(scope='2_NEW_CB1_OBJECTS_ONLY',objects=objects,ARM_execution=0,BSP_or_C3_link=False,FPSCR_gradual_runtime_stack_WCET=False,fp_arch8_note='M7 old-fromelf FP ISA label is not CPU ISA; CPU remains ARMv7E-M'))
 print(json.dumps(dict(rows=3200,bit_discrete_errors=len(errors),accepted_host_checks=compare['accepted_host_checks'],CPP=True,new_ARM_objects=len(objects),old_SDK_physics_runs=0),indent=2))
if __name__=='__main__':main()
