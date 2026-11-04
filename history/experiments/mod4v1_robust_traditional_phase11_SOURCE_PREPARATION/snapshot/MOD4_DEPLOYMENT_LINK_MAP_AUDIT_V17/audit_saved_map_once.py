"""One owned saved-text map pass only. No ELF/binary parser, native tool or payload access."""
from pathlib import Path
import datetime,hashlib,json,re,traceback
D=Path(__file__).resolve().parent;R=D.parent;V=R/'MOD4_DEPLOYMENT_FIRST_LINK_V16'
COUNT=dict(this_worker_saved_stdout_semantic_opens=0,this_worker_saved_stderr_opens=0,image_object_library_payload_reads=0,image_object_library_payload_hashes=0,native_queries_compile_link_fromelf_armar_UV_model_FK_PHY_QA_Git_agents_Goal=0)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(name,v):
 with(D/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 assert not(D/'MAP_READ_INTENT.json').exists(),'Saved-map semantic grant already consumed; inspect own minimum, never replay'
 saved={n:load(V/n)for n in('RESULT.json','IMAGE_BASIC_OBSERVATIONS.json','NATIVE_RESULT.json')};basic=saved['IMAGE_BASIC_OBSERVATIONS.json'];assert saved['RESULT.json']['returncode']==saved['NATIVE_RESULT.json']['returncode']==0
 assert basic['SHA']=='a70772a2c56bf38c144817b86a27d2ca01d32aa288c17bdcb9b592987ff4f601'and basic['bytes']==629048
 paths=[Path(__file__),D/'PARENT_SCOPE.json']+[V/n for n in saved]+[R/'MOD4_DEPLOYMENT_LINK_PREP_V15/PROJECT_MEMORY_SELECTION.json']
 before=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p.read_bytes()))for p in paths]
 mapfile=V/'link.stdout.txt';errfile=V/'link.stderr.txt';stat=mapfile.stat();new('MAP_READ_INTENT.json',dict(status='PREDECLARED_SINGLE_WORKER_SAVED_MAP_SEMANTIC_PASS_NOT_GLOBAL_FIRST_READ',files=before,only_additional_saved_text=[str(mapfile),str(errfile)],map_bytes=stat.st_size,map_mtime_ns=stat.st_mtime_ns,prohibited_binary_native_and_physics_calls=0,parent_grep_and_link_wrapper_reads_already_occurred=True,PH11pending=True))
 COUNT['this_worker_saved_stdout_semantic_opens']+=1
 with mapfile.open('rb')as f:raw=f.read()
 text=raw.decode('utf-8');lines=text.splitlines();COUNT['this_worker_saved_stderr_opens']+=1
 with errfile.open('rb')as f:err=f.read()
 symbols=['__Vectors','__Vectors_End','__Vectors_Size','__initial_sp','Reset_Handler','SVC_Handler','PendSV_Handler','SysTick_Handler','SystemInit','__user_initial_stackheap','__heap_base','__heap_limit','__main','__rt_entry','__I$use$semihosting','__use_no_semihosting_swi','__semihosting_library_function','sys_command','sys_exit','sys_wrch']
 defs={n:[]for n in symbols};refs={n:[]for n in symbols};regions=[];totals=[];libraries=[];library_paths=[];components=[];headings=[];section='unclassified';diagnostics=[];libseen=set()
 libpat=re.compile(r'([^\s()]+\.(?:lib|l))\(([^()]+)\)',re.I)
 for i,line in enumerate(lines,1):
  lo=line.lower()
  if 'image symbol table'in lo:section='symbols';headings.append(dict(line=i,text=line))
  elif 'memory map of the image'in lo:section='memory';headings.append(dict(line=i,text=line))
  elif 'image component sizes'in lo:section='components';headings.append(dict(line=i,text=line))
  elif 'removing unused input sections'in lo:section='removed';headings.append(dict(line=i,text=line))
  elif 'section cross references'in lo:section='references';headings.append(dict(line=i,text=line))
  elif 'image entry point'in lo or 'load region'in lo or 'execution region'in lo:regions.append(dict(line=i,text=line))
  if re.search(r'\b(?:Warning|Error):',line):diagnostics.append(dict(line=i,text=line))
  if any(s in lo for s in('grand totals','elf image totals','rom totals','total ro  size','total rw  size','total rom size','code (inc. data)'))or re.search(r'Total\s+(?:RO|RW|ROM)\s+Size',line):totals.append(dict(line=i,text=line,section=section))
  for name in symbols:
   if name in line:
    item=dict(line=i,text=line,section=section)
    if re.match(r'^\s*'+re.escape(name)+r'\s+(?:0x[0-9a-fA-F]+|[0-9]+)(?:\s|$)',line):
     mm=re.match(r'^\s*'+re.escape(name)+r'\s+(0x[0-9a-fA-F]+|[0-9]+)',line);item['map_value']=int(mm.group(1),0);defs[name].append(item)
    elif len(refs[name])<8:refs[name].append(item)
  found=list(libpat.finditer(line))
  for m in found:
   key=(m.group(1),m.group(2),section)
   if key not in libseen:
    libseen.add(key);libraries.append(dict(library=m.group(1),member=m.group(2),line=i,text=line,section=section,interpretation='component_size_member_evidence'if section=='components'else'map_reference_not_by_itself_selected_member'))
  if re.search(r'\b(?:Library Name|Library Member Name|Library Totals|Library Member|library)\b',line,re.I)or re.search(r'[A-Za-z]:[\\/].*\.(?:lib|l)\b',line,re.I):
   library_paths.append(dict(line=i,text=line,section=section))
   if len(library_paths)>260:library_paths.pop(0)
  if section=='components'and line.strip():components.append(dict(line=i,text=line))
 # Save minimum before any prose/further assertions; original saved map will never be reopened.
 capacities=load(R/'MOD4_DEPLOYMENT_LINK_PREP_V15/PROJECT_MEMORY_SELECTION.json');minimum=dict(status='MINIMUM_SAVED_MAP_FACTS_PERSISTED_BEFORE_REPORT_NOT_NEW_ELF_VALIDATION',counts=COUNT.copy(),map_path=str(mapfile),map_buffer_SHA=sha(raw),map_bytes=len(raw),map_line_count=len(lines),stderr_path=str(errfile),stderr_buffer_SHA=sha(err),stderr_bytes=len(err),parent_and_wrapper_prior_reads_separate=True,original_saved_metadata=saved,project_memory_from_prior_own_static_metadata=capacities,headings=headings,regions=regions,size_totals=totals,definitions=defs,selected_reference_excerpts=refs,library_member_rows=libraries,library_path_and_heading_rows=library_paths,component_size_rows=components,diagnostic_patterns=diagnostics,no_binary_or_native_validation_performed=True,PH11pending=True)
 new('MINIMUM_MAP_FACTS.json',minimum)
 after=mapfile.stat();new('READ_COUNTS.json',dict(counts=COUNT,map_lines=len(lines),map_bytes=len(raw),map_stat_unchanged=(after.st_size,after.st_mtime_ns)==(stat.st_size,stat.st_mtime_ns),all_small_metadata_before_after_equal=all(sha(Path(x['path']).read_bytes())==x['SHA']for x in before),own_semantic_passes=1,not_global_map_read_count=True,saved_image_already_read_by_parent_not_this_worker=True,no_runtime_reachability_or_ABI_execution=True))
 print(json.dumps(dict(status=minimum['status'],counts=COUNT,map_lines=len(lines),regions=regions,size_totals=totals,definitions=defs,library_component_rows=[x for x in libraries if x['section']=='components'],library_path_rows=library_paths[-35:],component_tail=components[-30:]),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  e=traceback.format_exc();p=D/'FAILURE.txt'
  if not p.exists():p.write_text(e,encoding='utf-8')
  p=D/'FAILURE_SOURCE.py'
  if not p.exists():p.write_bytes(Path(__file__).read_bytes())
  print(e);raise
