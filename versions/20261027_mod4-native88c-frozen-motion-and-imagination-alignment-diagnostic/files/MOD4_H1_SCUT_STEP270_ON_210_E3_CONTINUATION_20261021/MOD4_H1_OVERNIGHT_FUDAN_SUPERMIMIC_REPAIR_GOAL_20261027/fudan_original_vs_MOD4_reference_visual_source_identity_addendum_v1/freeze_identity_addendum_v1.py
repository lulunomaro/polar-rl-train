"""Preserve newly found local-source versus actual producer byte differences."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json
D=Path(__file__).resolve().parent;T=D.parent.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
r=json.loads((J/'reports/FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json').read_text(encoding='utf-8'))
p=J/'actual_72_reference_text/reference_capture/upstream_actual_default_dt_standing_jump/HEADLESS_REVIEWED_AST_SOURCE.py'
local=J/'source/mujoco/python_tools/onnx_mj_chuanlian.py';xml=J/'source/mujoco/assert_now/infantry_binglian_yuntai/infantry_V2/meshes/mjmodel.xml'
ar=p.read_bytes();lr=local.read_bytes();xr=xml.read_bytes()
a={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(ar.decode('utf-8-sig'))) if isinstance(n,ast.FunctionDef)}
b={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(lr.decode('utf-8-sig'))) if isinstance(n,ast.FunctionDef)}
changed=[k for k in b if b[k]!=a.get(k)]
script_asset=next(x for x in r['assets'] if x['path'].endswith('/onnx_mj_chuanlian.py'))
xml_asset=next(x for x in r['assets'] if x['path'].endswith('/mjmodel.xml'))
report=dict(schema='mod4.fudan.visual_provenance.source_identity_addendum.v1',
 frozen_UTC=datetime.now(timezone.utc).isoformat(),
 primary_directory='fudan_original_vs_MOD4_reference_visual_provenance_v1',primary_INDEX_SHA='7780774b061d939a5a03906f2b0f72ccc5cdee69ed719d553086d07d7b23fcf4',
 original_producer_asset=script_asset,local_script=dict(path=str(local),bytes=len(lr),SHA=H(lr),CRLF_count=lr.count(b'\r\n')),
 actual_ran_headless_AST_source=dict(path=str(p),bytes=len(ar),SHA=H(ar),
  local_function_AST_comparison=changed,all_nonmain_and_nested_function_AST_exact=changed==['main'],
  note='HEADLESS derived actual producer source is authoritative executed text; original upstream script hash remains receipt7ab504..., not local97cf...'),
 actual_XML_asset_metadata=xml_asset,local_XML=dict(path=str(xml),bytes=len(xr),SHA=H(xr),matches_actual_producer_bytes=H(xr)==xml_asset['SHA']),
 classification='local source snapshots are not byte-identical to actual downloaded producer assets; source-identity gap, not policy/runtime/physics failure',
 limitations=['Do not label localJ XML exact actual producer collider geometry without the pinned XML content or an explicit semantic comparison.',
  'Primary provenance report preserves false same_pinned_source; its parsed local geometry/body order is source evidence, not fresh byte-verified actual scene.',
  'Canonical source JSON explicitly declares body order preorder+world, but exact fullbody geometry/name certification still needs pinnedXML mapping. Recorded body/world poses and taskspace root/wheels remain actual simulation data.',
  'No CRLF-only explanation for local script mismatch: CRLFcount0. Do not erase this mismatch as formatting without evidence.',
  'No new download/SSH/binary/actor/physics/model operation authorized or run here. Root may use known saved pose arrays and clearly labelled skeleton/primitive view; exact mesh view needs separately bound existing assets.'],
 no_binary_motion_mesh_or_weight_read=True,original_directories_unchanged=True,Git_supplementation='PENDING_ROOT')
put('SOURCE_IDENTITY_ADDENDUM_ACTUAL.json',report)
put('HANDOFF.md',f'''# FROZEN source-identity addendum

Primary provenance INDEX `7780774b061d939a5a03906f2b0f72ccc5cdee69ed719d553086d07d7b23fcf4` remains unchanged and preserves `same_pinned_source=False`.

Local original script SHA `{H(lr)}` differs from actual producer receipt `{script_asset['SHA']}`; CRLF0, so no line-ending excuse. Existing actual executed headless AST text `{p}` SHA `{H(ar)}` is available. All local named nonmain/nested functions match that actual headless AST; onlymain differs as expected for headless capture, but full byte identity must not be claimed.

Also local XML SHA `{H(xr)}` differs from actual captured asset receipt `{xml_asset['SHA']}`. The primary report's local scene/body tree is not a fresh byte-certified actual producer geometry. Preserve that limitation for rendering; fullbody exact collider/name mapping needs pinned original XML content/semantic verification and exact mesh availability. This helper does not download or query remote to fill it. Root/wheel taskspace canonical JSON and recorded fullbody arrays are existing data, not actor/physics reruns; label any schematic view accordingly.

No NPZ/npy/PT/ONNX/STL opened or hashed. No GPU/SDK/actor/physics/SSH/network/Git. This is a new additive source-read finding, not a new trial or training failure. Main frozen directory and all old data remain unchanged. OrdinaryGit supplement pendingroot.
''')
rows=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name!='INDEX.json':
  raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
put('INDEX.json',dict(files=rows,self_excluded='INDEX.json'))
print(json.dumps(dict(frozen=True,INDEX_SHA=H((D/'INDEX.json').read_bytes()),changed_functions=changed,local_XML_matches=False)))
