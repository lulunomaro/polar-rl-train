"""Read existing ELF objects/macros/attributes; no compile/link/run calls."""
from pathlib import Path
import csv,hashlib,json,re,struct
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inspect(p):
    raw=p.read_bytes();assert raw[:7]==b'\x7fELF\x01\x01\x01'
    e=struct.unpack_from('<16sHHIIIIIHHHHHH',raw,0);assert e[1]==1 and e[2]==40
    shoff,shsize,shnum,shstr=e[6],e[11],e[12],e[13];assert shsize==40
    sec=[struct.unpack_from('<10I',raw,shoff+i*shsize)for i in range(shnum)]
    stringsec=sec[shstr];strings=raw[stringsec[4]:stringsec[4]+stringsec[5]]
    def text(buf,i):return buf[i:buf.index(b'\0',i)].decode('ascii')
    writable=[];undef=[]
    for s in sec:
        name=text(strings,s[0])
        if s[2]&1 and s[5]:writable.append(dict(name=name,bytes=s[5],section_type=s[1]))
        if s[1]==2:
            st=sec[s[6]];names=raw[st[4]:st[4]+st[5]];assert s[9]==16
            for off in range(s[4],s[4]+s[5],16):
                sn,_,_,_,_,ndx=struct.unpack_from('<IIIBBH',raw,off)
                if sn and ndx==0:undef.append(text(names,sn))
    return dict(ELF_class=32,little_endian=True,type='ET_REL',machine='EM_ARM',writable_allocated_sections=writable,undefined_symbols=sorted(set(undef)),e_flags=e[7])
def main():
    report=json.loads((HERE/'ARM_BUILD_01.json').read_bytes());assert report['success']and len(report['objects'])==2
    records=[]
    for old in report['objects']:
        p=Path(old['object']);assert sha(p)==old['sha256']and p.stat().st_size==old['bytes']
        folder=p.parent;macro=(folder/'target_macros.log').read_text();attributes=(folder/'fromelf.log').read_text()
        m=dict(re.findall(r'^#define\s+(\w+)\s+(.+)$',macro,re.M));wanted={k:m[k]for k in ('__ARM_ARCH','__ARM_ARCH_7EM__','__ARM_FP','__ARM_PCS_VFP','__DBL_MANT_DIG__','__SIZEOF_DOUBLE__','__FLT_EVAL_METHOD__','__THUMBEL__')}
        assert wanted=={'__ARM_ARCH':'7','__ARM_ARCH_7EM__':'1','__ARM_FP':'0x6','__ARM_PCS_VFP':'1','__DBL_MANT_DIG__':'53','__SIZEOF_DOUBLE__':'8','__FLT_EVAL_METHOD__':'0','__THUMBEL__':'1'}
        attrs=[s.strip()for s in attributes.splitlines()if 'Tag_'in s]
        assert any('Tag_CPU_arch = ARM v7E-M (=13)'in s for s in attrs)
        assert any('Tag_ABI_HardFP_use'in s and'(=1)'in s for s in attrs)
        assert any('Tag_ABI_VFP_args'in s and'(=1)'in s for s in attrs)
        binary=inspect(p);assert not binary['writable_allocated_sections']
        records.append(dict(**old,**binary,macros=wanted,attributes=attrs,target_execution=0,BSP_link=False,helper_libm_binding=False,FPSCR_gradual_underflow_verified=False,stack_or_WCET=False))
    result=dict(kind='ACTUAL_NEW_OBJECT_BYTE_MACRO_AND_ATTRIBUTE_FACTS',objects=records,SP_hard_ABI_is_not_SP_only_arithmetic=True)
    with(HERE/'OBJECT_SUMMARY.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
    with(HERE/'OBJECT_SUMMARY.csv').open('x',newline='',encoding='utf-8')as f:
        writer=csv.DictWriter(f,fieldnames=['target','bytes','sha256','source_SHA','ELF_class','type','machine','target_execution']);writer.writeheader()
        for row in records:writer.writerow({k:row[k]for k in writer.fieldnames})
    print(json.dumps(dict(objects=len(records),undefined_symbols=records[0]['undefined_symbols'],writable_sections=records[0]['writable_allocated_sections'],ARM_execution=0),indent=2))
if __name__=='__main__':main()
