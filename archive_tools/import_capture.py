"""Validate/extract capture ZIPs and materialize the original source hierarchy."""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def safe_name(value):
    value=re.sub(r'[<>:"|?*\x00-\x1f]', '_', value).rstrip(' .')
    if not value or value in {'.','..'}:raise ValueError('Unsafe path component')
    if re.match(r'(?i)^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)',value):value='_'+value
    return value

def import_zips(paths):
    manifests={};items={};roots={};capture_sessions=[]
    for path in paths:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                parts=PurePosixPath(name).parts
                if '..' in parts or PurePosixPath(name).is_absolute():raise ValueError('Unsafe ZIP path')
                if name.startswith('objects/sha256/'):
                    raw=z.read(name);sha=hashlib.sha256(raw).hexdigest()
                    if parts[-1]!=sha:raise ValueError('Invalid content-addressed object')
                    dest=ROOT/name
                    if dest.exists():
                        if hashlib.sha256(dest.read_bytes()).hexdigest()!=sha:raise ValueError('Existing object corrupt')
                    else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
                elif name.startswith('provenance/capture_') and name.endswith('.json'):
                    manifest=json.loads(z.read(name));capture_sessions.append({k:manifest[k] for k in
                        ('site','started_epoch','completed_epoch','unique_objects','read_only_source_capture')})
                    site=manifest['site'];manifests.setdefault(site,[]).append(manifest)
                    for r in manifest['roots']:roots[(site,r['stage'])]=r
                    for e in manifest['entries']:
                        key=(site,e['stage'],e['relative_path'])
                        # Complete, later capture supersedes an earlier metadata-only item.
                        if e['captured'] or key not in items:items[key]=e
                else:raise ValueError('Unexpected ZIP member')
    entries=sorted(items.values(),key=lambda e:(e['site'],e['stage'],e['relative_path']))
    grouped=collections.defaultdict(list)
    for e in entries:
        stage_id=e['site']+'--'+safe_name(e['stage'])
        e['stage_id']=stage_id;grouped[stage_id].append(e)
        if e['captured']:
            rel=PurePosixPath(e['relative_path'])
            if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe captured path')
            dest=ROOT/'sources'/e['site']/safe_name(e['stage'])
            for part in rel.parts:dest=dest/safe_name(part)
            dest.parent.mkdir(parents=True,exist_ok=True)
            raw=(ROOT/e['object_path']).read_bytes()
            if dest.exists() and dest.read_bytes()!=raw:raise ValueError('Sanitized filename collision')
            dest.write_bytes(raw)
            e['repository_path']=dest.relative_to(ROOT).as_posix()
    stages=[]
    (ROOT/'history/stages').mkdir(parents=True,exist_ok=True)
    for sid,values in grouped.items():
        first=values[0];stage={'id':sid,'site':first['site'],'name':first['stage'],
             'original_root':roots[(first['site'],first['stage'])]['root'],
             'files_indexed':len(values),'files_captured':sum(e['captured'] for e in values),
             'source_version_claim':'Read-only archive capture; saved per-run snapshots are separately indexed.',
             'author_attribution':'Unknown unless explicitly stated in preserved evidence. Directory name is not proof of authorship.',
             'entries':values}
        (ROOT/'history/stages'/f'{sid}.json').write_text(json.dumps(stage,ensure_ascii=False,indent=2),encoding='utf8')
        stages.append({k:stage[k] for k in stage if k!='entries'})
    combined={'schema_version':2,'capture_sessions':capture_sessions,'roots':list(roots.values()),
              'entries':entries,'errors':[error for ms in manifests.values() for m in ms for error in m['errors']],
              'notes':manifests['remote'][0]['notes']}
    (ROOT/'provenance/capture_inventory.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'history/stages.json').write_text(json.dumps(stages,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'stages':len(stages),'indexed_files':len(entries),'captured_files':sum(e['captured'] for e in entries),
                      'unique_objects':len(list((ROOT/'objects/sha256').glob('*/*'))),'errors':len(combined['errors'])}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zips',nargs='+',type=Path)
    import_zips(p.parse_args().zips)
