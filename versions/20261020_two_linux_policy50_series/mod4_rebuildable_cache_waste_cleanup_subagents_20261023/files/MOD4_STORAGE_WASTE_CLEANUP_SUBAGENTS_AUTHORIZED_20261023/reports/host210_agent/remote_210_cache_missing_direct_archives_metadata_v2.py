"""Exact missing-only direct package-download metadata. No cleanup/content reads."""
import os, stat, time, json, urllib.parse
start=time.monotonic();epoch=time.time();out={'schema':'210_cache_direct_archive_missing_metadata_v2','epoch':epoch,'read_only':True,'no_model_raw_hash_PT_GPU_process_budget_or_training_change':True,'only_conda_url_registry_read_in_memory_no_URL_output':True,'roots':[],'errors':[]}
for root in ['/mnt/mod4_linux_durable_20261013/anaconda/pkgs','/home/egde/anaconda3/pkgs']:
    r={'path':root,'complete':False,'archives':[],'excluded_partial_names':[]};out['roots'].append(r)
    try:
        rs=os.lstat(root)
        if not stat.S_ISDIR(rs.st_mode) or stat.S_ISLNK(rs.st_mode): raise RuntimeError('Root must be a real directory')
        r['device']=rs.st_dev
        url_names=set(); urls=os.path.join(root,'urls.txt');r['known_conda_urls_sentinel_regular']=False
        try:
            us=os.lstat(urls)
            if stat.S_ISREG(us.st_mode) and not stat.S_ISLNK(us.st_mode) and us.st_size<16*1024*1024:
                r['known_conda_urls_sentinel_regular']=True
                with open(urls,'r',encoding='utf-8',errors='replace') as f:
                    for line in f:
                        try:
                            # Do not save or output scheme, authority, query, credentials, or URL.
                            name=os.path.basename(urllib.parse.unquote(urllib.parse.urlsplit(line.strip()).path))
                            if name.endswith(('.conda','.tar.bz2')):url_names.add(name)
                        except ValueError:pass
                r['known_download_archive_basename_count']=len(url_names)
        except FileNotFoundError:pass
        for e in sorted(os.scandir(root),key=lambda e:e.name):
            if time.monotonic()-start>25: raise TimeoutError('25-second metadata bound')
            n=e.name.lower()
            if n.endswith(('.partial','.part','.download')):
                r['excluded_partial_names'].append(e.name);continue
            if not n.endswith(('.conda','.tar.bz2')):continue
            s=e.stat(follow_symlinks=False)
            if not stat.S_ISREG(s.st_mode) or s.st_dev!=rs.st_dev:continue
            x={'path':e.path,'bytes':s.st_size,'allocated_bytes':getattr(s,'st_blocks',0)*512,'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'mtime_ns':s.st_mtime_ns,'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'regular':True,'symlink':False,'class':'conda_complete_download_archive'}
            x['archive_name_matched_urls_registry_basename_only']=e.name in url_names
            x['age_seconds_at_audit']=epoch-s.st_mtime
            x['protect_modified_within_24h_or_future_timestamp']=epoch-s.st_mtime<86400
            x['safe_metadata_eligibility_only']=bool(r['known_conda_urls_sentinel_regular'] and e.name in url_names and s.st_nlink==1 and epoch-s.st_mtime>=86400)
            # Stat only; optional sibling extracted package metadata is never deleted.
            suffix='.tar.bz2' if n.endswith('.tar.bz2') else '.conda'
            sibling=os.path.join(root,e.name[:-len(suffix)],'info','index.json')
            try:
                is_=os.lstat(sibling)
                x['expanded_package_index_stat']={'path':sibling,'regular':stat.S_ISREG(is_.st_mode),'symlink':stat.S_ISLNK(is_.st_mode),'bytes':is_.st_size,'mtime_ns':is_.st_mtime_ns}
            except FileNotFoundError:x['expanded_package_index_stat']={'path':sibling,'exists':False}
            r['archives'].append(x)
        r['complete']=True
    except Exception as e:out['errors'].append({'path':root,'type':type(e).__name__,'error':str(e)})
out['elapsed_seconds']=time.monotonic()-start
print(json.dumps(out,ensure_ascii=False,separators=(',',':')))
