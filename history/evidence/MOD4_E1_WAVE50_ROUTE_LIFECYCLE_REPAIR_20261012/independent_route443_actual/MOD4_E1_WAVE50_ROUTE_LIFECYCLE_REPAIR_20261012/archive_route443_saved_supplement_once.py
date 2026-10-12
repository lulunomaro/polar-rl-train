from archive_route443_actual_stage_once import *

def main():
    receipt=json.loads((R/'ROUTE443_STAGE_GIT_RECORDED.json').read_bytes());assert receipt['remote_main_tag_peeled_verified']
    assert not base.gitio.g('status','--porcelain') and not base.gitio.g('diff','--cached','--name-only')
    old=base.gitio.refs();dest=REPO/'history/evidence'/D.name/('ordinary_supplement_'+str(time.time_ns()))
    rows,files=base.capture(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in files),capture_output=True,check=True)
    base.gitio.g('commit','-m','Supplement independent443 own reports and verified stage receipt')
    base.gitio.g('push','origin','HEAD');head=base.gitio.g('rev-parse','HEAD');base.verify(rows,old,head)
    tracked=set(base.gitio.g('ls-files').splitlines())
    latest={row['source_path']:row for row in rows}
    for folder in base.FOLDERS:
        for p in folder.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            row=latest[str(p.resolve())];assert row['sha256']==H(p.read_bytes())
            if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
            else:assert row['capture']=='large_actual_path_size_SHA_index_only'
    # Final verification lives in tool output; no infinite saved-receipt recursion.
    print(json.dumps(dict(commit=head,remote_main_verified=True,stage_tag=receipt['tag'],stage_tagobject=receipt['tagobject'],stage_peeled=receipt['commit'],all_old_tags_preserved=len(old),actual_current_saved_sources=len(rows),all_current_files_tracked_or_actual_large_SHA_index=True,no_new_record_or_tag=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_SUPPLEMENT_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_record_commit_replay=True));raise
