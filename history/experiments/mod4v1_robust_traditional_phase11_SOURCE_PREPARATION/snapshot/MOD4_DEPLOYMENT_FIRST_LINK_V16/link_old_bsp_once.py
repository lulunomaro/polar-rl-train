"""First one-shot old BSP diagnostic link; generated image is never executed or flashed."""
from pathlib import Path
import hashlib,json,subprocess,time,struct,traceback,sys,re
D=Path(__file__).resolve().parent;R=D.parent;P=R/'MOD4_DEPLOYMENT_LINK_PREP_V15'
def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
a=load(D/'PARENT_FIRST_LINK_APPROVAL.json');assert a['approved'] is True
assert not (D/'ATTEMPT_STARTED.json').exists() and not (D/'CURRENT_INPUT_IDENTITIES.json').exists()
checks=[('registry_SHA','MINIMUM_INPUT_REGISTRY.json'),('draft_SHA','FIRST_LINK_UNEXECUTED_DRAFT.json'),('receipt_SHA','RECEIPT.json'),('scatter_SHA','diagnostic_IROM1_IRAM1_DRAFT.sct'),('help_SHA','armlink_help.stdout.txt')]
for key,name in checks:assert sha(P/name)==a[key],name
reg=load(P/'MINIMUM_INPUT_REGISTRY.json');old=load(P/'FIRST_LINK_UNEXECUTED_DRAFT.json');rec=load(P/'RECEIPT.json')
assert rec['status']=='COMPLETE_V15_STATIC_163OBJECT_2LIB_MEMORY_AND_OWNHELP_LINK_NOT_EXECUTED' and rec['ARM_native_invocations']['armlink_link']==0
assert [v['source_id']for v in reg['objects']]==list(range(163)) and len(reg['libraries'])==2
objects=[v['object']for v in reg['objects']];libs=[dict(path=v['path'],bytes=v['bytes'],SHA=v['producer_SHA'])for v in reg['libraries']]
records=objects+libs;assert len({str(Path(v['path']).resolve()).casefold()for v in records})==165
out=D/'old_BSP_stage1_UNBOUND_diagnostic.axf';assert not out.exists()
args=old['expanded_literal_argv'].copy();oi=args.index('--output')+1;args[oi]=str(out)
expected=[r'C:\Keil_v5\ARM\ARMCC\bin\armlink.exe','--scatter',str(P/'diagnostic_IROM1_IRAM1_DRAFT.sct'),'--output',str(out),'--entry','Reset_Handler','--map','--symbols','--xref','--info','sizes,totals,unused,veneers']+[v['path']for v in records]
assert args==expected and len(args)==177 and Path(old['cwd'])==P and old['first_link_executed']is False
inverse=args.copy();inverse[oi]=old['expanded_literal_argv'][oi];assert inverse==old['expanded_literal_argv']
assert len(subprocess.list2cmdline(args))<32760
pins=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))for p in[Path(__file__).resolve(),D/'PARENT_FIRST_LINK_APPROVAL.json']+[P/name for _,name in checks]]
identities=[]
for v in records:
    p=Path(v['path']).resolve();assert p.is_relative_to(R.resolve()) and re.fullmatch('[0-9a-f]{64}',v['SHA'])
    before=p.stat();assert before.st_size==v['bytes'];digest=hashlib.sha256()
    with p.open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    after=p.stat();actual=digest.hexdigest()
    assert actual==v['SHA'] and (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),str(p)
    identities.append(dict(path=str(p),bytes=after.st_size,SHA=actual,stat_mtime_ns=after.st_mtime_ns,matched_producer=True,hash_for_first_link_integrity_not_archive=True))
dump(D/'CURRENT_INPUT_IDENTITIES.json',dict(objects=163,opaque_user_libs=2,total_bytes=sum(v['bytes']for v in identities),current_payload_hashes=165,one_payload_hash_per_input=True,records=identities))
dump(D/'PREEXEC.json',dict(argv=args,cwd=str(P),direct_expanded_argv_not_VIA=True,output_only_argv_inverse_exact=True,small_pins=pins,input_identities=str(D/'CURRENT_INPUT_IDENTITIES.json'),no_mismatch_override_or_librarypath_guess=True,max_link_calls=1,no_execution_or_flash=True))
dump(D/'ATTEMPT_STARTED.json',dict(wall_start=time.time(),link_invocation_started=True,no_retry=True,argv=args,cwd=str(P)))
started=time.perf_counter()
try:
    with (D/'link.stdout.txt').open('xb')as so,(D/'link.stderr.txt').open('xb')as se:
        run=subprocess.run(args,cwd=str(P),stdin=subprocess.DEVNULL,stdout=so,stderr=se,timeout=90,check=False)
    native=dict(link_calls=1,returncode=run.returncode,wall_s=time.perf_counter()-started,output_present=out.is_file(),output_bytes=out.stat().st_size if out.is_file()else None,compile_ASM_fromelf_armar_query_UV_flash_realIO_PHY_oldQA_Git_calls=0)
    dump(D/'NATIVE_RESULT.json',native)
    log=(D/'link.stdout.txt').read_text(encoding='utf-8',errors='replace')+'\n'+(D/'link.stderr.txt').read_text(encoding='utf-8',errors='replace')
    diagnostics=re.findall(r'(?m)^\s*(?:Warning|Error|Fatal):[^\r\n]*',log)
    poststat=all((Path(v['path']).stat().st_size,Path(v['path']).stat().st_mtime_ns)==(v['bytes'],v['stat_mtime_ns'])for v in identities)
    assert poststat and all(sha(Path(v['path']))==v['SHA']for v in pins),'inputs or small pins drift; preserve native result'
    result=dict(status='FIRST_LINK_NONZERO_PRESERVED' if run.returncode else 'FIRST_LINK_SUCCESS_IMAGE_METADATA_PENDING',**native,input_current_SHA_matched165=True,inputs_poststat_unchanged=True,small_pins_before_after_equal=True,diagnostic_lines=diagnostics,
        output_is_old_BSP_stage1_UNBOUND=True,latest_MOD4_C3_startup_integration=False,full_hardware_firmware_qualified=False,source_flags_libraries_memory_unmodified=True,no_auto_retry=True,PH11pending=True)
    if run.returncode==0:
        assert out.is_file() and 52<=out.stat().st_size<=8388608,'missing or out-of-cap successful image'
        data=out.read_bytes();assert data[:6]==b'\x7fELF\x01\x01'
        h=struct.unpack_from('<16sHHIIIIIHHHHHH',data);assert h[1]==2 and h[2]==40 and h[8]==52 and h[9]==32 and 0<h[10]<=128 and h[5]+32*h[10]<=len(data)
        segments=[];vectors=None
        for i in range(h[10]):
            s=struct.unpack_from('<8I',data,h[5]+32*i);typ,offset,va,pa,fs,ms,flags,align=s
            assert offset+fs<=len(data)
            segments.append(dict(type=typ,file_offset=offset,virtual_address=va,physical_address=pa,file_bytes=fs,memory_bytes=ms,flags=flags,alignment=align))
            if typ==1 and va==0x08000000 and fs>=8:
                sp,reset=struct.unpack_from('<II',data,offset);vectors=dict(address=va,initial_SP=sp,reset_word=reset,SP_8_aligned=sp%8==0,SP_in_selected_SRAM=0x20000000<=sp<=0x20020000,reset_Thumb_bit=bool(reset&1),reset_in_selected_Flash=0x08000000<=(reset&~1)<0x08100000,entry_equals_reset_word=h[4]==reset)
        image=dict(path=str(out),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),ELF_type=h[1],ELF_machine=h[2],entry=h[4],ELF_flags=h[7],program_segments=segments,first_flash_vector_words=vectors,image_file_read_snapshots=1,file_bytes_NOT_ROM_RAM_usage=True,basic_new_image_observation_not_full_parser_qualification=True)
        dump(D/'IMAGE_BASIC_OBSERVATIONS.json',image)
        result.update(status='LINKED_OLD_BSP_STAGE1_DIAGNOSTIC_NOT_LATEST_MOD4_OR_HARDWARE_QUALIFIED',image=image)
    dump(D/'RESULT.json',result)
    lines=['# V16：旧BSP/Stage1首次诊断链接',f'- 实际LINK调用1，rc={run.returncode}，输出存在={out.is_file()}；完整stdout/stderr保留。',
        '- 输入163独立obj＋两opaque库在本次firstlink前各核当前SHA一次匹配producer；用途为真实link完整性，非归档重复hash。poststat及小pins前后相同。',
        '- reviewed expanded argv直接传入，仅新output字符串替换；原order/flags/scatter/cwd/defaultRT未改。无VIA执行、重编译、抑制diagnostic、ABI/region覆盖或CCM搬移。',
        '- Flash1MiB/SRAM128KiB来自源项目显式选择，非physicalboard绑定。旧V6/V8历史gate/cap记录保持原状；不是单次cleanbuild。',
        '- 新映像若成功仅基本ELF/LOADsegments/vector元数据观察，文件大小不是ROM/RAM占用；map/runtime/IRQ覆盖/库成员/semihosting/完整ABI/FPSCR/RTOS/WCET/实机需分项核。',
        '- 保留旧机mechanicalcontrol/MF9025接口，MOD4绑定默认UNBOUND；这不是C3＋新startup技能一体化镜像或可刷机资格。映像未启动，库算法未调用，无flash/realIO/PHY/旧QA/Git。',
        f'- 提取的link diagnostic行数={len(diagnostics)}；源日志优先，不自动link重试；全部PH11pending。']
    with (D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps(result,indent=2))
    sys.exit(run.returncode)
except SystemExit:
    raise
except BaseException:
    dump(D/'ERROR.json',dict(error=traceback.format_exc(),native_prefix=str(D/'NATIVE_RESULT.json'),link_attempt_started=True,no_retry=True))
    raise
