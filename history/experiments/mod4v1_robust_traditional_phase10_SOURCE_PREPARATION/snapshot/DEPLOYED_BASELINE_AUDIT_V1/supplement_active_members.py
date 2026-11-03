"""Parent-approved exact offline build-dependency copy, never library execution.
Includes the two named static libraries for a real build purpose, not archive-only
hashing. Does not invoke Keil, old hooks, flash tools or any package program.
"""
from pathlib import Path,PurePosixPath
import hashlib,json,stat,zipfile
D=Path(__file__).resolve().parent;R=D.parent
P=Path(r'C:\Users\lulu\Documents\xwechat_files\wxid_yut919v6wi5a22_9afc\msg\file\2026-08\StandardRobotpp-balance1(3).zip')
req_path=R/'MOD4_DEPLOYMENT_PORT_V1/NEEDED_MEMBERS.json';req=json.loads(req_path.read_bytes())
needed={x['member']:x for x in req['active_project_members']}
assert len(needed)==17 and all(x['central']is True for x in needed.values())
O=D/'build_supplement001';O.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b)
put(O/'PLAN.json',json.dumps(dict(request=str(req_path),request_SHA=sha(req_path.read_bytes()),
    named_members=sorted(needed),additional='Only local music .h declarations required by selected active music TUs',
    maximum_original_bytes=15*1024*1024,maximum_files=40,payload_or_library_executions=0),indent=2).encode())
rows=[];total=0
with zipfile.ZipFile(P)as z:
    infos={i.filename:i for i in z.infolist()}
    wanted=set(needed)|{n for n in infos if n.startswith('StandardRobotpp-balance1/application/music/')and n.lower().endswith('.h')}
    assert len(wanted)<=40
    for name in sorted(wanted):
        pp=PurePosixPath(name);i=infos[name]
        assert not pp.is_absolute()and '..'not in pp.parts and '.git'not in pp.parts and not stat.S_ISLNK(i.external_attr>>16)
        assert name.startswith('StandardRobotpp-balance1/')and not i.is_dir()and not(i.flag_bits&1)
        if name in needed:assert i.file_size==needed[name]['central_bytes']and f'{i.CRC:08x}'==needed[name]['CRC32']
        assert i.file_size<=14*1024*1024 and total+i.file_size<=15*1024*1024
        raw=z.read(i);total+=len(raw);original=O/'source_original'/Path(*pp.parts);put(original,raw)
        r=dict(member=name,bytes=len(raw),raw_SHA=sha(raw),CRC32=f'{i.CRC:08x}',CRC_verified=True,original_path=str(original),executed=False)
        if pp.suffix.lower()!='.lib':
            codecs=['utf-16']if raw[:2]in(b'\xff\xfe',b'\xfe\xff')else['utf-8-sig','gb18030','cp1252']
            for encoding in codecs:
                try:
                    text=raw.decode(encoding)
                    if '\x00'in text:continue
                    readable=O/'source'/Path(*pp.parts);b=text.encode('utf-8');put(readable,b)
                    r.update(encoding=encoding,readable_path=str(readable),readable_SHA=sha(b),readable_bytes=len(b));break
                except UnicodeError:continue
            else:raise ValueError('No supported text encoding: '+name)
        else:r.update(kind='OPAQUE_STATIC_LINK_LIBRARY_NOT_EXECUTED',algorithm_and_ABI_not_verified=True)
        rows.append(r)
out=dict(status='ACTIVE_BUILD_DEPENDENCIES_COPIED_ONLY_NOT_BUILT_OR_FLASHED',source_archive=str(P),request_SHA=sha(req_path.read_bytes()),
    files=rows,total_original_bytes=total,whole_ZIP_hash_not_computed=True,archive_programs_or_libraries_executed=0,
    original_archive_selected_source_or_derived_project_modified=False)
put(O/'MANIFEST.json',json.dumps(out,indent=2,ensure_ascii=False).encode('utf-8'))
print(json.dumps(dict(status=out['status'],files=len(rows),original_bytes=total,manifest_SHA=sha((O/'MANIFEST.json').read_bytes()),
    text_encodings={r['member']:r['encoding']for r in rows if 'encoding'in r},libraries=[r for r in rows if r['member'].endswith('.lib')]),indent=2))
