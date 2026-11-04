"""First sole startup ASM diagnostic; no link, C/old-object read, firmware execution or retry."""
from pathlib import Path
import hashlib,json,subprocess,time,importlib.util,struct,traceback
D=Path(__file__).resolve().parent;R=D.parent;P=R/'MOD4_DEPLOYMENT_ARMASM_PREP_V13'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(p):return json.loads(p.read_bytes())
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
assert not (D/'ATTEMPT_STARTED.json').exists()
a=get(D/'PARENT_FIRST_ASM_APPROVAL.json');assert a['approved'] is True
f=P/'V14_LITERAL_DRAFT_UNEXECUTED_01.json';assert sha(f)==a['draft_SHA']=='6257cddd1a62fa22859b0fa537d43f0391781705bcbacf8f9532f09072321e9f'
x=get(f);args=x['argv'];src=Path(x['input_source']['path']);obj=Path(x['output_object']);reader=R/'MOD4_DEPLOYMENT_SCOPED_READER_V10/scoped_attrs_v10.py'
assert args==[r'C:\Keil_v5\ARM\ARMCC\bin\armasm.exe','--cpu=Cortex-M4.fp.sp','--li','-o',str(obj),str(src)]
assert obj==D/'objects/000_startup_stm32f407xx.s.o' and Path(x['cwd'])==src.parent and not obj.exists()
assert src.stat().st_size==30149 and sha(src)==a['original_source_SHA']=='7baf21c802efd7aaeace20cfecef16b967d124fcbd5f038088be0eee6138b261'
assert sha(reader)==a['sealed_reader_SHA']=='0a6437d1e5e3c56961547e3c3758a651a4c9e8ad36aeba7b1f1e71b282f522d0'
assert sha(P/'PRIMARY_ABI_RULES_01.json')=='4cfb79efe4243d822fbf1bf14652be3dcddcdb44689d4c019711f96a0471a8a5'
pins=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))for p in(Path(__file__).resolve(),D/'PARENT_FIRST_ASM_APPROVAL.json',f,src,reader,P/'PRIMARY_ABI_RULES_01.json')]
obj.parent.mkdir(exist_ok=False)
dump(D/'PREEXEC.json',dict(argv=args,cwd=x['cwd'],input_pins=pins,diagnostic_no_APCS_FPU_override=True,no_old_UV_or_C_PCS_equivalence_claim=True,max_native_assembly=1,max_object_read_snapshots=1,no_link=True))
dump(D/'ATTEMPT_STARTED.json',dict(ASM_source_id=0,invocation_started=True,argv=args,cwd=x['cwd'],wall_start=time.time(),no_automatic_retry=True))
started=time.perf_counter()
try:
    with (D/'armasm_stdout.log').open('xb')as so,(D/'armasm_stderr.log').open('xb')as se:
        run=subprocess.run(args,cwd=x['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se,timeout=60,check=False)
    native=dict(ASM_calls=1,returncode=run.returncode,wall_s=time.perf_counter()-started,object_present=obj.is_file(),source_SHA_after=sha(src),other_ARM_calls=0,link_calls=0,old_C_library_objects_read=0,PHY_oldQA_Git_calls=0)
    dump(D/'NATIVE_RESULT.json',native)
    assert run.returncode==0 and obj.is_file() and obj.stat().st_size>0,'first ASM failed or missing nonempty object; preserve and stop'
    assert native['source_SHA_after']==a['original_source_SHA'],'source drift; preserve successful native prefix'
    raw=obj.read_bytes();object_sha=hashlib.sha256(raw).hexdigest()
    spec=importlib.util.spec_from_file_location('sealed_v10_metadata_only',reader);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    observed=mod.inspect_elf(raw);attrs=observed.pop('attributes')
    observed['public_scopes']=[dict(scope_kind=k[0],scope_id=k[1],**v)for k,v in sorted(attrs.scopes.items())]
    observed['FILE_effective']={str(t):attrs.effective(t,('FILE',0))for t in(6,7,8,9,10,18,24,25,26,27,28,64)}
    observed['code_ABI_observations']=[dict(section_id=s['id'],section_name=s['name'],effective={str(t):attrs.effective(t,('SECTION',s['id']))for t in(6,7,9,10,18,24,25,26,27,28)})for s in observed['code_sections']]
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',raw);sections=[struct.unpack_from('<10I',raw,h[6]+40*i)for i in range(h[12])]
    names={s['id']:s['name']for s in observed['sections_metadata']};symtabs={};symbols=[]
    for i,s in enumerate(sections):
        if s[1]!=2:continue
        assert s[9]==16 and s[5]%16==0 and s[5]//16<=16384 and 0<s[6]<len(sections)
        st=sections[s[6]];assert st[1]==3;strings=raw[st[4]:st[4]+st[5]];table=[]
        for j in range(s[5]//16):
            n,value,size,info,other,shndx=struct.unpack_from('<IIIBBH',raw,s[4]+16*j);text,_=mod.ntbs(strings,n,len(strings));name=mod.ascii_name(text,'symbol name')
            row=dict(table_section=i,index=j,name=name,value=value,size=size,bind=info>>4,type=info&15,other=other,defined_section=shndx,defined_section_name=names.get(shndx))
            table.append(row);symbols.append(row)
        symtabs[i]=table
    relocations=[]
    for i,s in enumerate(sections):
        if s[1]not in(4,9):continue
        step=12 if s[1]==4 else 8;assert s[9]==step and s[5]%step==0 and s[6]in symtabs and s[7]<len(sections)
        for j in range(s[5]//step):
            offset,info=struct.unpack_from('<II',raw,s[4]+step*j);si=info>>8;assert si<len(symtabs[s[6]])
            row=dict(relocation_section=i,target_section=s[7],target_section_name=names[s[7]],offset=offset,type=info&255,symbol_index=si,symbol_name=symtabs[s[6]][si]['name'])
            if s[1]==4:row['addend']=struct.unpack_from('<i',raw,s[4]+step*j+8)[0]
            relocations.append(row)
    observed.update(symbols=symbols,relocations=relocations,weak_symbol_count=sum(s['bind']==2 for s in symbols),undefined_global_or_weak=[s['name']for s in symbols if s['defined_section']==0 and s['bind']in(1,2)],
        object=dict(path=str(obj),bytes=len(raw),SHA=object_sha),new_object_file_read_snapshots=1,sealed_V10_metadata_inspections=1,C_specific_FP_gate_applied=False,ASM_link_ABI_qualified=False,
        ET_REL_flags_not_used_as_public_FP_PCS_certificate=True,scope_zero_meanings_reference=str(P/'PRIMARY_ABI_RULES_01.json'))
    dump(D/'OBJECT_OBSERVATIONS.json',observed)
    assert all(sha(Path(v['path']))==v['SHA']for v in pins),'input source/reader/approval drift'
    result=dict(status='ASSEMBLED_FIRST_STARTUP_DIAGNOSTIC_METADATA_OBSERVED_NOT_LINK_QUALIFIED',ASM_calls=1,ASM_success=1,source_id=0,
        object=observed['object'],section_count=observed['section_count'],code_sections=len(observed['code_sections']),weak_symbol_count=observed['weak_symbol_count'],symbol_count=len(symbols),relocation_count=len(relocations),
        FILE_effective_values={k:v['value']for k,v in observed['FILE_effective'].items()},undefined_global_or_weak=observed['undefined_global_or_weak'],new_object_file_read_snapshots=1,
        symbol_and_relocation_metadata_from_same_owned_bytes=True,all_inputs_before_after_equal=True,no_old_ledger_rewrite=True,C_specific_FP_gate_applied=False,link_ABI_qualified=False,
        ARMCC_fromelf_query_version_probe_link_UV_flash_realIO_PHY_oldQA_Git_calls=0,PH11pending=True)
    dump(D/'RESULT.json',result)
    lines=['# V14：唯一startup首次诊断汇编与新物件元数据',f'- 实际一次ARMASM rc0；source id0保持原30149B SHA；新object {len(raw)}B / {object_sha}。',
        '- 采用C13已核CPU Cortex-M4.fp.sp、--li、新-o；无APCS/FPUoverride、无__MICROLIB定义、无新-I/宏/source改写。不是旧UV数值selector精确复现。',
        f'- ELF32LE/ARM ET_REL；sections={observed["section_count"]}，code={len(observed["code_sections"])}，symbols={len(symbols)}，weak={observed["weak_symbol_count"]}，relocations={len(relocations)}。',
        '- FILE有效tag值：'+json.dumps(result['FILE_effective_values'],sort_keys=True)+'；详细scope/provenance另存。',
        '- tag10/27/28/24/25按C13精确含义分别观察；不将0泛作UNUSED或从ET_REL flags推断hardFP。18/26规范0仍为typeUNUSED。',
        '- 未套C浮点gate；当前仅汇编成功及scope原始元数据，C/lib PCS/merge/链接、强IRQ覆盖、地址、stackheap充足、FPSCR/WCET/实机均待核。',
        '- undefined global/weak：'+', '.join(observed['undefined_global_or_weak'])+'；导入不是已解析链接。',
        '- ONE新object文件读snapshot/SHA；sealedV10 inspect1；symbol/relocation均用同ownedbytes。六输入before-after匹配，无162Cobjects/库读取、旧test重放、fromelf/ARMCC/query/link/flash/PHY/Git。',
        '- 旧C11仍保留其当时ASM未启动记录；新V14补独立id0object，163个source已有分段compile/assemble记录不等单次完整firmware。全部PH11pending，不自动link或重跑。']
    with (D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as out:out.write('\n'.join(lines)+'\n')
    print(json.dumps(result,indent=2))
except BaseException:
    dump(D/'ERROR.json',dict(error=traceback.format_exc(),ASM_attempt_started=True,no_retry=True,object_present=obj.is_file(),success_prefix_file=str(D/'NATIVE_RESULT.json'),no_link=True))
    raise
