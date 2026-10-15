"""Extract into new owned directories only. Original tar is retained; no deletion."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import posixpath
import tarfile
import time
import traceback

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')
ARCHIVE = ROOT / 'downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz'
ENV = ROOT / 'envs/mod4'
PROJECT = ROOT / 'src/fangzhen_linux'
OLD_ENV = '/home/egde/anaconda3/envs/fangzhen-isaaclab'
OLD_PROJECT = '/home/egde/fangzhen_linux'


def below(p):
    p = Path(p)
    assert str(p.resolve()).startswith(str(ROOT.resolve()) + '/'), str(p)
    return p


def mapped_archive_path(name):
    p = PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts and p.parts
    if p.parts[0] == 'fangzhen-isaaclab':
        return ENV.joinpath(*p.parts[1:])
    assert p.parts[0] in ('isaac', 'robot', 'cad', 'scripts', 'train', 'third_party'), name
    return PROJECT.joinpath(*p.parts)


def mapped_absolute(name):
    for old, new in ((OLD_ENV, str(ENV)), (OLD_PROJECT, str(PROJECT))):
        if name == old or name.startswith(old + '/'):
            return new + name[len(old):]
    return None


def main():
    assert ROOT.resolve() == ROOT and ARCHIVE.is_file()
    assert not ENV.exists() and not PROJECT.exists()
    assert not (ROOT / 'audit/EXTRACTION_V1_STARTED.json').exists()
    receipt = ROOT / 'audit/SOURCE_ARCHIVE_V2_STREAM_SHA_ACTUAL.json'
    expected = json.loads(receipt.read_bytes())
    h = hashlib.sha256()
    with ARCHIVE.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            h.update(b)
    assert h.hexdigest() == expected['sha256'] and ARCHIVE.stat().st_size == expected['bytes']
    started = dict(epoch=time.time(), archive=str(ARCHIVE), archive_bytes=expected['bytes'],
        archive_SHA=expected['sha256'], environment=str(ENV), project=str(PROJECT),
        no_deletion_or_existing_user_file_overwrite=True)
    with (ROOT / 'audit/EXTRACTION_V1_STARTED.json').open('x') as f:
        json.dump(started, f, indent=2)
    ENV.mkdir()
    PROJECT.mkdir()
    count = size = 0
    links, hardlinks, external = [], [], []
    last = begin = time.time()
    index_path = ROOT / 'audit/EXTRACTED_FILE_SHA_V1.jsonl'
    with index_path.open('x', encoding='utf8') as index, tarfile.open(ARCHIVE, 'r|gz') as archive:
        for member in archive:
            dest = mapped_archive_path(member.name)
            below(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if member.isdir():
                assert not dest.is_symlink()
                dest.mkdir(exist_ok=True)
                continue
            assert not dest.exists() and not dest.is_symlink(), str(dest)
            if member.issym():
                target = member.linkname
                if target.startswith('/'):
                    rewritten = mapped_absolute(target)
                    if rewritten is None:
                        assert any(target.startswith(x) for x in ('/lib/', '/lib64/', '/usr/lib/', '/etc/ssl/', '/usr/share/zoneinfo/')), target
                        external.append(dict(path=str(dest), target=target, inherited_readonly_system_link=True))
                    else:
                        target = rewritten
                else:
                    resolved = posixpath.normpath(posixpath.join(str(dest.parent), target))
                    if not resolved.startswith(str(ROOT) + '/'):
                        raise RuntimeError('Relative link escapes owned root: ' + member.name)
                os.symlink(target, str(dest))
                links.append(dict(path=str(dest), old=member.linkname, actual_target=target))
            elif member.islnk():
                target = mapped_archive_path(member.linkname)
                below(target)
                if target.exists():
                    os.link(str(target), str(dest))
                else:
                    hardlinks.append((str(dest), str(target)))
            elif member.isfile():
                source = archive.extractfile(member)
                assert source is not None
                digest = hashlib.sha256()
                copied = 0
                with dest.open('xb') as out:
                    for data in iter(lambda: source.read(4*1024*1024), b''):
                        out.write(data)
                        digest.update(data)
                        copied += len(data)
                        size += len(data)
                        if time.time()-last >= 20:
                            print(json.dumps(dict(epoch=time.time(), phase='extract_and_SHA_inside_zonglin2',
                                regular_files=count, extracted_bytes=size, elapsed_seconds=time.time()-begin)), flush=True)
                            last = time.time()
                assert copied == member.size
                os.chmod(str(dest), member.mode & 0o777)
                os.utime(str(dest), (member.mtime, member.mtime))
                count += 1
                index.write(json.dumps(dict(archive_name=member.name, path=str(dest), bytes=copied,
                    sha256=digest.hexdigest(), mode=member.mode & 0o777)) + '\n')
            else:
                raise RuntimeError('Unsupported special member preserved in archive: ' + member.name)
    for dest, target in hardlinks:
        below(dest)
        below(target)
        assert Path(target).is_file() and not Path(dest).exists()
        os.link(target, dest)
    value = dict(epoch=time.time(), complete=True, regular_files=count, regular_file_bytes=size,
        symlinks=links, deferred_hardlinks=hardlinks, inherited_readonly_system_links=external,
        archive_SHA=expected['sha256'], archive_retained=True, file_SHA_index=str(index_path),
        environment=str(ENV), project=str(PROJECT), elapsed_seconds=time.time()-begin,
        no_deletion_or_outside_root_write=True, no_runtime_admission_claimed=True)
    with (ROOT / 'audit/EXTRACTION_V1_COMPLETE.json').open('x') as f:
        json.dump(value, f, indent=2)
    print(json.dumps(dict(complete=True, files=count, extracted_bytes=size, symlinks=len(links),
                         inherited_readonly_links=len(external))), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (ROOT / ('audit/EXTRACTION_V1_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x') as f:
            json.dump(dict(error=traceback.format_exc(), original_archive_and_partial_files_retained=True,
                           no_deletion_or_blind_extraction_replay=True), f, indent=2)
        raise
