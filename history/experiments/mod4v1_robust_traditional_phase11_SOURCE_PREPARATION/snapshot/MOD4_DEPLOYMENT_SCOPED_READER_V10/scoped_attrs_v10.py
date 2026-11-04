"""Bounded static ELF32LE/AEABI FILE->SECTION->SYMBOL metadata reader.
Honors Arm Addenda32 2026Q3 rules; never executes an object or an ARM tool.
This is an intentionally bounded reader, not a general ELF/linker implementation.
"""
import struct

MAX_OBJECT=1048576
MAX_SECTIONS=4096
MAX_VENDORS=32
MAX_BLOCKS=128
MAX_PAIRS=2048
MAX_IDS=256
KNOWN_MANDATORY=set(range(4,33))|{34,36,38,42,44,46,48,50,52}

class ParseError(ValueError):
    pass

class ScopeConflict(ParseError):
    pass

def need(condition, text):
    if not condition:
        raise ParseError(text)

def u32(data, pos, end):
    need(0<=pos and pos+4<=end<=len(data), 'truncated uint32')
    return struct.unpack_from('<I',data,pos)[0]

def uleb(data, pos, end):
    value=0
    for k in range(5):
        need(0<=pos<end<=len(data),'truncated ULEB32 within declared scope')
        byte=data[pos];pos+=1
        need(k<4 or byte<16,'ULEB32 overflow/continuation exceeds five bytes')
        value|=(byte&127)<<(7*k)
        if not (byte&128):
            return value,pos
    raise ParseError('ULEB32 has no terminator')

def ntbs(data,pos,end):
    need(0<=pos<=end<=len(data),'NTBS bounds')
    finish=data.find(b'\0',pos,end)
    need(finish>=0,'unterminated NTBS within declared scope')
    return data[pos:finish],finish+1

def ascii_name(data, label):
    try:
        return data.decode('ascii')
    except UnicodeDecodeError as exc:
        raise ParseError('unsupported non-ASCII '+label) from exc

def label(key):
    return 'FILE' if key[0]=='FILE' else key[0]+'#'+str(key[1])

class PublicAttributes:
    def __init__(self, sections, symbol_sections=None):
        self.section_ids=set(sections)
        self.symbol_sections={} if symbol_sections is None else dict(symbol_sections)
        self.scopes={}
        self.raw_public_blocks=[]
        self.vendor_blocks=[]
        self.symbol_ids=set()
        self.pair_count=0

    def merge(self,key,tag,value,origin):
        scope=self.scopes.setdefault(key,{'tags':{},'origins':{}})
        if tag in scope['tags'] and scope['tags'][tag]!=value:
            raise ScopeConflict('different explicit values in same '+label(key)+' for tag '+str(tag))
        scope['tags'][tag]=value
        scope['origins'].setdefault(tag,[]).append(origin)

    def parent(self,key):
        if key[0]=='FILE':
            return None
        if key[0]=='SECTION':
            return ('FILE',0)
        need(key[1] in self.symbol_sections,'SYMBOL has no validated defining section')
        return ('SECTION',self.symbol_sections[key[1]])

    def scope(self,key):
        return self.scopes.get(key,{'tags':{},'origins':{}})

    def effective(self,tag,key):
        if key is None:
            default='' if tag in (4,5) or (tag>32 and tag&1) else 0
            if tag==32:
                default={'flag':0,'vendor':''}
            return {'value':default,'origin_kind':('NORMATIVE_PUBLIC_DEFAULT_ZERO' if default==0 else 'NORMATIVE_PUBLIC_DEFAULT_EMPTY'),'origin_scope':'FILE.parent','origin_records':[],'path':[]}
        current=self.scope(key)
        par=self.parent(key)
        empty=not any(t!=64 for t in current['tags'])
        if empty and par is not None and 64 in self.scope(par)['tags']:
            return {'value':None,'origin_kind':'NODEFAULTS_UNDEFINED','origin_scope':label(par),'origin_records':self.scope(par)['origins'][64],'path':[label(key)],'empty_scope_rule_applied':True}
        if tag in current['tags']:
            return {'value':current['tags'][tag],'origin_kind':'EXPLICIT_ATTRIBUTE','origin_scope':label(key),'origin_records':current['origins'][tag],'path':[label(key)]}
        result=self.effective(tag,par)
        return dict(result,path=[label(key)]+result['path'])

    def typed(self,tag,key):
        result=self.effective(tag,key)
        value=result['value']
        if value is None:
            state='UNKNOWN';meaning='UNDEFINED_BY_NODEFAULTS_EMPTY_SCOPE_RULE'
        elif value==0:
            state='UNUSED';meaning='ABI_CONTRACT_PROHIBITS_'+('WCHAR_T' if tag==18 else 'ENUM_USE')
        elif tag==18 and value in (2,4):
            state='VALUE';meaning='WCHAR_T_BYTES_'+str(value)
        elif tag==26 and value in (1,2,3):
            state='VALUE';meaning={1:'ENUM_SMALLEST_CONTAINER',2:'ENUM_CONTAINERS_32_BIT',3:'ABI_VISIBLE_ENUMS_NEED_32_BITS_OTHERS_CONTAINERIZED'}[value]
        else:
            state='UNKNOWN';meaning='UNSUPPORTED_OR_RESERVED_PUBLIC_VALUE'
        return dict(result,classification=state,meaning=meaning)

    def rows(self,sections):
        rows=[]
        for s in sections:
            if not s['flags']&4:
                continue
            key=('SECTION',s['id'])
            exceptions=[]
            for sym in sorted(self.symbol_ids):
                if self.symbol_sections.get(sym)==s['id']:
                    exceptions.append({'symbol_id':sym,'defined_section_id':s['id'],'tag18':self.typed(18,('SYMBOL',sym)),'tag26':self.typed(26,('SYMBOL',sym))})
            rows.append(dict(s,flags_hex='0x%08x'%s['flags'],tag18=self.typed(18,key),tag26=self.typed(26,key),symbol_scope_exceptions=exceptions))
        return rows


def parse_attributes(data,section_ids,symbol_sections=None,file_offset=0):
    need(1<=len(data)<=MAX_OBJECT,'attribute region size')
    need(data[0]==0x41,'attribute format is not A')
    public=PublicAttributes(section_ids,symbol_sections)
    pos=1
    while pos<len(data):
        need(len(public.vendor_blocks)<MAX_VENDORS,'vendor count limit')
        start=pos
        size=u32(data,start,len(data));end=start+size
        need(size>=5 and end<=len(data),'vendor length exceeds attribute region')
        vendor_raw,pos=ntbs(data,start+4,end)
        vendor=ascii_name(vendor_raw,'vendor name')
        public.vendor_blocks.append({'vendor':vendor,'file_offset':file_offset+start,'bytes':size,'payload_bytes':end-pos,'public':vendor=='aeabi','private_payload_interpreted':False})
        if vendor!='aeabi':
            pos=end
            continue
        while pos<end:
            need(len(public.raw_public_blocks)<MAX_BLOCKS,'public block limit')
            sub=pos
            kind,pos=uleb(data,pos,end)
            length=u32(data,pos,end);pos+=4;stop=sub+length
            need(stop>=pos and stop<=end,'public block length exceeds vendor boundary')
            need(kind in (1,2,3),'unsupported public scope kind')
            ids=[]
            if kind!=1:
                while True:
                    index,pos=uleb(data,pos,stop)
                    if index==0:
                        break
                    need(len(ids)<MAX_IDS,'index list limit')
                    if kind==2:
                        need(index in public.section_ids and index!=0,'invalid SECTION index')
                    ids.append(index)
                need(bool(ids),'empty index list is not supported')
            if kind==3:
                public.symbol_ids.update(ids)
            values=[]
            while pos<stop:
                origin=file_offset+pos
                tag,pos=uleb(data,pos,stop)
                need(tag>=4,'unsupported/reserved public attribute tag below four')
                if tag<64 and tag not in KNOWN_MANDATORY:
                    raise ParseError('unknown mandatory public tag '+str(tag))
                if tag in (4,5) or (tag>32 and tag&1):
                    raw,pos=ntbs(data,pos,stop)
                    if tag==65:
                        value={'NTBS_hex':raw.hex()}
                    else:
                        value=ascii_name(raw,'public string')
                elif tag==32:
                    flag,pos=uleb(data,pos,stop);raw,pos=ntbs(data,pos,stop)
                    value={'flag':flag,'vendor':ascii_name(raw,'compatibility vendor')}
                else:
                    value,pos=uleb(data,pos,stop)
                public.pair_count+=1
                need(public.pair_count<=MAX_PAIRS,'attribute pair limit')
                values.append((tag,value,origin))
            need(pos==stop,'attribute overrun')
            keys=[('FILE',0)] if kind==1 else [(('SECTION' if kind==2 else 'SYMBOL'),i) for i in ids]
            record={'kind':{1:'FILE',2:'SECTION',3:'SYMBOL'}[kind],'indices':ids,'file_offset':file_offset+sub,'bytes':length,'attributes':[{'tag':t,'value':v,'file_offset':p} for t,v,p in values]}
            public.raw_public_blocks.append(record)
            for key in keys:
                for tag,value,origin in values:
                    public.merge(key,tag,value,{'public_block_offset':file_offset+sub,'attribute_offset':origin})
            pos=stop
        need(pos==end,'vendor overrun')
    need(pos==len(data),'attribute region trailing overrun')
    for sym in public.symbol_ids:
        if symbol_sections is not None:
            need(sym in public.symbol_sections and public.symbol_sections[sym] in public.section_ids,'invalid/undefined SYMBOL index')
    return public


def inspect_elf(data):
    need(52<=len(data)<=MAX_OBJECT,'ELF object size outside supported bounds')
    need(data[:6]==b'\x7fELF\x01\x01','only ELF32 little-endian is supported')
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    need(h[1]==1 and h[2]==40 and h[3]==1,'not ARM ET_REL version one')
    need(h[8]==52 and h[11]==40,'ELF header/section-entry size')
    need(0<h[12]<=MAX_SECTIONS and 0<h[13]<h[12],'unsupported extended/invalid section indices')
    need(52<=h[6] and h[6]+40*h[12]<=len(data),'section table bounds')
    raw=[struct.unpack_from('<10I',data,h[6]+40*i) for i in range(h[12])]
    for s in raw:
        if s[1]!=8:
            need(s[4]<=len(data) and s[4]+s[5]<=len(data),'section payload bounds')
    st=raw[h[13]];need(st[1]==3,'section-name table is not STRTAB')
    strings=data[st[4]:st[4]+st[5]]
    sections=[]
    for i,s in enumerate(raw):
        name,pos=ntbs(strings,s[0],len(strings))
        sections.append({'id':i,'name':ascii_name(name,'section name'),'type':s[1],'flags':s[2],'size':s[5],'offset':s[4]})
    carriers=[i for i,s in enumerate(raw) if s[1]==0x70000003]
    need(len(carriers)==1,'bounded reader requires one SHT_ARM_ATTRIBUTES carrier')
    a=raw[carriers[0]]
    attrs=parse_attributes(data[a[4]:a[4]+a[5]],range(1,len(raw)),file_offset=a[4])
    symbol_metadata_read=False
    if attrs.symbol_ids:
        tables=[s for s in raw if s[1]==2]
        need(len(tables)==1,'SYMBOL scopes require one unambiguous SYMTAB')
        table=tables[0]
        need(table[9]==16 and table[5]%16==0 and table[5]//16<=16384,'symbol-table bounds')
        for index in attrs.symbol_ids:
            need(0<index<table[5]//16,'SYMBOL index outside table')
            entry=struct.unpack_from('<IIIBBH',data,table[4]+16*index)
            need(0<entry[5]<len(raw),'undefined/special-section SYMBOL is unsupported')
            attrs.symbol_sections[index]=entry[5]
        symbol_metadata_read=True
    return {'ELF_class':data[4],'ELF_data':data[5],'ELF_type':h[1],'ELF_machine':h[2],'ELF_flags':h[7],'section_count':len(raw),'attribute_section_id':carriers[0],'symbol_table_index_metadata_read':symbol_metadata_read,'attributes':attrs,'code_sections':attrs.rows(sections),'sections_metadata':sections}
