from pathlib import Path
import os,json,time,subprocess,shutil,hashlib,sys

OUT=Path(__file__).resolve().parent
INTENT=OUT/'EXACT_UV_NATIVE_CACHE_CLEAN_BEFORE_COMMAND_INTENT_ACTUAL.json'
COMPLETE=OUT/'EXACT_UV_NATIVE_CACHE_CLEAN_COMPLETE_ACTUAL.json'
STARTED=OUT/'EXACT_UV_NATIVE_CACHE_CLEAN_STARTED_ACTUAL.json'
assert not INTENT.exists() and not STARTED.exists() and not COMPLETE.exists(),'intent/started/completion consumed: never rerun clean'
UV=Path(r'C:/Users/lulu/AppData/Local/Programs/Python/Python314/Scripts/uv.exe')
CACHE=Path(r'C:/Users/lulu/AppData/Local/uv/cache')
EXACT=Path(r'C:/Users/lulu/AppData/Local/uv/cache')
assert CACHE.is_absolute() and CACHE==EXACT and os.path.normcase(str(CACHE.resolve(strict=True)))==os.path.normcase(str(CACHE))
assert CACHE.is_dir() and not CACHE.is_symlink() and not CACHE.is_junction()
PARENT_UV_CACHE=CACHE.parent
START=time.time()
def write(path,obj):
    data=json.dumps(obj,ensure_ascii=False,indent=2).encode('utf-8')
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(data).hexdigest()
def metadata(root):
    count=0;total=0;dirs=0;errors=[];reparse=[];top={};stack=[root]
    if not root.exists():return {'exists':False,'files':0,'logical_bytes':0,'errors':[],'reparse_skipped':[]}
    while stack:
        p=stack.pop();dirs+=1
        try:
            with os.scandir(p) as it:entries=list(it)
        except OSError as e:errors.append({'path':str(p),'error':repr(e)});continue
        for ent in entries:
            q=Path(ent.path)
            try:
                st=ent.stat(follow_symlinks=False)
                if ent.is_symlink() or getattr(st,'st_file_attributes',0)&0x400:reparse.append({'path':str(q),'not_followed':True});continue
                if ent.is_dir(follow_symlinks=False):stack.append(q);continue
                if not ent.is_file(follow_symlinks=False):continue
                count+=1;total+=st.st_size;parts=q.relative_to(root).parts;k=parts[0] if len(parts)>1 else '[root files]'
                row=top.setdefault(k,{'bytes':0,'files':0});row['bytes']+=st.st_size;row['files']+=1
            except OSError as e:errors.append({'path':str(q),'error':repr(e)})
    return {'exists':True,'files':count,'directories_including_root':dirs,'logical_bytes':total,'top_children':top,'errors':errors,'reparse_skipped':reparse}
env_report=json.loads((OUT/'KNOWN_INSTALLED_ENV_UV_CACHE_REPARSE_DEPENDENCIES_READ_ONLY_ACTUAL.json').read_text(encoding='utf-8'))
cli_report=json.loads((OUT/'UV_OFFICIAL_CACHE_CLEAN_HELP_VERSION_LOCAL_PROCESS_READ_ONLY_ACTUAL.json').read_text(encoding='utf-8-sig'))
known_paths=[Path(r['path']) for r in env_report['roots'] if r['exists']]
known_paths += [Path(r'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'),Path(r'C:/Users/lulu/miniconda3/python.exe'),Path(r'C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe')]
before_env=[{'path':str(p),'exists':p.exists(),'is_dir':p.is_dir(),'is_symlink':p.is_symlink(),'is_junction':p.is_junction()} for p in known_paths]
assert not env_report['known_uv_cache_dependencies'] and not env_report['errors'] and all(not r.get('partial_90s_bound') for r in env_report['roots'])
before=metadata(CACHE)
assert not before['errors'] and not before['reparse_skipped'],'cache metadata gap/reparse: keep source, no clean'
command=[str(UV),'cache','clean','--cache-dir',str(CACHE),'--offline','--no-config','--no-python-downloads']
free_before=shutil.disk_usage('C:/').free
intent={'authorization':'Original human: this turn use subagents to inspect space and actually clean unused waste. Root explicitly delegated ONLY this exact native uv cache clean after read-only env-dependency checks; no other package/env changes, no downloads, no force.','started_epoch':START,'exact_existing_cache_root':str(CACHE),'cache_root_resolved':str(CACHE.resolve()),'before_fresh_metadata':before,'C_free_before_bytes':free_before,'uv_actual_CLI_help_version':cli_report,'known_env_dependency_report':str(OUT/'KNOWN_INSTALLED_ENV_UV_CACHE_REPARSE_DEPENDENCIES_READ_ONLY_ACTUAL.json'),'known_env_check_scope_limitations':env_report['limitations'],'known_paths_before':before_env,'command':command,'child_only_environment_override':{'UV_LOCK_TIMEOUT':'10'},'native_lock_required_no_force':True,'native_cache_internals_not_manually_removed':True,'installed_environment_paths_not_targeted':True,'cache_data_unlinks_irrecoverable_but_dependency_cache_rebuildable':True,'physical_reclaimed_bytes_not_assumed_from_logical_cache_total':True,'full_file_content_hash_not_read':True}
intent_sha=write(INTENT,intent)
cim_code=r"$p=@(Get-CimInstance Win32_Process | Where-Object {($_.Name -match '^(uv|uvx|pip|pip3|conda|mamba)(\.exe)?$') -or (($_.Name -match '^(python|pythonw)(\.exe)?$') -and ($_.CommandLine -match '(^|\s)(-m\s+pip|pip\.py|pip\s+install|uv\s+(sync|pip|add|tool))'))} | Select-Object ProcessId,Name,ExecutablePath,CreationDate); [PSCustomObject]@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000; matching_installers=$p; installer_count=$p.Count} | ConvertTo-Json -Depth 5 -Compress"
cim=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cim_code],capture_output=True,text=True,encoding='utf-8',errors='replace')
if cim.returncode:
    write(COMPLETE,{'passed':False,'command_started':False,'intent_SHA256':intent_sha,'CIM_returncode':cim.returncode,'CIM_stdout':cim.stdout,'CIM_stderr':cim.stderr,'reason':'fresh installer check failed; no retry'})
    sys.exit(1)
fresh=json.loads(cim.stdout)
write(OUT/'EXACT_UV_NATIVE_CACHE_CLEAN_FRESH_INSTALLER_CIM_ACTUAL.json',fresh)
if fresh['installer_count']!=0:
    write(COMPLETE,{'passed':False,'command_started':False,'intent_SHA256':intent_sha,'fresh_installer_CIM':fresh,'reason':'installer in use; skip/no force/no retry'})
    sys.exit(2)
env=os.environ.copy();env['UV_LOCK_TIMEOUT']='10'
stdout_path=OUT/'UV_NATIVE_CACHE_CLEAN_FULL_STDOUT_ACTUAL.txt';stderr_path=OUT/'UV_NATIVE_CACHE_CLEAN_FULL_STDERR_ACTUAL.txt'
write(STARTED,{'epoch':time.time(),'intent':str(INTENT),'intent_SHA256':intent_sha,'command':command,'fresh_installer_count':0,'only_child_env_override':{'UV_LOCK_TIMEOUT':'10'}})
with stdout_path.open('xb') as so,stderr_path.open('xb') as se:
    proc=subprocess.Popen(command,stdout=so,stderr=se,env=env,cwd=str(PARENT_UV_CACHE))
    code=proc.wait();so.flush();os.fsync(so.fileno());se.flush();os.fsync(se.fileno())
command_returned_epoch=time.time()
free_after=shutil.disk_usage('C:/').free
residual=metadata(CACHE)
after_env=[{'path':str(p),'exists':p.exists(),'is_dir':p.is_dir(),'is_symlink':p.is_symlink(),'is_junction':p.is_junction()} for p in known_paths]
stdout_bytes=stdout_path.read_bytes();stderr_bytes=stderr_path.read_bytes()
out={'passed':code==0 and all(p['exists'] for p in after_env),'command_actual_returned':True,'command_returncode':code,'started_epoch':START,'command_returned_epoch':command_returned_epoch,'ended_epoch':time.time(),'intent':str(INTENT),'intent_SHA256':intent_sha,'command':command,'native_in_use_checks_no_force':True,'C_free_before_bytes':free_before,'C_free_after_native_return_bytes':free_after,'C_free_whole_drive_snapshot_difference_bytes':free_after-free_before,'physical_difference_scope':'Whole drive concurrent snapshot difference, not a byte-exact causal storage proof; native command result and logical metadata are separately retained.','before_fresh_metadata':before,'cache_residual_after_command':residual,'stdout_path':str(stdout_path),'stdout_bytes':len(stdout_bytes),'stdout_SHA256':hashlib.sha256(stdout_bytes).hexdigest(),'stderr_path':str(stderr_path),'stderr_bytes':len(stderr_bytes),'stderr_SHA256':hashlib.sha256(stderr_bytes).hexdigest(),'known_environment_paths_after':after_env,'all_known_environment_paths_still_exist':all(p['exists'] for p in after_env),'known_env_limitations':env_report['limitations'],'no_installed_env_or_dependencies_mutation_command':True,'no_other_cache_training_host_Git_protected_raw_model_log_source_mutation':True,'consumed_never_rerun_this_helper_or_cache_clean_batch':True}
write(COMPLETE,out)
print(json.dumps({'report':str(COMPLETE),'returncode':code,'before_files':before['files'],'before_logical_bytes':before['logical_bytes'],'residual_files':residual['files'],'residual_logical_bytes':residual['logical_bytes'],'C_free_before_bytes':free_before,'C_free_after_bytes':free_after,'C_free_difference_bytes':free_after-free_before,'all_known_env_paths_still_exist':out['all_known_environment_paths_still_exist']}))
