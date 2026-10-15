"""Read all archive headers before extraction; do not create environment files."""
from pathlib import Path, PurePosixPath
import json
import tarfile
import time
import sys

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')
ARCHIVE = ROOT/'downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz'


def main():
    report=ROOT/'audit/ARCHIVE_PATH_PREFLIGHT_V1_ACTUAL.json'
    assert ROOT.resolve()==ROOT and not report.exists()
    count=regular=total=0
    issues=[]
    links=[]
    first=last=time.time()
    with tarfile.open(ARCHIVE,'r|gz') as z:
        for m in z:
            count+=1
            p=PurePosixPath(m.name)
            if p.is_absolute() or '..' in p.parts or not p.parts:
                issues.append(dict(name=m.name,issue='unsafe_member_path'))
            elif p.parts[0] not in ('fangzhen-isaaclab','isaac','robot','cad','scripts','train','third_party'):
                issues.append(dict(name=m.name,issue='unmapped_top_level'))
            if m.isfile():regular+=1;total+=m.size
            elif m.issym():
                links.append(dict(name=m.name,target=m.linkname))
                if m.linkname.startswith('/') and not any(m.linkname==x or m.linkname.startswith(x+'/') for x in (
                    '/home/egde/anaconda3/envs/fangzhen-isaaclab','/home/egde/fangzhen_linux',
                    '/lib','/lib64','/usr/lib','/etc/ssl','/usr/share/zoneinfo')):
                    issues.append(dict(name=m.name,target=m.linkname,issue='unmapped_absolute_link'))
            elif not (m.isdir() or m.islnk()):
                issues.append(dict(name=m.name,issue='unsupported_special_member'))
            if time.time()-last>=20:
                print(json.dumps(dict(phase='archive_path_preflight_readonly',members=count,
                    regular_file_bytes=total,elapsed_seconds=time.time()-first)),flush=True)
                last=time.time()
    v=dict(epoch=time.time(),passed=not issues,members=count,regular_files=regular,regular_file_bytes=total,
        symlinks=links,issues=issues,no_environment_extracted_or_outside_root_write=True,
        original_archive_retained=True,elapsed_seconds=time.time()-first)
    with report.open('x') as f:json.dump(v,f,indent=2)
    print(json.dumps(dict(passed=not issues,members=count,regular_files=regular,bytes=total,issues=issues)),flush=True)
    if issues:sys.exit(2)


if __name__=='__main__':main()
