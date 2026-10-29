"""Resume the existing staged118 supplement, preserving its original refusal.
No old capture/main/experiment/CPU diagnostic is rerun. No new trial tag.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import time

T = Path(__file__).resolve().parent
G = T.parent / 'polar-rl-train'
D = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native120_original_closure_vs_imagined_stop_CPU_review_v1'
R = D / 'reports'
REL = 'versions/20261029_mod4-native116-latest-user-mujoco-actual-blue-imagination118/ordinary_source119120_core_failure_review_v1'
DEST = G / REL
BASE = '306b79e2aa75ca7992a740d03eedf0e43518130e'


def run(*args):
    return subprocess.run(['git', *args], cwd=G, capture_output=True)


def git(*args, binary=False):
    p = run(*args)
    if p.returncode:
        raise RuntimeError(args[0]+' failed: '+p.stderr.decode('utf-8', 'replace')[-1600:])
    return p.stdout if binary else p.stdout.decode('utf-8').strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def put(p, obj):
    assert not p.exists(), str(p)
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))


def tags_local():
    out = {}
    for line in git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags').splitlines():
        row = line.split()
        out[row[0]] = dict(object=row[1], peeled=row[2] if len(row)==3 else None)
    return out


def remote():
    refs = dict(line.split()[::-1] for line in git('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*').splitlines())
    tags = {name:dict(object=obj, peeled=refs.get(name+'^{}')) for name,obj in refs.items()
            if name.startswith('refs/tags/') and not name.endswith('^{}')}
    return refs['refs/heads/main'], tags


def main():
    assert git('rev-parse', 'HEAD') == BASE
    index = json.loads((DEST/'ORDINARY_CAPTURE_INDEX.json').read_bytes())
    old_tags = index['protected_tags']
    assert len(old_tags)==1484 and tags_local()==old_tags
    assert remote() == (BASE, old_tags)
    staged = git('diff', '--cached', '--name-only').splitlines()
    assert staged and all(x.startswith(REL+'/') for x in staged)
    marker = R/'ORDINARY119120_EXISTING_INDEX_FINISH_CONSUMED.json'
    put(marker, dict(epoch=time.time(), old_capture_not_replayed=True,
        mode='finish existing staged ordinary supplement after whitespace-only archive refusal',
        previous_HEAD=BASE, no_new_tag=True, no_model_raw_CPU_experiment_or_runtime_execution=True))

    # Retain full original checker output and isolate Windows publication CRs.
    default = run('diff', '--cached', '--check')
    cr = run('-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check')
    default_path = R/'ORIGINAL_ARCHIVE_DIFF_CHECK_FULL_UTF8.txt'
    cr_path = R/'CR_AWARE_ARCHIVE_DIFF_CHECK_FULL_UTF8.txt'
    for p,raw in [(default_path,default.stdout), (cr_path,cr.stdout)]:
        assert not p.exists()
        raw.decode('utf-8')
        p.write_bytes(raw)
    issues = [x for x in cr.stdout.decode('utf-8').splitlines() if ': trailing whitespace.' in x or ': new blank line at EOF.' in x]
    expected_rel = REL+'/files/36735776b121ac7754d0.txt'
    assert default.returncode==2 or default.returncode==1
    assert cr.returncode in (1,2) and issues
    assert all(x.startswith(expected_rel+':') for x in issues), issues[:3]

    # The old excerpt is retained. Numerical execution used original parsed AST
    # (review script line37), before the display-only write_text publication.
    original = T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/job0/runtime/isaac/mod4/mod4_task.py'
    raw = original.read_bytes()
    text = raw.decode('utf-8')
    names = {'_closure_cache','closure_errors','closure_broken','_past_spawn_grace'}
    nodes = [n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == names
    segments = [ast.get_source_segment(text,n).encode('utf-8') for n in nodes]
    corrected = D/'ORIGINAL_CLOSURE_FUNCTIONS_EXACT_SEGMENTS_BYTE_WRITTEN_V2.txt'
    assert not corrected.exists()
    corrected.write_bytes(b'\n\n'.join(segments))
    put(R/'ORIGINAL_SOURCE_EXCERPT_WINDOWS_NEWLINE_PUBLICATION_ERROR_AND_BYTE_WRITTEN_V2.json',
        dict(epoch=time.time(), original_physics_source=str(original), original_source_SHA256=sha(raw),
        retained_original_excerpt=str(D/'ORIGINAL_CLOSURE_AND_GRACE_FUNCTIONS_EXACT_SOURCE.txt'),
        original_error='write_text on Windows translated existing CRLF into CRCRLF in the display-only excerpt; its EXACT_SOURCE filename overstates byte exactness.',
        original_numerical_execution='compile(ast.Module(body=original_nodes,...)) directly from original mod4_task.py; no published excerpt was executed.',
        numerical_result_not_recomputed_or_modified=True, original_false_preserved=True,
        corrected_byte_written_excerpt=str(corrected), separator_between_exact_segments='two LF bytes; not claimed as contiguous original file bytes',
        segment_rows=[dict(name=n.name, bytes=len(s), SHA256=sha(s)) for n,s in zip(nodes,segments)],
        original_default_check_RC=default.returncode, CR_aware_check_RC=cr.returncode,
        remaining_CR_aware_warning_count=len(issues), warning_scope='only retained CRCRLF documentary .txt excerpt',
        repository_attributes_unchanged=True, no_runtime_source_model_or_Git_tag_change=True))

    additions = [Path(__file__).resolve(), corrected, marker, default_path, cr_path,
        R/'ORIGINAL_SOURCE_EXCERPT_WINDOWS_NEWLINE_PUBLICATION_ERROR_AND_BYTE_WRITTEN_V2.json']
    additions += sorted(R.glob('ORDINARY119120_ARCHIVE_ERROR_*.json'))
    assert len(additions)>=7
    rows=[]
    for p in additions:
        before=p.stat(); data=p.read_bytes(); data.decode('utf-8-sig')
        assert before.st_size==len(data) and p.stat().st_mtime_ns==before.st_mtime_ns
        name=sha(str(p).encode())[:20]+p.suffix.lower()
        dst=DEST/'files'/name
        assert not dst.exists()
        dst.write_bytes(data)
        rows.append(dict(origin=str(p), bytes=len(data), SHA256=sha(data),
            archive_path=REL+'/files/'+name, archived_SHA256=sha(data), archive_status='complete_UTF8_exact_bytes'))
    put(DEST/'RESUME_ADDITIONS_INDEX.json', dict(epoch=time.time(), previous_index_not_modified=True,
        no_original_capture_or_CPU_case_rerun=True, entries=rows,
        justification='Preserve original CRCRLF publication and archive refusal; add exact byte-written source segments. No whitespace normalization of frozen evidence.'))
    git('add','--',REL)
    staged=git('diff','--cached','--name-only').splitlines()
    assert all(x.startswith(REL+'/') for x in staged)
    for name in staged:
        data=git('show', ':'+name, binary=True)
        assert data==(G/name).read_bytes()
        if name.endswith('.py'):
            ast.parse(data.decode('utf-8-sig'))
        elif name.endswith('.json'):
            json.loads(data)
    git('commit','-m','Record H1 closure planning mismatch and source-only corrections')
    commit=git('rev-parse','HEAD')
    assert git('rev-parse','HEAD^')==BASE and commit!=BASE
    print(json.dumps(dict(stage='committed_existing_staged_supplement', commit=commit,
        original_refusal_and_publication_error_preserved=True)),flush=True)
    git('push','origin','HEAD:refs/heads/main')
    for row in index['entries']+rows:
        if row['archive_status']=='complete_UTF8_exact_bytes':
            data=git('show','HEAD:'+row['archive_path'],binary=True)
            assert sha(data)==row['SHA256'] and len(data)==row['bytes']
    committed=git('ls-tree','-r','--name-only','HEAD','--',REL).splitlines()
    for name in committed:
        assert git('show','HEAD:'+name,binary=True)==(G/name).read_bytes()
    assert tags_local()==old_tags
    assert remote()==(commit,old_tags)
    assert not git('status','--porcelain=v1')
    print(json.dumps(dict(passed=True,commit=commit,remote_main=commit,
        old_tag_objects_and_peels_preserved=len(old_tags),new_tags=0,
        verified_new_committed_blobs=len(committed),exact_text_entries=len(index['entries'])+len(rows),
        repository_clean=True,archive_path=REL,no_new_learning_or_binary_model_read_for_Git=True)),flush=True)


if __name__=='__main__':
    main()
