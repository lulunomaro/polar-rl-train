"""Exact one missing compile dependency from authorized original ZIP, no execution.
Parent explicit per-member cap exception2MiB; initial1MiB text cap excluded this
1,350,860B header. No broad extraction, original/Stage1 trees stay untouched.
"""
from pathlib import Path
import json,hashlib,zipfile,stat
D=Path(__file__).resolve().parent;O=D/'device_header_supplement002';O.mkdir(exist_ok=False)
central=json.loads((D/'CENTRAL_DIRECTORY.json').read_bytes())
name='StandardRobotpp-balance1/Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f407xx.h'
rec=next(r for r in central['members']if r['name']==name)
assert rec['bytes']==1350860 and rec['CRC32']=='9a578ca0'and not rec['symlink']and not rec['is_directory']
archive=Path(central['source']);assert archive.stat().st_size==central['archive_bytes']
def put(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b)
def sha(b):return hashlib.sha256(b).hexdigest()
put(O/'PLAN.json',json.dumps(dict(member=name,maximum_member_bytes=2*1024*1024,maximum_members=1,
    reason='Actual first main.c compiler failure needs this device header, not archive-only hashing.',
    original1MiB_extraction_cap_smaller_than_member=True,original_ZIP_or_sealed_derived_modified=False,algorithms_executed=0),indent=2).encode())
with zipfile.ZipFile(archive)as z:
    i=z.getinfo(name);assert i.file_size==rec['bytes']and f'{i.CRC:08x}'==rec['CRC32']and not(i.flag_bits&1)and not stat.S_ISLNK(i.external_attr>>16)
    assert i.file_size<=2*1024*1024
    b=z.read(i);assert len(b)==i.file_size and b'\x00'not in b
original=O/'source_original'/name;overlay=O/'device_headers/stm32f407xx.h';put(original,b);put(overlay,b)
encoding=None
for codec in('utf-8-sig','gb18030','cp1252'):
    try:text=b.decode(codec);encoding=codec;break
    except UnicodeError:continue
assert encoding is not None
readable=O/'source/stm32f407xx.h';put(readable,text.encode('utf-8'))
r=dict(status='EXACT_DEVICE_HEADER_COPIED_ONLY_NOT_COMPILED',member=name,source_archive=str(archive),bytes=len(b),CRC32=rec['CRC32'],CRC_verified=True,
    SHA=sha(b),original_path=str(original),compiler_overlay_path=str(overlay),readable_path=str(readable),encoding=encoding,
    only_one_member_read=True,original_ZIP_sealed_derived_or_old_manifest_written=False,whole_ZIP_hash=False,
    library_program_or_compiler_executions=0,missing_dependency_fixed_in_NEW_overlay_only=True)
put(O/'RECEIPT.json',json.dumps(r,indent=2).encode());print(json.dumps(r,indent=2))
