"""Read ELF32 header/section-header/AEABI build attributes only; no code/disassembly."""
import struct,hashlib
NAMES={4:'CPU_raw_name',5:'CPU_name',6:'CPU_arch',7:'CPU_arch_profile',8:'ARM_ISA_use',9:'THUMB_ISA_use',10:'FP_arch',18:'ABI_Wchar_t',20:'ABI_FP_denormal',26:'ABI_enum_size',27:'ABI_HardFP_use',28:'ABI_VFP_args',64:'nodefaults',67:'conformance'}
def inspect(path):
 b=path.read_bytes();assert b[:4]==b'\x7fELF'and b[4]==1 and b[5]==1
 h=struct.unpack_from('<16sHHIIIIIHHHHHH',b);assert h[11]==40 and h[12]>0 and h[6]+40*h[12]<=len(b)
 sections=[struct.unpack_from('<10I',b,h[6]+40*i)for i in range(h[12])];st=sections[h[13]];names=b[st[4]:st[4]+st[5]]
 def cstr(data,pos,end):
  stop=data.index(0,pos,end);return data[pos:stop].decode('ascii',errors='replace'),stop+1
 def uleb(data,pos,end):
  result=0;shift=0
  while pos<end:
   v=data[pos];pos+=1;result|=(v&127)<<shift
   if not(v&128):return result,pos
   shift+=7;assert shift<=63
  raise ValueError('Truncated ULEB attribute')
 scopes=[];all_names=[]
 for sh in sections:
  name=cstr(names,sh[0],len(names))[0]if names and sh[0]<len(names)else'';all_names.append(name)
  if name!='.ARM.attributes':continue
  data=b[sh[4]:sh[4]+sh[5]];assert data[:1]==b'A';p=1
  while p<len(data):
   start=p;size=struct.unpack_from('<I',data,p)[0];end=start+size;assert size>=5 and end<=len(data);vendor,p=cstr(data,p+4,end)
   if vendor!='aeabi':p=end;continue
   while p<end:
    sub=p;kind,p=uleb(data,p,end);length=struct.unpack_from('<I',data,p)[0];p+=4;se=sub+length;assert se<=end and se>=p
    if kind!=1:p=se;continue
    tags={}
    while p<se:
     tag,p=uleb(data,p,se)
     if tag in (4,5,67)or(tag>32 and tag%2==1):v,p=cstr(data,p,se)
     elif tag==32:
      v,p=uleb(data,p,se);s,p=cstr(data,p,se);v=dict(value=v,text=s)
     else:v,p=uleb(data,p,se)
     tags[str(tag)]=v
    scopes.append(dict(vendor=vendor,scope='FILE',tags=tags,named={NAMES.get(int(k),'Tag_'+k):v for k,v in tags.items()}))
   p=end
 merged={}
 for x in scopes:
  for k,v in x['tags'].items():
   if k in merged:assert merged[k]==v
   merged[k]=v
 return dict(bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),ELF_class=b[4],ELF_data=b[5],ELF_type=h[1],ELF_machine=h[2],ELF_flags=h[7],section_names=all_names,AEABI_file_scopes=scopes,merged_tags=merged,no_code_disassembly_or_symbol_dump=True)
