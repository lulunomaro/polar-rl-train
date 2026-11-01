from pathlib import Path
import ast
B=Path(__file__).resolve().parent
p=B/'build_h1_normal_mod4v1_source_v1.py';s=p.read_bytes().decode('utf-8')
a=" if t.count(a)!=1:raise ValueError('Exact source anchor '+label+' count='+str(t.count(a)))\n return t.replace(a,z,1)"
z=" if t.count(a)==0 and '\\n' in a and '\\r\\n' in t:\n  a=a.replace('\\n','\\r\\n');z=z.replace('\\n','\\r\\n')\n if t.count(a)!=1:raise ValueError('Exact source anchor '+label+' count='+str(t.count(a)))\n return t.replace(a,z,1)"
assert s.count(a)==1;s=s.replace(a,z,1)
a=" if O.exists():raise FileExistsError('Unused independent source output required; keep any old output unchanged: '+str(O))"
z=" if O.exists():\n  assert {x.name for x in O.iterdir()} <= {'ACTUAL_MOTHER453_IDENTITY.json','MOTHER453_INPUT_MANIFEST.json'}, 'Only preserved two metadata files from failedV1 may exist'"
assert s.count(a)==1;s=s.replace(a,z,1)
a=" with p.open('x',encoding='utf-8',newline='') as f:f.write(data)"
z=" if p.exists():\n  assert p.read_bytes()==data.encode('utf-8'), 'Existing failed-attempt metadata must stay byte-identical: '+str(p)\n else:\n  with p.open('x',encoding='utf-8',newline='') as f:f.write(data)"
assert s.count(a)==1;s=s.replace(a,z,1)
s=s.replace(' O.mkdir(parents=True)',' O.mkdir(parents=True,exist_ok=True)',1)
s=s.replace("generator_attempt='H1SRC_GENERATOR_V1'","generator_attempt='H1SRC_GENERATOR_V2_CRLF',prior_generator_error=str(B/'H1SRC_GENERATOR_ORIGINAL_ERROR_1793563116350502300.json'),prior_two_metadata_outputs_reused_byte_identically=True",1)
s=s.replace("trial_id='H1SRC_GENERATOR_V1'","trial_id='H1SRC_GENERATOR_V2_CRLF'",1)
needle=" save('SOURCE_GENERATION_HISTORY.json',"
location=" location,locref=jd(T/'reports/H1_typed_source_location_metadata_20261102_035651.json')\n save('SOURCE_LOCATION_METADATA_FROM_PARENT.json',dict(kind='PARENT_METADATA_SUPERSEDES_OLD_UNKNOWN_LOCATION_WITHOUT_CHILD_PT_ACCESS',parent_report=locref,value=location,new_actual_parent_source_path_still_required=True))\n"
assert s.count(needle)==1;s=s.replace(needle,location+needle,1)
ast.parse(s)
with (B/'build_h1_normal_mod4v1_source_v2.py').open('x',encoding='utf-8',newline='') as f:f.write(s)
print('Saved independent builderV2; V1 error/source/partial two metadata files remain unchanged.')
