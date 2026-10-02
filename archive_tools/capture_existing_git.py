"""Preserve actual existing player commit metadata and text diffs without changing those repos."""
from pathlib import Path
import hashlib
import json
import subprocess
from capture_history import redact, TEXT

R=Path(__file__).resolve().parents[1]

def main():
    records=[]
    for repo in R.parent.iterdir():
        if not repo.is_dir() or not repo.name.lower().startswith(('mod4','chassis_mod4','rmuc2026')) or not (repo/'.git').exists():continue
        args=['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo)]
        def old(*a):return subprocess.check_output(args+list(a)).decode('utf8',errors='replace').strip()
        shas=old('rev-list','--reverse','--all').splitlines()
        for sha in shas:
            ident=repo.name+'-'+sha[:12]
            directory=R/'history/original-git'/ident;directory.mkdir(parents=True,exist_ok=True)
            metadata=old('show','-s','--format=%H%n%aI%n%an%n%ae%n%s',sha).splitlines()
            paths=old('show','--format=','--name-only',sha).splitlines()
            text_paths=[p for p in paths if Path(p).suffix.lower() in TEXT or Path(p).name in ('LICENSE','NOTICE')]
            patch=old('show','--format=','--no-ext-diff',sha,'--',*text_paths) if text_paths else ''
            patch,n=redact(patch)
            (directory/'text_changes.diff').write_text(patch+'\n',encoding='utf8')
            record={'original_repository':str(repo),'original_commit':metadata[0],
                    'original_author_date':metadata[1],'original_author_name':metadata[2],
                    'original_author_email':metadata[3],'original_subject':metadata[4],
                    'original_changed_paths':paths,'archived_text_patch_paths':text_paths,
                    'redactions':n,'weights_or_other_nontext_diff_not_archived':True,
                    'archive_tag':'original-'+ident,'text_patch_sha256':hashlib.sha256((patch+'\n').encode()).hexdigest(),
                    'not_a_rewritten_original_commit':True}
            (directory/'record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
            subprocess.run(['git','-C',str(R),'add','--',directory.relative_to(R).as_posix()],check=True,capture_output=True)
            message='保存原 Git 记录：'+metadata[4]+'\n\nSource: '+str(repo)+'\nOriginal commit: '+sha+'\n原作者/时间保留在证据中；本次归档提交保持真实时间。'
            subprocess.run(['git','-C',str(R),'commit','-m',message],check=True,capture_output=True)
            subprocess.run(['git','-C',str(R),'tag','-a',record['archive_tag'],'-m',message],check=True,capture_output=True)
            records.append(record)
    (R/'provenance/ORIGINAL_GIT_RECORDS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    print('Existing original Git records preserved:',len(records))

if __name__=='__main__':main()
