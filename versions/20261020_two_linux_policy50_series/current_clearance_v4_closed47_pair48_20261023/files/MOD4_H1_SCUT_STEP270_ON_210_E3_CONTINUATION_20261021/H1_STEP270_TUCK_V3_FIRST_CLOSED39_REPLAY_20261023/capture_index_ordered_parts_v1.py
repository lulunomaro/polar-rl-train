"""Lossless forward-only text index partitions; legacy JSON indexes remain readable."""
from pathlib import Path
import hashlib,json

FORMAT='complete_capture_index_full_ordered_utf8_parts_v1'

def index_parts(raw,maximum=24000000):
    result=[];offset=0
    while offset<len(raw):
        end=min(offset+maximum,len(raw))
        while end<len(raw) and raw[end]&0xc0==0x80:end-=1
        assert end>offset
        block=raw[offset:end];block.decode('utf8');result.append(block);offset=end
    return result

def reassemble_index(parts,rows,total,sha):
    assert len(parts)==len(rows)
    joined=hashlib.sha256();data=[];size=0
    for block,row in zip(parts,rows):
        assert len(block)==row['bytes'] and hashlib.sha256(block).hexdigest()==row['SHA']
        block.decode('utf8');joined.update(block);size+=len(block);data.append(block)
    assert size==total and joined.hexdigest()==sha
    return json.loads(b''.join(data))

def read_capture_index(path,repo_root):
    value=json.loads(Path(path).read_bytes())
    if value.get('format')!=FORMAT:
        assert isinstance(value.get('entries'),list),'Expected complete legacy entries or the recognized full-parts format'
        return value
    root=Path(repo_root).resolve();parts=[]
    for row in value['ordered_UTF8_parts']:
        rel=Path(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
        p=(root/rel).resolve();assert p.is_relative_to(root) and p.is_file() and not p.is_symlink()
        parts.append(p.read_bytes())
    result=reassemble_index(parts,value['ordered_UTF8_parts'],value['complete_json_bytes'],value['complete_json_SHA'])
    assert result['epoch']==value['epoch'] and result['kind']==value['kind'] and len(result['entries'])==value['complete_entries_count']
    return result

def write_capture_index(path,index,add,splits,repo_root):
    path=Path(path);root=Path(repo_root).resolve();raw=json.dumps(index,ensure_ascii=False,indent=2).encode('utf8')
    if len(raw)<=49000000:
        add(path,raw);return 'legacy_plain_JSON'
    blocks=index_parts(raw);rows=[]
    for i,block in enumerate(blocks):
        p=path.with_name(path.name+'.utf8part'+str(i).zfill(4)+'.txt')
        assert p.resolve().is_relative_to(root)
        rows.append(dict(path=p.relative_to(root).as_posix(),bytes=len(block),SHA=hashlib.sha256(block).hexdigest()))
    sha=hashlib.sha256(raw).hexdigest()
    assert reassemble_index(blocks,rows,len(raw),sha)==index
    for block,row in zip(blocks,rows):add(root/row['path'],block)
    descriptor=dict(epoch=index['epoch'],kind=index['kind'],format=FORMAT,complete_entries_count=len(index['entries']),complete_json_bytes=len(raw),complete_json_SHA=sha,ordered_UTF8_parts=rows,full_reassembled_SHA_verified=True,all_original_JSON_values_preserved=True,not_a_partial_or_excerpt_index=True)
    add(path,json.dumps(descriptor,ensure_ascii=False,indent=2).encode('utf8'))
    splits.append(dict(source_kind='complete_capture_index',original_path=str(path),archived_bytes=len(raw),archived_SHA=sha,ordered_UTF8_parts=rows,full_reassembled_SHA_verified=True))
    return FORMAT
