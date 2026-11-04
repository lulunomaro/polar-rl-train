"""Six NEW synthetic ELF capacity-boundary blobs. Metadata only, never ARM execution."""
import struct

def uleb(v):
 out=bytearray()
 while True:
  b=v&127;v>>=7;out.append(b|(128 if v else 0))
  if not v:return bytes(out)

def block(kind,ids,values):
 body=(b''.join(uleb(i) for i in ids)+b'\0') if kind!=1 else b''
 body+=b''.join(uleb(k)+uleb(v) for k,v in values)
 return uleb(kind)+struct.pack('<I',5+len(body))+body

def make_elf(section_count=4,symbol_count=0,padded_bytes=None):
 assert 4<=section_count<65535 and (not symbol_count or section_count>=5)
 names=b'\0.text\0.shstrtab\0.ARM.attributes\0.symtab\0.extra\0'
 public=block(1,[],[(18,2),(26,1)])
 if symbol_count:public+=block(3,[symbol_count-1],[(18,2),(26,1)])
 attrs=b'A'+struct.pack('<I',4+6+len(public))+b'aeabi\0'+public
 blob=bytearray(52)
 def put(b,align=1):
  blob.extend(b'\0'*((-len(blob))%align));off=len(blob);blob.extend(b);return off
 text_off=put(b'\x00\xbf',2);str_off=put(names);attr_off=put(attrs,4)
 sym_off=None
 if symbol_count:
  syms=bytearray(16*symbol_count)
  struct.pack_into('<H',syms,16*(symbol_count-1)+14,1)  # Last symbol defined in .text.
  sym_off=put(syms,4)
 blob.extend(b'\0'*((-len(blob))%4));shoff=len(blob)
 def row(name,kind,flags,off,size,link=0,info=0,align=1,entsize=0):
  return (names.index(name.encode()+b'\0') if name else 0,kind,flags,0,off,size,link,info,align,entsize)
 rows=[(0,)*10,row('.text',1,6,text_off,2,align=2),row('.shstrtab',3,0,str_off,len(names)),row('.ARM.attributes',0x70000003,0,attr_off,len(attrs))]
 if symbol_count:rows.append(row('.symtab',2,0,sym_off,16*symbol_count,2,symbol_count,4,16))
 rows.extend(row('.extra',1,0,attr_off+len(attrs),0) for _ in range(section_count-len(rows)))
 for s in rows:blob.extend(struct.pack('<10I',*s))
 ident=b'\x7fELF\x01\x01\x01'+b'\0'*9
 struct.pack_into('<16sHHIIIIIHHHHHH',blob,0,ident,1,40,1,0,0,shoff,0x05000000,52,0,0,40,section_count,2)
 if padded_bytes is not None:
  assert padded_bytes>=len(blob);blob.extend(b'\0'*(padded_bytes-len(blob)))
 # Structural construction checks only; these DO NOT call any scoped reader.
 assert shoff+40*section_count<=len(blob)
 for s in rows:assert s[4]+s[5]<=len(blob)
 assert rows[2][1]==3 and rows[3][1]==0x70000003
 return bytes(blob),dict(section_count=section_count,symbol_count_including_null=symbol_count,public_SYMBOL_scope_present=bool(symbol_count),section_table_end=shoff+40*section_count,valid_backing_bounds=True,tail_padding_bytes=len(blob)-(shoff+40*section_count))

def fixture_cases():
 specs=[
  ('01_object_at_1048576',dict(padded_bytes=1048576),True,None),
  ('02_object_above_1048576',dict(padded_bytes=1048577),False,'ELF object size outside supported bounds'),
  ('03_sections_at_4096',dict(section_count=4096),True,None),
  ('04_sections_above_4096',dict(section_count=4097),False,'unsupported extended/invalid section indices'),
  ('05_symbols_at_16384',dict(section_count=5,symbol_count=16384),True,None),
  ('06_symbols_above_16384',dict(section_count=5,symbol_count=16385),False,'symbol-table bounds')]
 cases=[]
 for name,params,positive,message in specs:
  blob,shape=make_elf(**params)
  cases.append(dict(name=name,blob=blob,positive=positive,expected_error=message,construction=shape))
 return cases
