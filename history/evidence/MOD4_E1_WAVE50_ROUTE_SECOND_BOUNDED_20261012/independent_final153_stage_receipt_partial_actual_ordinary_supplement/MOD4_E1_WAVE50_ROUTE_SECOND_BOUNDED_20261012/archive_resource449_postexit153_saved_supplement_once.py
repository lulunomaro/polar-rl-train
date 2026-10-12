from archive_independent449_final153_repair_stage_once import *

def main():
    receipt=json.loads((R/'RESOURCE449_POSTEXIT153_STAGE_GIT_RECORDED.json').read_bytes());assert receipt['remote_main_tag_peeled_verified']
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    old=archive.gitio.refs();dest=REPO/'history/evidence'/D.name/'independent_final153_stage_receipt_partial_actual_ordinary_supplement'
    rows,files=archive.capture(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+bytes([0]) for p in files),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Supplement independent449 final stage receipt and actual153 partial review')
    archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
    tracked=set(archive.gitio.g('ls-files').splitlines());index={row['source_path']:row for row in rows}
    for folder in archive.FOLDERS:
        for p in folder.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            row=index[str(p.resolve())];assert row['sha256']==H(p.read_bytes())
            if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
            else:assert row['capture']=='large_actual_path_size_SHA_index_only'
    print(json.dumps(dict(commit=head,remote_main_verified=True,stage_tag=receipt['tag'],stage_tagobject=receipt['tagobject'],stage_peeled=receipt['commit'],all_old_tags_preserved=len(old),all_current_saved_source_reports_tracked_or_actual_large_SHA_index=True,sources=len(rows),no_new_record_or_tag=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_POSTEXIT153_SUPPLEMENT_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True));raise
