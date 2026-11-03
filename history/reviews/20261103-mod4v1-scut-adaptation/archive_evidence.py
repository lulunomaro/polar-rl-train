"""Archive changed small text and reference identical Git content/large artifacts."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

G = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parent
S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
N = S/'runs/h1_target_limit_cont_20261103'
ANALYSIS = S/'analysis/20261103_targetlimitcont477_vs455'


def main():
    dest=R/'EVIDENCE_INDEX.json'
    if dest.exists():
        raise FileExistsError('Evidence frozen; append changes as a supplement')
    sys.path.insert(0,str(G/'archive_tools'))
    from capture_history import redact
    tree=subprocess.check_output(['git','-C',str(G),'ls-tree','-r','HEAD'],text=True,encoding='utf-8')
    known={}
    for line in tree.splitlines():
        metadata,path=line.split('\t',1)
        known.setdefault(metadata.split()[2],path)
    rows=[];text_count=0;redaction_count=0
    def capture(path,label,raw=None,actual=None):
        nonlocal text_count,redaction_count
        path=Path(path)
        if raw is None:
            raw=path.read_bytes()
        original_sha=hashlib.sha256(raw).hexdigest()
        if actual:
            assert len(raw)==actual['bytes'] and original_sha==actual['SHA'],label
        row=dict(path=str(path),bytes=len(raw),SHA=original_sha)
        if len(raw)>5_000_000:
            row.update(archive='external_large_raw',preserved=True)
        else:
            text=raw.decode('utf-8-sig')
            clean,count=redact(text)
            archived=clean.encode('utf-8') if count else raw
            blob=hashlib.sha1(b'blob '+str(len(archived)).encode()+b'\0'+archived).hexdigest()
            row.update(archived_SHA=hashlib.sha256(archived).hexdigest(),redactions=count)
            redaction_count+=count
            if blob in known:
                row.update(archive='same_blob_reference',git_path=known[blob])
            else:
                target=R/'evidence'/label
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb')as out:out.write(archived)
                row.update(archive='full_text' if count==0 else 'redacted_text',git_path=target.relative_to(G).as_posix())
                known[blob]=row['git_path'];text_count+=1
        rows.append(row)
    for path in sorted(N.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.py','.json','.log','.md','.csv','.txt'):
            continue
        if path.name=='ROOT477_EVALUATION_FULL_RETURNED.json':
            source=json.loads((ANALYSIS/'analysis.json').read_bytes())['source_result']
            assert path.stat().st_size==source['bytes']
            rows.append(dict(**source,archive='external_large_raw',preserved=True));continue
        capture(path,Path('h1_476_477')/path.relative_to(N))
    for path in sorted(ANALYSIS.iterdir()):
        if path.suffix.lower() in ('.json','.csv','.md','.py'):
            capture(path,'analysis477/'+path.name)
    capture(S/'admin/CURRENT_STATE.json','state/CURRENT_STATE.json')
    # Full returned file embeds original remote UTF8 reports. Preserve small
    # originals separately and only index large raw traces already inside it.
    returned=json.loads((N/'evaluation/reports/ROOT477_EVALUATION_FULL_RETURNED.json').read_bytes())
    embedded=[]
    for row in returned['full_UTF8']:
        raw=row['UTF8'].encode('utf-8')
        capture(row['path'],'evaluation477_embedded/'+Path(row['path']).name,raw,row)
        embedded.append(dict(path=row['path'],bytes=row['bytes'],SHA=row['SHA']))
    for subdir in ('recorded_native','recorded_native_late'):
        rendering=json.loads((N/'evaluation'/subdir/'RENDER_REPORT.json').read_bytes())
        for media in rendering['media']:
            rows.append(dict(**media,archive='external_media',current_model_native_reviewed=True))
    # Store the saved actual cases/summary, not a new physics evaluation.
    capture('embedded_RESULT477.json','evaluation477_embedded/RESULT477_SUMMARY.json',
            json.dumps(returned['result'],ensure_ascii=False,indent=2).encode('utf-8'))
    auto=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
    capture(auto,'automation/mod4-10.toml')
    oldtags=subprocess.check_output(['git','-C',str(G),'show-ref','--tags','--dereference'],text=True,encoding='utf-8')
    (R/'OLD_TAG_OBJECTS_BEFORE.txt').write_text(oldtags,encoding='utf-8')
    index=dict(entries=rows,changed_text=text_count,redactions=redaction_count,
        same_blob_references=sum(r['archive']=='same_blob_reference' for r in rows),
        external_large_or_media=sum(r['archive'].startswith('external')for r in rows),
        no_model_reads=True,no_physics=True,no_old_once_replay=True,
        embedded_report_index=embedded)
    dest.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:index[k]for k in ('changed_text','redactions','same_blob_references','external_large_or_media')}))


if __name__=='__main__':main()
