from archive_actual_reference_stage_once import *

def main():
    receipt=json.loads((R/'SCUT_REFERENCE_STAGE_GIT_RECORDED.json').read_bytes());assert receipt['remote_main_tag_peeled_verified'] and not gitio.g('status','--porcelain')
    old=gitio.refs();dest=DEST.parent/'poststage_receipt_supplement';rows,files=capture(dest)
    r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in files),capture_output=True,check=True)
    gitio.g('commit','-m','Supplement SCUT3060 actual stage Git receipt and complete evidence index');gitio.g('push','origin','HEAD');head=gitio.g('rev-parse','HEAD');verify(rows,old,head)
    print(json.dumps(dict(supplement_commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),all_saved_reports_source_and_poststage_receipt_tracked_SHA_exact=True,saved_sources=len(rows),working_tree_clean=not gitio.g('status','--porcelain'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_SUPPLEMENT_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_repeat_commit=True));raise
