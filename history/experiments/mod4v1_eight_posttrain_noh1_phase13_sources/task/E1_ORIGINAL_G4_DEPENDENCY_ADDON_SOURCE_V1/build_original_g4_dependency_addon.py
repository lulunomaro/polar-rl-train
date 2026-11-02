"""Appendonlyexactg4 originaldependency; sourceonly, no model/SDK import."""
from pathlib import Path
import ast,hashlib,json,sys,types,importlib
B=Path(__file__).resolve().parent;T=B.parent;P=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016');V=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V2'
H=lambda x:hashlib.sha256(x).hexdigest()
def info(p):
 r=p.read_bytes();return dict(path=str(p),bytes=len(r),SHA=H(r))
def put(name,v):
 p=B/name
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return info(p)
a=P/'eval_payload_v2/g4_worldmesh_query_contract.py';b=P/'curb113_frozen_v2/eval_payload_v2/g4_worldmesh_query_contract.py';raw=a.read_bytes();assert raw==b.read_bytes() and H(raw)=='67bbebe6923e81842093c09ef04c07396897d942172aab38c05d2869d2ca4b89'
addon=B/'runtime_addon';addon.mkdir(exist_ok=False);target=addon/a.name
with target.open('xb') as f:f.write(raw)
baseg3=P/'eval_payload_v2/runtime/isaac/mod4/g3_cad_wave_geometry.py';s=baseg3.read_bytes();assert H(s)=='8b0f15d23f8891270727ff405d7af4a7282aa6952ab6449972c24b52884bb523'
j=json.loads((T/'E1_FOUR_WORKERS_REMOTE_NONPT_ORIGIN_DELTA_V1.json').read_bytes());manifest=[]
for row in j['rows']:
 allfiles=row['complete_nonPT_files_METADATA_ONLY'];g4=[r for r in allfiles if Path(r['relative']).name==a.name];g3=[r for r in allfiles if r['relative']=='runtime/isaac/mod4/g3_cad_wave_geometry.py'];prof=[r for r in allfiles if r['relative']=='runtime/isaac/mod4/g3_cad_profile.json'];assert not g4 and len(g3)==len(prof)==1
 assert g3[0]['sha256']==H(s);manifest.append(dict(role=row['role'],saved_original_nonPT_stage_g4_entries=0,own_runtime_g3=g3[0],own_runtime_g3_profile=prof[0],runtime_mod_path_already_added_bychild=True,source_refs_metadata_only=info(T/'E1_FOUR_WORKERS_REMOTE_NONPT_ORIGIN_DELTA_V1.json')))
# Module-loadclosureonly; g3.configure_g3 SDK importsarelazy/unusedbyCURBhelpers.
closure=[]
for label,p in [('originalg4',a),('sameown113g4',b),('originalg3',baseg3),('currentCURBhelper',V/'curb_worldmesh_query_contract_v1.py')]:
 r=p.read_bytes();tree=ast.parse(r,filename=str(p));compile(tree,str(p),'exec');top=[];lazy=[]
 for n in tree.body:
  if isinstance(n,ast.Import):top.extend(x.name for x in n.names)
  if isinstance(n,ast.ImportFrom):top.append(n.module)
 for n in ast.walk(tree):
  if isinstance(n,ast.ImportFrom) and n not in tree.body:lazy.append(n.module)
 closure.append(dict(label=label,**info(p),module_top_imports=top,nested_only_imports=lazy,AST_SHA=H(ast.dump(tree,include_attributes=False).encode())))
# Purestdlibimportwitness withnamedexternalnumpy/trimeshstubs, nofunctionexecution.
smoke=[];original_path=sys.path[:];saved={k:sys.modules.get(k) for k in ('numpy','trimesh','curb_worldmesh_query_contract_v1','g4_worldmesh_query_contract','g3_cad_wave_geometry','curb20_geometry')}
try:
 for row in manifest:
  role=row['role'];mod=Path(row['own_runtime_g3']['local_dependency_path']).parent
  for name in ('curb_worldmesh_query_contract_v1','g4_worldmesh_query_contract','g3_cad_wave_geometry','curb20_geometry'):sys.modules.pop(name,None)
  sys.modules['numpy']=types.ModuleType('numpy_EXTERNAL_STUB_NO_ARRAY_FUNCTIONS');sys.modules['trimesh']=types.ModuleType('trimesh_EXTERNAL_STUB_NO_MESH_FUNCTIONS')
  sys.path[:]=[str(addon),str(mod),str(V)]+original_path
  q=importlib.import_module('curb_worldmesh_query_contract_v1');g=importlib.import_module('g4_worldmesh_query_contract');gg=importlib.import_module('g3_cad_wave_geometry')
  assert callable(q.expected_ground) and callable(g.canonical_triangles) and callable(g.downward_triangle_heights)
  assert Path(g.__file__).resolve()==target.resolve() and H(Path(gg.__file__).read_bytes())==row['own_runtime_g3']['sha256']
  smoke.append(dict(role=role,module_import_resolved=True,g4_file=str(g.__file__),g3_file=str(gg.__file__),external_numpy_trimesh='STUB_ONLY',geometry_orSDK_orphysicsfunctions_called=0))
finally:
 sys.path[:]=original_path
 for name,value in saved.items():
  if value is None:sys.modules.pop(name,None)
  else:sys.modules[name]=value
proof=put('G4_SOURCE_IMPORT_CLOSURE_AND_MINIMAL_STAGE_V1.json',dict(kind='SOURCE_ONLY_ORIGINAL_BYTE_EXACT_DEPENDENCY_ADDON',minimal_runtime_addition=info(target),copy_destination='GROUP_ROOT/worker_sources/e1/g4_worldmesh_query_contract.py alongsidecurb_worldmesh_query_contract_v1.py; nochangeoldfunctions/predicate/asset/geometry',identical_original_producers=[info(a),info(b)],importclosure=closure,saved_manifest=manifest,importsmoke=smoke,geometry_scope='CURBexpected_ground stillusescurb20_geometry.make_mesh; onlyg4canonical_triangles/downward_triangle_heights imported. g4expected_ground(make_meshwave) isnotcalled, noWAVEgeometrysubstitute.',existing_dependencies='g3py+g3profile alreadyinall4ownruntime/modandcurrentchildmodsyspath. numpy/trimesh areexistingactualenvironmentpackages; stubimportsmoke notnumericalorSDKqualification.',new_B_or_lib_syspath_required=False,reason='NoG4entryinoriginalsuccessfulnonPTstagefilewhiteLists, notmerelyB/libimportpathmissing accordingtosavedmetadata. Actualremoteunindexedextrafilesnotinspected.',source_PT_stat_read_hash_decode_raw_NPZ_USD_SSH_SDK_GPU_orGO=0))
erratum=put('PRIOR_13_FILE_COMPLETENESS_APPEND_ONLY_ERRATUM_V1.json',dict(kind='SOURCE_PACKAGING_OMISSION_NOT_SKILL_OR_PHYSICS_RESULT',old_V1_index=info(T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/FINAL_FOUR_E1_PARALLEL_N80_SOURCE_INDEX_V1.json'),old_V2_index=info(V/'FINAL_FOUR_E1_PARALLEL_N80_SOURCE_INDEX_V2.json'),old_claim_scope_correction='13runtimefileswereenumeratedbutnotcompleteimportclosureforCURBaux. ASTcompile+stdlibsemanticMOCKdidnotimportCURBauxlazybranch, missedg4topdependency. Preserveoldindex/proofs/errors,notrewriteascomplete.',observed_closed_V6_error=info(T/'reports/NINE_SINGLE_GPU_V6_CLOSED_20261102_100350/CURB_INDEPENDENT113/WORKER_ERROR.json'),actual_failure='CURB113afterownreset/geometryquery, beforeREADY/commonstart, ModuleNotFoundErrorg4fromCURBauxL4. Groupcontrolledstep0 perparentclosedreceipt; notexpertfailureornewskilldata.',fix='Onlyaddexact2975B67bbg4sourcebyteforbytebesideauxinnewunusedgroup; no data/predicatechanges. Existingg3resolvermodunchanged.',remaining_scope='Minimalmissingdependency verifiedagainstoriginalproducer+savedruntime manifests; notanunqualifiedwholeSDKimportqualification.',source_lookup_error=dict(path=str(P/'eval_payload_v2/g3_cad_wave_geometry.py'),result='notfound',resolved=str(baseg3)),remote_touched=False,old_source_or_group_modified=False))
files=[info(p) for p in sorted(B.rglob('*')) if p.is_file()]
index=put('FINAL_G4_DEPENDENCY_ADDON_SOURCE_INDEX_V1.json',dict(runtime_addon_files=[info(target)],proof=proof,old_completeness_erratum=erratum,files=files,source_only=True,parent_archive_append_pending=True,no_Git=True))
print(json.dumps(dict(index=index,proof=proof,erratum=erratum,runtime_addon=info(target),importsmoke_roles=len(smoke),PT_SDK_calls=0),indent=2))
