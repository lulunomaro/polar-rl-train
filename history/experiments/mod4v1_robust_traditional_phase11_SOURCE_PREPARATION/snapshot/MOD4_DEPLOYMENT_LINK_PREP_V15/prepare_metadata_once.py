"""Bounded JSON/stat/source-config preparation only. Never open payload objects/libs or invoke tools."""
from pathlib import Path
import datetime,hashlib,json,traceback,itertools
R=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def new(n,x):
 p=D/n
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def meta(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))
def main():
 assert not(D/'MINIMUM_INPUT_REGISTRY.json').exists(),'Existing preparation: inspect; never replay'
 paths=[D/'PARENT_SCOPE.json',D/'LINKER_QUERY_INTENT.json',D/'LINKER_QUERY_LEDGER.json',D/'armlink_help.stdout.txt',D/'armlink_help.stderr.txt',Path(__file__),R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6/COMPILE_RESULT_V6_01.json',R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8/COMPILE_RESULT_V8_01.json',R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V11/COMPILE_RESULT_V11_01.json',R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/RESULT.json',R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/PREEXEC.json',R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/OBJECT_OBSERVATIONS.json',R/'MOD4_DEPLOYMENT_PORT_V1/SUPPLEMENT_RECEIPT.json',R/'PH10_PARENT_SNAPSHOT_REVIEW_V1.json',R/'MOD4_DEPLOYMENT_ABI_SCOPE_STATIC_V7/REPORT.md',R/'MOD4_DEPLOYMENT_SCOPED_READER_V10/REPORT.md']
 project=R/'MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx';oldscatter=project.parent/'standard_tpye_c/standard_tpye_c.sct';paths.extend([project,oldscatter]);before=[meta(p)for p in paths]
 query=load(D/'LINKER_QUERY_LEDGER.json');assert query['returncode']==0 and query['native_queries']==1
 inputs=[];counts={}
 for v in(6,8,11):
  path=R/f'MOD4_DEPLOYMENT_TARGET_COMPILE_V{v}'/f'COMPILE_RESULT_V{v}_01.json';data=load(path);tu=data['TU_results'];counts[f'V{v}']=len(tu)
  for z in tu:
   o=z['object'];p=Path(o['path']);s=p.stat();assert z['exit']==0 and p.is_file()and s.st_size==o['bytes'],('bad existing object metadata',z['id'],str(p))
   inputs.append(dict(source_id=z['id'],name=z['name'],language='C',source_producer=z.get('source_before',z.get('source_now')),object=o,stat_bytes=s.st_size,stat_mtime_ns=s.st_mtime_ns,producer_record_path=str(path),producer_record_status=data['status'],original_scope_pass=z.get('scope_pass',data.get('first_object_gate',{}).get('pass_gate')),later_static_assessment_separate='V7 for id1; V10 for id40; never overwrite original gates'if z['id']in(1,40)else None,payload_read_or_rehash=False,current_bytes_identity_NOT_verified=True))
 assert counts==dict(V6=1,V8=39,V11=122)
 ar=load(R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/RESULT.json');ap=load(R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/PREEXEC.json');obs=load(R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/OBJECT_OBSERVATIONS.json');o=ar['object'];p=Path(o['path']);s=p.stat();assert s.st_size==o['bytes']==6880 and o['SHA']=='480f8c785deb11c702c437ee81e97ace0e27a24ff0c2b362cd5031cb7cb46134'
 src=next(x for x in ap['input_pins']if x['path']==ap['argv'][-1]);reset=[x for x in obs['symbols']if x['name']=='Reset_Handler'];assert len(reset)==1 and reset[0]['defined_section_name']=='.text'
 inputs.append(dict(source_id=ar['source_id'],name=Path(src['path']).name,language='ASM',source_producer=src,object=o,stat_bytes=s.st_size,stat_mtime_ns=s.st_mtime_ns,producer_record_path=str(R/'MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/RESULT.json'),producer_record_status=ar['status'],original_C_ABI_gate_applied=False,link_ABI_qualified=False,payload_read_or_rehash=False,current_bytes_identity_NOT_verified=True))
 inputs.sort(key=lambda x:x['source_id']);assert[x['source_id']for x in inputs]==list(range(163));assert len({x['object']['path'].lower()for x in inputs})==163 and len({x['source_producer']['path'].lower()for x in inputs})==163
 review=load(R/'PH10_PARENT_SNAPSHOT_REVIEW_V1.json');libs=review['additional_existing_library_copy_producer_bindings'];assert len(libs)==2
 supplement=load(R/'MOD4_DEPLOYMENT_PORT_V1/SUPPLEMENT_RECEIPT.json')
 def dicts(v):
  if isinstance(v,dict):
   yield v
   for x in v.values():yield from dicts(x)
  elif isinstance(v,list):
   for x in v:yield from dicts(x)
 libraries=[]
 for row in libs:
  p=R/row['derived_relative'];st=p.stat();claims=[z for z in dicts(supplement)if z.get('member')==row['member']and z.get('copied_original_bytes')is True];assert len(claims)==1;z=claims[0]
  assert(st.st_size,row['bytes'],row['raw_producer_SHA'],row['CRC32'])==(z['bytes'],z['bytes'],z['raw_SHA'],z['CRC32'])
  libraries.append(dict(path=str(p),bytes=st.st_size,producer_SHA=z['raw_SHA'],member=z['member'],CRC32=z['CRC32'],stat_mtime_ns=st.st_mtime_ns,producer_copy_claim=claims[0],copy_receipt_path=str(R/'MOD4_DEPLOYMENT_PORT_V1/SUPPLEMENT_RECEIPT.json'),closure_binding_review_path=str(R/'PH10_PARENT_SNAPSHOT_REVIEW_V1.json'),current_payload_read_rehash_or_new_ABI_validation=False))
 registry=dict(status='MINIMUM_163_DISTINCT_PRODUCER_OBJECTS_AND_2_LIBS_STAT_ONLY_SAVED_BEFORE_DRAFT',objects=inputs,libraries=libraries,unique_source_ids=163,C162_ASM1=True,variant_counts=dict(V6main=1,V8=39,V11=122,V14ASM=1),payload_stat_checks=165,payload_reads=0,payload_hashes=0,not_single_uniform_build_or_latest_MOD4_firmware=True,native_query_only=query,Reset_Handler_saved_symbol=reset[0],startup_imports_saved=ar['undefined_global_or_weak'],current_payload_hash_identity_UNKNOWN=True)
 new('MINIMUM_INPUT_REGISTRY.json',registry)
 # Source excerpt only: no whole uvproj/filelist parse.
 with project.open(encoding='utf-8-sig')as f:head=list(itertools.islice(f,378))
 ranges=[(10,21),(51,52),(177,212),(244,253),(299,308),(360,376)];excerpt=''.join(f'{i}: {head[i-1]}'for a,b in ranges for i in range(a,b+1))
 for needle in('<Device>STM32F407IGHx</Device>','<Ir1Chk>1</Ir1Chk>','<Ir2Chk>0</Ir2Chk>','<Im1Chk>1</Im1Chk>','<useUlib>0</useUlib>','<noStLib>0</noStLib>','<ScatterFile></ScatterFile>'):
  assert needle in excerpt,needle
 with(D/'PROJECT_MEMORY_EXCERPT.txt').open('x',encoding='utf-8',newline='\n')as f:f.write(excerpt)
 memory=dict(project=str(project),project_source_SHA=sha(project),device='STM32F407IGHx',board_physical_map_not_independently_verified=True,toolset_requested='ARMCC5.06u4 build422; not installedu6 reproduction',selected_IROM1=dict(base='0x08000000',size='0x00100000',Im1Chk=1),selected_IRAM1=dict(base='0x20000000',size='0x00020000',Ir1Chk=1),listed_but_unselected_CCM_IRAM2=dict(base='0x10000000',size='0x00010000',Ir2Chk=0,hadIRAM2=1),useUlib=0,noStLib=0,umfTarg=1,useFile=0,explicit_ScatterFile='',IncludeLibsPath='',Misc='',OutputDirectory='mod4_port_stage1',OutputName='mod4_port_stage1_UNBOUND',old_generated_scatter_exists=True,old_scatter=str(oldscatter),old_scatter_not_explicit_current_target_assignment=True,current_target_generated_scatter_availability='UNKNOWN_NOT_GENERATED_OR_RUN_HERE',CCM_special_sections_and_copy_initialization='UNKNOWN; no automatic relocation to CCM',selection_not_hardware_binding=True)
 new('PROJECT_MEMORY_SELECTION.json',memory)
 scatter=D/'diagnostic_IROM1_IRAM1_DRAFT.sct'
 text='; UNEXECUTED V15 diagnostic draft from explicit project IROM1/IRAM1, not hardware map proof.\nLR_IROM1 0x08000000 0x00100000 {\n  ER_IROM1 0x08000000 0x00100000 {\n    *.o (RESET, +First)\n    *(InRoot$$Sections)\n    .ANY (+RO)\n  }\n  RW_IRAM1 0x20000000 0x00020000 {\n    .ANY (+RW +ZI)\n  }\n}\n'
 with scatter.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
 helptext=(D/'armlink_help.stdout.txt').read_text(encoding='utf-8')
 for opt in('--via','--output','--scatter','--entry','--map','--symbols','--xref','--info'):
  assert opt in helptext,opt
 out=D/'future_first_link001';assert not out.exists();out.mkdir()
 args=['--scatter',str(scatter),'--output',str(out/'old_BSP_diagnostic.axf'),'--entry','Reset_Handler','--map','--symbols','--xref','--info','sizes,totals,unused,veneers']+[x['object']['path']for x in inputs]+[x['path']for x in libraries]
 assert all(not any(c.isspace()for c in a)for a in args),'No unreviewed VIA quoting needed'
 via=D/'first_link_UNEXECUTED.via'
 with via.open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(args)+'\n')
 argv=[r'C:\Keil_v5\ARM\ARMCC\bin\armlink.exe','--via',str(via)]
 unknowns=['Current object/library byte hashes not verified; metadata+size are not current content certification','No one uniform clean build: mainV6,39C V8,122C V11,ASM V14; original gateFalse/capacity-stop remain','Installed linker5.06u6 differs project requested5.06u4; actual consumer ABI merging, library member contracts and FP/denormal consistency unknown','System libraries remain automatic installed armlink defaults, no --libpath override or guessed RT archive; selected RT path/member set/semihosting UNKNOWN until real link evidence','Explicit AHRS then DSP opaque user libs not disassembled/newly ABI validated; definitions/duplicates/cross-library scan behavior unknown','Old scatter generated artifact is not current target explicit assignment; new draft matches selected Flash1MiB/SRAM128KiB only, not physical board verification','CCMRAM listed but unselected; section demands, allocation, copy/ZI tables and SRAM/stack/heap overflow unknown','Saved startup STACK8192+HEAP8192 metadata not real runtime stack/heap requirement','Future map must check Reset_Handler/RESET vector address, ISR strong overrides, entry, undefined and removed code, libraries, veneers, copy regions and memory limits','Link success would not run SystemInit/CRT/RTOS or validate FPSCR/pins/CAN/Damiao mapping/control safety/physical standup/send transaction/HIL/WCET','VIA and scatter syntax drawn from own help and existing selected source artifact; native parsing of these new drafts unexecuted']
 new('FIRST_LINK_UNEXECUTED_DRAFT.json',dict(status='DRAFT_ONLY_NO_LINK_OR_ADMISSION_PERMISSION',argv=argv,expanded_literal_argv=[argv[0]]+args,cwd=str(D),via=meta(via),scatter=meta(scatter),owned_new_output_paths=dict(axf=str(out/'old_BSP_diagnostic.axf'),stdout=str(out/'link.stdout.txt'),stderr=str(out/'link.stderr.txt')),stdout_capture_policy='Capture map/symbols/xref/info in stdout file; --list not in captured own-help so deliberately omitted',object_order_source_ids=list(range(163)),explicit_libraries_order=[x['path']for x in libraries],system_library_policy='useUlib0/noStLib0; do not add microlib/no_scanlib/libpath assumptions; installed defaults unbound until link',section_removal_policy='Unchanged linker default; unused report not full input symbol validation; no override/suppress/force',unknowns=unknowns,first_link_executed=False))
 assert all(sha(Path(x['path']))==x['SHA']for x in before),'Small metadata/source changed during prep'
 new('SOURCE_INPUT_PINS.json',dict(files=before,all_before_after_equal=True,binary_obj_lib_payload_hashes=0,uvproj_read_mode='Only bounded first378 lines selected memory/LDads; no165-filelist reparse',old_scatter_unchanged=True))
 print(json.dumps(dict(status='STATIC_V15_REGISTRY_AND_COMPLETE_UNEXECUTED_LINK_DRAFT_SAVED',source_ids=len(inputs),objects_stat=163,libraries_stat=2,total_object_producer_bytes=sum(x['object']['bytes']for x in inputs),query_native=1,link_calls=0,project_memory=memory,unknown_count=len(unknowns))))
if __name__=='__main__':
 try:main()
 except BaseException:
  detail=traceback.format_exc();p=D/'PREPARATION_FAILURE.txt'
  if not p.exists():p.write_text(detail,encoding='utf-8')
  p=D/'PREPARATION_FAILURE_SOURCE.py'
  if not p.exists():p.write_bytes(Path(__file__).read_bytes())
  print(detail);raise
