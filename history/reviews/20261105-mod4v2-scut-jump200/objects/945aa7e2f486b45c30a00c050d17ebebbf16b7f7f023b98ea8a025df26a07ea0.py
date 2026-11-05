"""Keep a huge immutable return intact; stream its log strings to local files."""
from pathlib import Path
import argparse,codecs,hashlib,json,mmap,re,time

p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);a=p.parse_args()
A=a.root.resolve();R=A/'reports';source=R/'POSTROUND_FULL_RETURNED.json'
destination=R/'LOCAL_COMPLETE_RETURNED.json'
assert not destination.exists()
files={}
with source.open('rb')as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ)as raw:
    matches=list(re.finditer(rb'(?m)^    "([^"\n]+)": ',raw))
    for index,match in enumerate(matches):
        name=match.group(1).decode('utf8');start=match.end()
        end=matches[index+1].start()if index+1<len(matches)else re.search(rb'\r?\n  },\r?\n  "exact_owner_alive"',raw).start()
        while raw[end-1:end]in(b'\n',b'\r',b' ',b','):end-=1
        if name.endswith('.log'):
            marker=raw.find(b'\n      "text": "',start,end)
            assert marker>=0,name
            textstart=marker+len(b'\n      "text": "')
            textend=raw.rfind(b'"',textstart,end)
            header=raw[start:marker].rstrip(b'\r\n ,')+b'}'
            meta=json.loads(header)
            target=R/('CLOSED_'+Path(name).name)
            if target.exists():
                with target.open('rb')as local:digest=hashlib.file_digest(local,'sha256').hexdigest()
                assert digest==meta['SHA']and target.stat().st_size==meta['bytes']
                meta.update(local_path=str(target),text_external=True,original_full_return_preserved=True)
                files[name]=meta
                continue
            with target.open('xb')as out:
                position=textstart;carry=b''
                while position<textend:
                    piece=carry+raw[position:min(textend,position+1024*1024)]
                    position+=min(textend-position,1024*1024)
                    # Preserve a possibly incomplete escape/UTF8 codepoint.
                    cutoff=max(0,len(piece)-16)if position<textend else len(piece)
                    while cutoff and (piece[cutoff-1:cutoff]==b'\\'or (cutoff<len(piece)and piece[cutoff]&0xc0==0x80)):cutoff-=1
                    if cutoff:
                        # Logs are escaped JSON strings, not Python literals.
                        out.write(json.loads(b'"'+piece[:cutoff]+b'"').encode('utf8'))
                    carry=piece[cutoff:]
                assert not carry
            with target.open('rb')as local:digest=hashlib.file_digest(local,'sha256').hexdigest()
            assert digest==meta['SHA']and target.stat().st_size==meta['bytes'],name
            meta.update(local_path=str(target),text_external=True,original_full_return_preserved=True)
            files[name]=meta
        else:files[name]=json.loads(raw[start:end])
    tail=raw[raw.rfind(b'\n  "exact_owner_alive"'):]
    alive=json.loads(b'{'+tail.strip().rstrip(b'}')+b'}')['exact_owner_alive']
with source.open('rb')as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
with destination.open('x',encoding='utf8')as out:json.dump(dict(epoch=time.time(),files=files,
    exact_owner_alive=alive,immutable_full_return=dict(path=str(source),bytes=source.stat().st_size,SHA=sha),
    log_text_streamed_without_secondSSH=True),out,indent=2)
print(json.dumps(dict(path=str(destination),files=len(files),owner_alive=alive,
    logs={k:v['bytes']for k,v in files.items()if k.endswith('.log')})))
