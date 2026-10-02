"""Check object integrity, evidence links, credential redaction and Git size limits."""
from pathlib import Path
import hashlib
import json
from capture_history import redact

ROOT=Path(__file__).resolve().parents[1]

def main():
    inventory=json.loads((ROOT/'provenance/capture_inventory.json').read_text(encoding='utf8'))
    checked=set();errors=[]
    for e in inventory['entries']:
        if not e['captured']:continue
        sha=e['object_sha256'];path=ROOT/e['object_path']
        if sha not in checked:
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=sha:errors.append('Object digest mismatch: '+str(path))
            if len(raw)>=100_000_000:errors.append('GitHub oversized file: '+str(path))
            if not e['binary']:
                text=raw.decode('utf8')
                if redact(text)[0]!=text:errors.append('Unredacted credential: '+e['repository_path'])
            checked.add(sha)
        if hashlib.sha256((ROOT/e['repository_path']).read_bytes()).hexdigest()!=sha:
            errors.append('Materialized source mismatch: '+e['repository_path'])
    tags=set();events=[]
    for line in (ROOT/'history/experiments.jsonl').read_text(encoding='utf8').splitlines():
        e=json.loads(line);events.append(e)
        if e['tag'] in tags:errors.append('Duplicate experiment tag')
        tags.add(e['tag'])
        for path in e['all_evidence_origins']+[e['record_path']]:
            if not (ROOT/path).is_file():errors.append('Missing evidence: '+path)
        for path in e['version_evidence'].get('snapshot_paths',[]):
            if not (ROOT/path).is_file():errors.append('Missing historical snapshot: '+path)
    result={'objects_verified':len(checked),'captured_source_files_verified':sum(e['captured'] for e in inventory['entries']),
            'experiment_records_verified':len(events),'errors':errors,'pass':not errors,
            'scope':'Archive integrity and redaction only; does not validate robot performance.'}
    (ROOT/'provenance/ARCHIVE_VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
