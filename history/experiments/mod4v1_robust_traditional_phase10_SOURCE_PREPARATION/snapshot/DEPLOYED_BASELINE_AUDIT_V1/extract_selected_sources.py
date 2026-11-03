"""Read selected text from the exact user-supplied deployed ZIP; execute none."""
from pathlib import Path,PurePosixPath
import collections,hashlib,json,stat,zipfile
D=Path(__file__).resolve().parent
P=Path(r'C:\Users\lulu\Documents\xwechat_files\wxid_yut919v6wi5a22_9afc\msg\file\2026-08\StandardRobotpp-balance1(3).zip')
MAX_FILE=1024*1024;MAX_TOTAL=16*1024*1024
SUFFIXES={'.c','.cpp','.cc','.h','.hpp','.s','.ld','.sct','.ioc','.uvprojx','.uvoptx','.cmake','.md','.txt','.m','.yaml','.yml','.json'}
SKIP_PARTS={'.git','.svn','.hg','.idea','.vscode','build','out','output','outputs','cmake-build-debug','cmake-build-release','objects','listings','music'}
rows=[];excluded=[];total=0;seen=set();top=collections.Counter()
def sha(b):return hashlib.sha256(b).hexdigest()
def write_new(p,raw):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(raw)
with zipfile.ZipFile(P)as z:
    for i in z.infolist():
        pp=PurePosixPath(i.filename.replace('\\','/'));parts=pp.parts
        if len(parts)>1:top[parts[1]]+=1
        reason=None
        if i.is_dir():continue
        if pp.is_absolute()or '..'in parts or any(':'in p for p in parts):reason='unsafe_archive_path'
        elif stat.S_ISLNK(i.external_attr>>16):reason='symlink_not_followed'
        elif any(p.lower()in SKIP_PARTS for p in parts):reason='history_editor_build_or_unneeded_music_excluded'
        elif i.flag_bits&1:reason='encrypted_member_not_opened'
        elif pp.suffix.lower()not in SUFFIXES and pp.name.lower()not in('license','copying','makefile','cmakelists.txt'):reason='nonselected_extension'
        elif i.file_size>MAX_FILE:reason='member_text_size_cap'
        elif total+i.file_size>MAX_TOTAL:reason='total_text_budget'
        elif str(pp).casefold()in seen:reason='casefold_duplicate_path_not_overwritten'
        if reason:
            excluded.append(dict(member=i.filename,bytes=i.file_size,reason=reason));continue
        raw=z.read(i) # ZipFile verifies each selected member CRC.
        assert len(raw)==i.file_size
        encoding=None;text=None
        codecs=['utf-16']if raw[:2]in(b'\xff\xfe',b'\xfe\xff')else['utf-8-sig','gb18030']
        for codec in codecs:
            try:
                candidate=raw.decode(codec)
                if '\x00'in candidate:continue
                text=candidate;encoding=codec;break
            except UnicodeError:pass
        if text is None:
            excluded.append(dict(member=i.filename,bytes=i.file_size,reason='selected_suffix_not_decodable_text'));continue
        original=D/'source_original'/Path(*parts);readable=D/'source'/Path(*parts)
        decoded=text.encode('utf-8') # Preserve decoded CR/LF exactly; no OS newline conversion.
        write_new(original,raw);write_new(readable,decoded)
        seen.add(str(pp).casefold());total+=len(raw)
        rows.append(dict(member=i.filename,CRC32=f'{i.CRC:08x}',raw_bytes=len(raw),raw_SHA=sha(raw),original_path=str(original),
            encoding=encoding,readable_path=str(readable),readable_bytes=len(decoded),readable_SHA=sha(decoded),
            crc_checked_on_selected_payload=True,payload_executed=False))
manifest=dict(kind='USER_ACTUALLY_DEPLOYED_OLD_ROBOT_TEXT_SELECTION_NOT_MOD4_BINDING',source_archive=str(P),archive_bytes=P.stat().st_size,
    central_entry_count=1184,selected_text_count=len(rows),selected_original_bytes=total,source_not_executed_or_built_or_flashed=True,
    whole_archive_SHA_not_computed=True,git_history_credentials_hooks_objects_not_opened=True,
    per_file_cap=MAX_FILE,total_original_text_cap=MAX_TOTAL,top_member_components=dict(top),files=rows,excluded=excluded)
write_new(D/'SELECTED_SOURCE_MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False).encode('utf-8'))
print(json.dumps(dict(status='SELECTED_TEXT_EXTRACTED_NO_EXECUTION',selected_files=len(rows),original_bytes=total,top_components=dict(top),
    hardware_and_startup_hints=[r['member']for r in rows if any(s in r['member'].lower()for s in('chassis','motor','can','imu','ins_task','freertos','main.c','startup','robot','balance','parameter','bsp','board','config','cmake','keil','c_board'))][:120],
    manifest_SHA=sha((D/'SELECTED_SOURCE_MANIFEST.json').read_bytes()),whole_archive_SHA_not_computed=True),indent=2,ensure_ascii=False))
