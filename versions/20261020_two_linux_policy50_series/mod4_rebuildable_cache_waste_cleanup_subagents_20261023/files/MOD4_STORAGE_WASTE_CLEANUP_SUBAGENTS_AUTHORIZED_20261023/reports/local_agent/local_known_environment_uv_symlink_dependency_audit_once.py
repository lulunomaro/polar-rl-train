from pathlib import Path
import os,json,time

OUT=Path(__file__).resolve().parent; REPORT=OUT/'KNOWN_INSTALLED_ENV_UV_CACHE_REPARSE_DEPENDENCIES_READ_ONLY_ACTUAL.json'
assert not REPORT.exists(),'once consumed'
start=time.time(); errors=[]; reparses=[]; results=[]
roots=[Path(r'C:/Users/lulu/Desktop/claude/mjcf/.venv'),Path(r'C:/Users/lulu/AppData/Local/Programs/Python/Python314/Lib/site-packages'),Path(r'C:/Users/lulu/miniconda3/Lib/site-packages'),Path(r'C:/Users/lulu/AppData/Roaming/uv/tools'),Path(r'C:/Users/lulu/.local/share/uv/tools')]
envroot=Path(r'C:/Users/lulu/miniconda3/envs')
if envroot.is_dir():
    for p in envroot.iterdir():
        if p.is_dir():roots.append(p/'Lib/site-packages')
for root in roots:
    if not root.exists():results.append({'path':str(root),'exists':False});continue
    count=0;stack=[root];partial=False
    while stack:
        if time.time()-start>90:partial=True;break
        folder=stack.pop()
        try:
            with os.scandir(folder) as it:entries=list(it)
        except OSError as e:errors.append({'path':str(folder),'error':repr(e)});continue
        for ent in entries:
            p=Path(ent.path)
            try:
                st=ent.stat(follow_symlinks=False);count+=1
                if ent.is_symlink() or (getattr(st,'st_file_attributes',0)&0x400):
                    try:target=os.readlink(p)
                    except OSError as e:target=None;errors.append({'path':str(p),'error':repr(e),'stage':'readlink reparse only'})
                    candidate=Path(target) if target else None
                    if candidate and not candidate.is_absolute():candidate=p.parent/candidate
                    target_norm=os.path.normcase(os.path.abspath(candidate)) if candidate else None
                    uvbase=os.path.normcase(os.path.abspath(r'C:/Users/lulu/AppData/Local/uv/cache'))
                    depends=target_norm is not None and (target_norm==uvbase or target_norm.startswith(uvbase+os.sep))
                    reparses.append({'path':str(p),'raw_link_target':target,'points_into_known_uv_cache':depends,'not_followed':True});continue
                if ent.is_dir(follow_symlinks=False):stack.append(p)
            except OSError as e:errors.append({'path':str(p),'error':repr(e)})
    results.append({'path':str(root),'exists':True,'entries_metadata_read':count,'partial_90s_bound':partial})
out={'scope':'Known MOD4 .venv, global Python314, Conda env site-packages, standard uv tools only; metadata and reparse targets only, never contents/credential/session files. No deletion.','started_epoch':start,'ended_epoch':time.time(),'roots':results,'reparse_points':reparses,'known_uv_cache_dependencies':[r for r in reparses if r['points_into_known_uv_cache']],'errors':errors,'limitations':['Not a whole-computer proof: unknown custom environments or .pth/editable import hooks were not content-scanned.','Hardlinks are not symlinks and removing a cache hardlink preserves installed paths. Logical cache size can overestimate physical reclaim.','Only native uv clean/prune with in-use checks, exact cache-dir, offline, no-config, no --force is recommended.','This audit does not authorize deleting any environments.']}
REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(REPORT),'seconds':time.time()-start,'roots':results,'reparse_count':len(reparses),'known_uv_cache_dependencies':len(out['known_uv_cache_dependencies']),'errors':len(errors)},ensure_ascii=False))
