"""Archive actual attempts through the canonical helper in the task-private clone.

Use Git plumbing for this intentionally unpopulated partial clone. --sync-existing
only retries the already-created objects if a push fails; never creates a new trial.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=Path(r'C:\Users\lulu\.codex\scratch\sim2real_20261113\polar')
REL=Path('history/reviews/20261113-mod4v3-dm3519-r1-deploy')
ID='mod4v3-dm3519-r1-deploy'
TAG='trial-20261113-'+ID
def git(*args,data=None):
    env=os.environ.copy();env['GIT_NO_LAZY_FETCH']='1'
    p=subprocess.run(['git','-c','http.version=HTTP/1.1','-c','diff.renames=false','-c','status.renames=false','-C',str(REPO),*args],input=data,capture_output=True,text=True,encoding='utf-8',env=env,check=True)
    return p.stdout.strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sync():
    commit=git('rev-parse','HEAD');tag=git('rev-parse','refs/tags/'+TAG)
    assert git('rev-parse',TAG+'^{}')==commit
    git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
    actual=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines())
    assert actual['refs/heads/main']==commit and actual['refs/tags/'+TAG]==tag and actual['refs/tags/'+TAG+'^{}']==commit,actual
    print(json.dumps(dict(commit=commit,tag=TAG,annotated_tag_object=tag,remote_main_tag_peeled_verified=True),indent=2))
if __name__=='__main__':
    if '--sync-existing' in sys.argv:sync();sys.exit(0)
    assert git('branch','--show-current')=='main'
    if '--resume-before-commit' in sys.argv:
        # Only resume this task's uncommitted draft. Existing commits/tags are immutable.
        assert not git('tag','--list',TAG)
        staged=git('diff-index','--cached','--no-renames','--name-only','-z','HEAD').split('\0')
        record_rel='history/experiments/20261113-'+ID+'.json'
        assert all(not p or p.startswith(REL.as_posix()+'/') or p==record_rel for p in staged)
        prior=ROOT/'reports/superseded/archive_attempt1_uncommitted_record.json'
        generated=REPO/record_rel
        assert prior.read_bytes()==generated.read_bytes()
        git('read-tree','HEAD')  # Index only; no checkout or active workspace changes.
        generated.unlink()    # Preserved above; not a committed experiment record.
    else:
        assert not git('diff-index','--cached','--no-renames','--name-only','HEAD')
        assert not (REPO/REL).exists(),'Do not overwrite an earlier stage.'
    assert (ROOT/'DELIVERY_ZIP.json').exists(),'Finalize the reviewable delivery first.'
    base=git('rev-parse','HEAD')
    remote=git('ls-remote','origin','refs/heads/main').split()[0]
    assert remote==base,'Remote advanced; update the private clone/index without touching active checkouts.'
    helper=REPO/'archive_tools/record_experiment.py'
    sys.path.insert(0,str(helper.parent))
    spec=importlib.util.spec_from_file_location('_record_mod4_dm3519_deployment',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    patched={r['path'].replace('\\','/') for r in json.loads((ROOT/'FIRMWARE_PATCHES.json').read_text(encoding='utf-8'))}
    selected=[];rows=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.is_symlink():continue
        local=p.relative_to(ROOT);parts=local.parts
        if any(v in parts for v in ('.git','__pycache__','build','install','toolchain')):continue
        if parts[:2]==('reference','rmcs_auto_aim_v2'):continue
        if local.name=='ARTIFACT_INDEX.json':continue
        include=False
        if len(parts)==1 and p.suffix.lower() in ('.md','.json'):include=True
        if parts[0] in ('docs','tools','tests','upper','reports','model','reference'):include=True
        if parts[0]=='firmware':
            include=local.as_posix().removeprefix('firmware/') in patched or parts[1:3]==('application','mod4_rl')
        if p.name=='policy_weights.h' or p.suffix.lower() in ('.onnx','.pt','.pth','.npz','.npy','.pdf','.axf','.hex','.lib','.zip','.exe','.dll','.so'):include=False
        if not include:continue
        raw=p.read_bytes();row=dict(source=str(p),relative=local.as_posix(),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())
        dest=REPO/REL/local;dest.parent.mkdir(parents=True,exist_ok=True)
        try:content=raw.decode('utf-8')
        except UnicodeDecodeError:content=None
        if content is not None:
            redacted,count=module.redact(content)
            output=redacted.encode('utf-8') if redacted!=content else raw
            row.update(status='redacted' if redacted!=content else 'full',redaction_counts=count if redacted!=content else {})
        else:output=raw;row['status']='full'
        dest.write_bytes(output);row.update(archive=(REL/local).as_posix(),archive_SHA256=sha(dest));rows.append(row);selected.append((REL/local).as_posix())
    manifest=json.loads((ROOT/'DELIVERY_MANIFEST.json').read_text(encoding='utf-8'))
    copied={r['relative'] for r in rows}
    external=[dict(**row,status='external_original_index') for row in manifest['files'] if row['path'] not in copied]
    index=ROOT/'ARTIFACT_INDEX.json'
    index.write_text(json.dumps(dict(stage=ID,archived=rows,external_delivery_artifacts=external,delivery=json.loads((ROOT/'DELIVERY_ZIP.json').read_text(encoding='utf-8')),manifest_self_hash_not_recursive=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REPO/REL/index.name).write_bytes(index.read_bytes());selected.append((REL/index.name).as_posix())
    def archive_git(*args):
        if args[0]=='commit':
            assert args[1]=='-m';tree=git('write-tree','--missing-ok')
            changed=git('diff-tree','--no-commit-id','--name-only','--no-renames','-z','-r',base,tree).rstrip('\0').split('\0')
            assert set(changed)==set(selected)|{'history/experiments/20261113-'+ID+'.json'}
            commit=git('commit-tree',tree,'-p',base,data=args[2]+'\n');git('update-ref','refs/heads/main',commit,base);return commit
        return git(*args)
    module.git=archive_git
    sys.argv=[str(helper),'--id',ID,'--title','Port selected MOD4v3 R1 policy to DM3519 wheel firmware and RMCS chassis bridge',
              '--kind','deployment','--note-file',str(ROOT/'README.md'),
              '--validation','Offline implementation only: model zero; four DM8009 + two DM3519/individual DM3520; retained failures; ARMCC full build; 16 golden vectors; CAN/controller tests; real ROS2 and RMCS plugin PTY loopbacks; calibration false; no hardware or training',
              '--files',*selected]
    module.main();print(json.dumps(dict(archived_files=len(selected),indexed_external_files=len(external))))
    sync()
