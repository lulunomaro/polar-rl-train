"""Exactly four new pure attribute fixtures, then one existing-object static QA.
No subprocess, old inspector import, SDK, compilation, disassembly or link.
"""
from pathlib import Path
import hashlib,json,re,struct,traceback
from scoped_attrs_v7 import parse_attributes,inspect_elf,ParseError,ScopeConflict
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def out(name,data):
 with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def ub(x):
 b=bytearray()
 while True:
  y=x&127;x>>=7;b.append(y|(128 if x else 0))
  if not x:return bytes(b)
def av(tag,value):
 if isinstance(value,str):return ub(tag)+value.encode('ascii')+b'\0'
 return ub(tag)+ub(value)
def block(kind,ids,values):
 payload=(b''.join(ub(i) for i in ids)+b'\0') if kind!=1 else b''
 payload+=b''.join(av(t,v) for t,v in values)
 return ub(kind)+struct.pack('<I',len(ub(kind))+4+len(payload))+payload
def region(blocks):
 payload=b'aeabi\0'+b''.join(blocks)
 return b'A'+struct.pack('<I',4+len(payload))+payload

def make_fixtures():
 f1=region([block(1,[],[(18,2),(26,1),(64,0)]),block(2,[1],[(67,'2.09')]),block(2,[3],[(18,4)])])
 f2=region([block(1,[],[(20,2)]),block(2,[1,2],[(18,2),(26,1)]),block(3,[7],[(26,2)])])
 f3=region([block(1,[],[(18,2)]),block(1,[],[(18,4)])])
 f4=region([ub(2)+struct.pack('<I',6)+ub(1)])
 return [dict(id=1,name='inheritance_nodefaults',hex=f1.hex(),sections=[1,2,3],symbols={},expected='PASS_VALUES'),dict(id=2,name='multi_section_symbol_default',hex=f2.hex(),sections=[1,2,3],symbols={'7':2},expected='PASS_VALUES'),dict(id=3,name='same_scope_conflict',hex=f3.hex(),sections=[1],symbols={},expected='ScopeConflict'),dict(id=4,name='bounded_missing_index_terminator',hex=f4.hex(),sections=[1],symbols={},expected='ParseError_truncated_ULEB32')]

class Checks:
 def __init__(self):self.count=0
 def yes(self,value,message):
  self.count+=1
  if not value:raise AssertionError(message)

def run_fixture(f):
 c=Checks();data=bytes.fromhex(f['hex'])
 record={'id':f['id'],'name':f['name'],'blob_bytes':len(data),'blob_SHA256':sha(data),'parse_attempts':1,'expected':f['expected']}
 try:
  a=parse_attributes(data,f['sections'],{int(k):v for k,v in f['symbols'].items()})
 except (ScopeConflict,ParseError) as exc:
  record['observed_error']={'type':type(exc).__name__,'text':str(exc)}
  if f['id']==3:
   c.yes(type(exc) is ScopeConflict,'expected conflict, not another parser error')
   c.yes('same FILE' in str(exc) and 'tag 18' in str(exc),'conflict must name same scope and tag')
  elif f['id']==4:
   c.yes(type(exc) is ParseError,'expected boundary error, not conflict')
   c.yes('truncated ULEB32 within declared scope' in str(exc),'missing terminator must stop at declared boundary')
  else:raise
 else:
  c.yes(f['id'] in (1,2),'malformed/conflicting fixture was accepted')
  cells={}
  for s in f['sections']:
   cells[str(s)]={str(t):a.typed(t,('SECTION',s)) for t in (18,26)}
  record['section_cells']=cells
  if f['id']==1:
   c.yes(cells['1']['18']['value']==2 and cells['1']['26']['value']==1,'nonempty child inherits FILE 2/1')
   c.yes(cells['1']['18']['origin_scope']=='FILE' and cells['1']['26']['origin_scope']=='FILE','inheritance source FILE')
   c.yes(cells['2']['18']['value'] is None and cells['2']['26']['value'] is None,'empty child under nodefaults undefined, even FILE explicit values')
   c.yes(cells['2']['18']['classification']=='UNKNOWN' and cells['2']['26']['classification']=='UNKNOWN','undefined is unknown, not default zero')
   c.yes(cells['3']['18']['value']==4 and cells['3']['26']['value']==1,'explicit SECTION overrides only its own tag')
   c.yes(cells['3']['18']['origin_scope']=='SECTION#3' and cells['3']['26']['origin_scope']=='FILE','override/inheritance provenance')
  else:
   for s in ('1','2'):
    c.yes(cells[s]['18']['value']==2 and cells[s]['26']['value']==1,'one multi-section record applies to both IDs')
   c.yes(cells['3']['18']['value']==0 and cells['3']['26']['value']==0,'omitted FILE values normative zero')
   c.yes(cells['3']['18']['classification']=='UNUSED' and cells['3']['26']['classification']=='UNUSED','zero means prohibited type use, not compiler size')
   c.yes(cells['3']['18']['origin_kind']=='NORMATIVE_PUBLIC_DEFAULT_ZERO','source of zero is normative default')
   s18=a.typed(18,('SYMBOL',7));s26=a.typed(26,('SYMBOL',7))
   record['symbol7_cells']={'18':s18,'26':s26}
   c.yes(s18['value']==2 and s18['origin_scope']=='SECTION#2','SYMBOL inherits section')
   c.yes(s26['value']==2 and s26['origin_scope']=='SYMBOL#7','SYMBOL overrides enum without same-scope conflict')
 record.update(status='PASS',checks=c.count)
 return record

def saved_section_metadata(text):
 pieces=re.split(r'(?m)^\*\* Section #(\d+)\s*$',text)
 result={}
 for i in range(1,len(pieces),2):
  n=int(pieces[i]);body=pieces[i+1]
  name=re.search(r'(?m)^\s*Name\s*:\s*(.+)$',body)
  flags=re.search(r'(?m)^\s*Flags\s*:.*\(0x([0-9a-fA-F]+)\)',body)
  size=re.search(r'(?m)^\s*Size\s*:\s*(\d+) bytes',body)
  if name and flags and size:result[n]={'name':name.group(1).strip(),'flags':int(flags.group(1),16),'size':int(size.group(1))}
 return result

def saved_public_scopes(text):
 headers=list(re.finditer(r"(?m)^    '([^']+)' (file|section|symbol) build attributes[^\n]*:\s*$",text))
 result=[]
 wanted={18:'ABI_PCS_wchar_t',26:'ABI_enum_size',24:'ABI_align_needed',30:'ABI_optimization_goals'}
 for i,m in enumerate(headers):
  body=text[m.end():headers[i+1].start() if i+1<len(headers) else len(text)]
  if m.group(1)!='aeabi':continue
  ids=[int(x) for x in re.findall(r'(?m)^\s+[^\n]+ \(#(\d+)\)\s*$',body)]
  tags={}
  for t,name in wanted.items():
   v=re.search(r'(?m)^\s*Tag_'+name+r' = [^\n]*\(=(\d+)\)\s*$',body)
   if v:tags[str(t)]=int(v.group(1))
  conf=re.search(r'(?m)^\s*Tag_conformance = "([^"]*)"\s*$',body)
  if conf:tags['67']=conf.group(1)
  result.append({'kind':m.group(2).upper(),'indices':ids,'selected_explicit_tags':tags})
 return result

def main():
 snapshot=load(HERE/'INPUT_SNAPSHOT.json');old={}
 for ref in snapshot['old_read_only_inputs']:
  b=(ROOT/ref['path']).read_bytes()
  assert len(b)==ref['bytes'] and sha(b)==ref['SHA256'],ref['path']
  old[ref['path']]=b
 fixtures=make_fixtures();assert len(fixtures)==4 and all(len(bytes.fromhex(f['hex']))<=4096 for f in fixtures)
 out('FIXTURE_PLAN_01.json',{'new_fixtures_only':True,'count':4,'fixtures':fixtures})
 out('QA_PREEXEC.json',{'method_SHA256':sha((HERE/'METHOD.md').read_bytes()),'reader_SHA256':sha((HERE/'scoped_attrs_v7.py').read_bytes()),'runner_SHA256':sha(Path(__file__).read_bytes()),'input_snapshot_SHA256':sha((HERE/'INPUT_SNAPSHOT.json').read_bytes()),'fixture_plan_SHA256':sha((HERE/'FIXTURE_PLAN_01.json').read_bytes()),'fixture_parse_calls_planned':4,'real_object_parse_calls_planned':1,'ARM_native_planned':0})
 records=[]
 try:
  for f in fixtures:
   record=run_fixture(f);records.append(record)
   print(json.dumps({'fixture':f['name'],'status':record['status'],'checks':record['checks']}))
  out('FIXTURE_RESULTS_01.json',{'status':'PASS','fixture_count':4,'parse_attempts':4,'checks':sum(x['checks'] for x in records),'records':records,'old_QA_calls':0})
  objref=snapshot['old_read_only_inputs'][0];textref=snapshot['old_read_only_inputs'][1];gateref=snapshot['old_read_only_inputs'][3]
  result=inspect_elf(old[objref['path']]);attrs=result.pop('attributes')
  text=old[textref['path']].decode('utf-8');gate=json.loads(old[gateref['path']].decode('utf-8'));c=Checks()
  file_tags={str(k):v for k,v in attrs.scope(('FILE',0))['tags'].items()}
  c.yes(file_tags==gate['attributes']['merged_tags'],'new explicit FILE observations must equal immutable old recorded observations')
  c.yes(gate['pass_gate'] is False,'old gate remains false')
  c.yes([x['actual'] for x in gate['checks'] if x.get('tag') in (18,26)]==['UNKNOWN','UNKNOWN'],'old file-only unknown entries remain unchanged')
  expected={6:13,7:77,9:2,10:6,20:2,27:1,28:1}
  for tag,value in expected.items():c.yes(file_tags.get(str(tag))==value,'existing CPU/FPU/args/denormal observation changed')
  rows=result['code_sections'];saved=saved_section_metadata(text)
  c.yes(len(rows)==6,'expected all six executable sections')
  for row in rows:
   c.yes(row['id'] in saved,'code section missing from saved fromelf metadata')
   for key in ('name','flags','size'):c.yes(row[key]==saved[row['id']][key],'section metadata differs from saved fromelf')
   if row['id'] in (1,2,3):
    for tag in (18,26):
     cell=row['tag'+str(tag)]
     c.yes(cell['value']==0 and cell['classification']=='UNUSED' and cell['origin_kind']=='NORMATIVE_PUBLIC_DEFAULT_ZERO','intrinsic section needs normative unused zero, not forced 2/1')
   elif row['id'] in (4,5,6):
    for tag,value in ((18,2),(26,1)):
     cell=row['tag'+str(tag)]
     c.yes(cell['value']==value and cell['origin_scope']=='SECTION#'+str(row['id']),'function section explicit provenance')
  saved_scopes=saved_public_scopes(text)
  c.yes(len(saved_scopes)==len(attrs.raw_public_blocks),'public scope count differs from existing fromelf')
  for a,b in zip(attrs.raw_public_blocks,saved_scopes):
   c.yes(a['kind']==b['kind'] and a['indices']==b['indices'],'public scope kind/index list mismatch')
   actual={str(t['tag']):t['value'] for t in a['attributes'] if t['tag'] in (18,26,24,30,67)}
   c.yes(actual==b['selected_explicit_tags'],'scope type/alignment/optimization/conformance differs from saved fromelf')
  c.yes(not attrs.symbol_ids and not result['symbol_table_index_metadata_read'],'actual object has no public SYMBOL scope')
  c.yes(all(64 not in s['tags'] for s in attrs.scopes.values()),'actual public scopes unexpectedly contain nodefaults')
  unknown=sum(row['tag'+str(tag)]['classification']=='UNKNOWN' for row in rows for tag in (18,26))
  c.yes(unknown==0,'actual code-section type attribute remains unknown')
  compatible=all(row['tag'+str(tag)]['value'] in (0,want) for row in rows for tag,want in ((18,2),(26,1)))
  c.yes(compatible,'actual code section is neither requested type contract nor unused')
  for ref in snapshot['old_read_only_inputs']:c.yes(sha((ROOT/ref['path']).read_bytes())==ref['SHA256'],'old immutable input changed')
  result.update(status='PASS_STATIC_THIS_OBJECT_ONLY',object_reference=objref,saved_fromelf_reference=textref,old_file_only_explicit_tags_unchanged=file_tags,new_file_effective18=attrs.typed(18,('FILE',0)),new_file_effective26=attrs.typed(26,('FILE',0)),public_raw_blocks=attrs.raw_public_blocks,vendor_blocks=attrs.vendor_blocks,public_symbol_scope_count=len(attrs.symbol_ids),scope_metadata_checks=c.count,fixture_count=4,fixture_checks=sum(x['checks'] for x in records),real_object_parse_attempts=1,code_type_unknown_count=unknown,code_type_same_scope_conflict_count=0,code_type_contracts_expected_or_unused=compatible,original_V6_record={'compiler_success_count':1,'post_ABI_accepted_prefix_count':0,'pass_gate':False,'unchanged':True},assessment={'original_file_parser_unknown_resolved_for_this_object':True,'original_gate_rewritten':False,'remaining_161_C_plus_1_ASM_may_be_submitted_for_separate_parent_review':True,'native_continuation_authorized':False,'full_target_or_library_ABI_qualified':False,'runtime_FPSCR_hardware_qualified':False},new_ARM_native_fromelf_compile_probe_link_calls=0)
  out('OBJECT_SCOPE_RESULT_01.json',result)
  print(json.dumps({'status':result['status'],'fixture_count':4,'fixture_checks':result['fixture_checks'],'object_metadata_checks':c.count,'code_sections':len(rows),'unknown':unknown,'conflicts':0,'old_V6_compiler_success':1,'old_V6_ABI_prefix':0,'new_ARM_native':0}))
 except BaseException as exc:
  out('PARTIAL_ERROR_01.json',{'status':'STOPPED_STATIC_REVIEW_ERROR','completed_fixture_records':records,'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'new_ARM_native':0,'no_retry_automatic':True})
  raise
if __name__=='__main__':main()
