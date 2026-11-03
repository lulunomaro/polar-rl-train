"""Trusted inspection/copy helper; ZIP contents are never executed/imported."""
from pathlib import Path,PurePosixPath
import zipfile,json,hashlib,stat,zlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;AUDIT=ROOT/'SPR_AUDIT'
ARCHIVE=Path(r'C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip')
MAX=1048576;TOTAL=12582912;RATIO=200
SELECT=['chassis/Core/Src/main.c','chassis/Core/Src/freertos.c','chassis/application/chassis_behaviour.c','chassis/application/chassis_behaviour.h','chassis/Task/chassis_task.c','chassis/Task/chassis_task.h','chassis/Task/INS_task.c','chassis/Task/INS_task.h','chassis/Task/send_task.c','chassis/application/CAN_receive.c','chassis/application/CAN_receive.h','chassis/algorithm/leg_force.c','chassis/algorithm/leg_force.h','chassis/algorithm/leg_position.c','chassis/algorithm/leg_position.h','chassis/algorithm/LQR_K.c','chassis/algorithm/LQR_K.h','chassis/algorithm/PID.c','chassis/algorithm/PID.h','chassis/algorithm/kalman_filter.c','chassis/algorithm/kalman_filter.h','chassis/algorithm/KNN.c','chassis/algorithm/KNN.h','chassis/algorithm/ClimbKNN.c','chassis/algorithm/ClimbKNN.h','chassis/algorithm/MPC.c','chassis/user/readme.txt']
def load(p):return json.loads(p.read_bytes())
def rec(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(name,v):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def safe(name,attrs):
    assert '\\'not in name and '\x00'not in name and ':'not in name
    p=PurePosixPath(name);assert not p.is_absolute()and '..'not in p.parts and p.parts
    assert stat.S_IFMT(attrs>>16)!=stat.S_IFLNK
    return p
idx=load(AUDIT/'SPR_SOURCE_INDEX.json');prior=load(AUDIT/'zip_central_index.json');inner=load(AUDIT/'chassis_central_index.json')
assert Path(idx['original_archive']['path'])==ARCHIVE and ARCHIVE.stat().st_size==idx['original_archive']['bytes']
old={r['member']:r for r in prior['members']};central=[];written=0;selected=[];fold=set()
with zipfile.ZipFile(ARCHIVE,'r')as z:
    info=z.infolist();assert len({i.filename for i in info})==len(info)
    for i in info:
        row=dict(member=i.filename,uncompressed_bytes=i.file_size,compressed_bytes=i.compress_size,crc32=f'{i.CRC:08x}',compression=i.compress_type,is_directory=i.is_dir(),flags=i.flag_bits,external_attributes=i.external_attr)
        assert row==old[i.filename],('current central differs from prior index',i.filename)
        try:safe(i.filename,i.external_attr);row['safe_relative_non_symlink']=True
        except AssertionError:row['safe_relative_non_symlink']=False
        central.append(row)
    assert len(info)==len(old)
    container=next(r for r in central if r['member']=='SPR Balanced-infantry/code/chassis.zip')
    assert container['uncompressed_bytes']==inner['nested_archive']['bytes']==122201554
    # The sole fresh text decompression is the small outer README; ZipFile verifies CRC.
    member='SPR Balanced-infantry/readme.txt';i=z.getinfo(member);safe(member,i.external_attr)
    assert i.file_size<=MAX and i.file_size/max(1,i.compress_size)<=RATIO
    b=z.read(i);assert len(b)==i.file_size and zlib.crc32(b)==i.CRC
    oldread=next(r for r in idx['selected_members']if r['container_archive']is None and r['member']==member)
    assert hashlib.sha256(b).hexdigest()==oldread['member_sha256']
    dest=OUT/'source'/member;assert dest.resolve().is_relative_to(OUT.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb')as f:f.write(b)
    written+=len(b);selected.append(dict(member=member,container_archive=None,mode='FRESH_BOUNDED_ZIP_TEXT_READ_CRC_CHECKED',bytes=len(b),producer_SHA=hashlib.sha256(b).hexdigest(),readable_SHA=hashlib.sha256(b).hexdigest(),source_encoding=oldread['source_encoding'],path=str(dest.resolve())))
byinner={r['member']:r for r in inner['members']}
for name in SELECT:
    meta=byinner[name];safe(name,meta['external_attributes']);assert name.casefold()not in fold;fold.add(name.casefold())
    assert not meta['is_directory']and meta['uncompressed_bytes']<=MAX and meta['uncompressed_bytes']/max(1,meta['compressed_bytes'])<=RATIO
    oldsrc=next(r for r in idx['selected_members']if r['container_archive']=='SPR Balanced-infantry/code/chassis.zip'and r['member']==name)
    assert oldsrc['member_bytes']==meta['uncompressed_bytes']and oldsrc['crc32']==meta['crc32']
    src=(AUDIT/oldsrc['extracted_path']).resolve();assert src.is_relative_to(AUDIT.resolve())and src.is_file()and not src.is_symlink()
    b=src.read_bytes();assert len(b)<=MAX and hashlib.sha256(b).hexdigest()==oldsrc['extracted_sha256'];b.decode('utf-8-sig')
    if not oldsrc['transcoded']:assert len(b)==meta['uncompressed_bytes']and f'{zlib.crc32(b):08x}'==meta['crc32']
    written+=len(b);assert written<=TOTAL
    dest=OUT/'source'/name;assert dest.resolve().is_relative_to(OUT.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb')as f:f.write(b)
    selected.append(dict(member=name,container_archive='SPR Balanced-infantry/code/chassis.zip',mode='REUSED_PRIOR_AUDITED_TEXT_NOT_FRESH_NESTED_DECOMPRESSION',original_bytes=meta['uncompressed_bytes'],compressed_bytes=meta['compressed_bytes'],crc32=meta['crc32'],prior_member_producer_SHA=oldsrc['member_sha256'],source_encoding=oldsrc['source_encoding'],transcoded=oldsrc['transcoded'],readable_bytes=len(b),readable_SHA=hashlib.sha256(b).hexdigest(),path=str(dest.resolve()),prior_path=str(src)))
put('CENTRAL_CURRENT.json',dict(kind='CURRENT_OUTER_CENTRAL_VERIFIED_AGAINST_PRIOR_ALL_FIELDS_NO_ARCHIVE_HASH',archive=dict(path=str(ARCHIVE),bytes=ARCHIVE.stat().st_size,mtime_ns=ARCHIVE.stat().st_mtime_ns),members=central,current_entries=len(central),nested_payload_reads=0))
put('SELECTED_SOURCE_MANIFEST.json',dict(kind='CURRENT_OUTER_IDENTITY_PLUS_PRIOR_AUDIT_TEXT_PROVENANCE_STATIC_ONLY',archive=dict(path=str(ARCHIVE),bytes=ARCHIVE.stat().st_size,prior_archive_SHA_declared_not_recomputed=idx['original_archive']['sha256']),container=container,prior_nested_metadata=inner['nested_archive'],current_outer_entries_all_metadata_match=True,current_nested_payload_reread=False,current_nested_payload_SHA_recomputed=False,current_outer_readme_fresh_CRC_and_SHA_match=True,selected=selected,selected_files=len(selected),new_text_bytes_written=written,selected_original_bytes=sum(r.get('original_bytes',r.get('bytes',0))for r in selected),max_text_total=TOTAL,max_single=MAX,max_compression_ratio=RATIO,large_zip_hashes=0,code_or_readme_commands_executed=0,prior_metadata_refs=[rec(AUDIT/n)for n in['SPR_SOURCE_INDEX.json','zip_central_index.json','chassis_central_index.json','selection_chassis.json','build_entry_map.json']]))
print(json.dumps(dict(status='SELECTED_READONLY_TEXT_READY_FOR_READ_TOOL',current_central_entries=len(central),chassis_container_bytes=container['uncompressed_bytes'],chassis_container_crc=container['crc32'],selected_files=len(selected),text_bytes=written,nested_reread=False,large_archive_hashes=0,critical_paths=[str(OUT/'source/chassis/Task/chassis_task.c'),str(OUT/'source/chassis/application/chassis_behaviour.c')]),indent=2))
