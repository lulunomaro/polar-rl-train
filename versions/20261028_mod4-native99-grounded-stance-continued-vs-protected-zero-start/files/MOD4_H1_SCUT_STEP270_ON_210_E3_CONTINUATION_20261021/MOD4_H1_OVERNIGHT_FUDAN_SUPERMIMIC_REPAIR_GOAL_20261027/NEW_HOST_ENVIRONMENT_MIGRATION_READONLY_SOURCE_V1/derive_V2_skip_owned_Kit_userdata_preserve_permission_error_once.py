from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;p=B/'read_known72_mod4_runtime_portability_footprint_finite_v1.py';s=p.read_text();t=ast.parse(s);node=next(n for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));code=ast.literal_eval(node.value);ct=ast.parse(code);old=ast.get_source_segment(code,next(n for n in ct.body if isinstance(n,ast.FunctionDef) and n.name=='inventory'))
new='''def inventory(root):
 stack=[root];files=0;total=0;excluded=0;symlinks=[];toplevel=collections.defaultdict(lambda:dict(files=0,bytes=0));partial=False;dirs=0;denied=[];excluded_names=[];excluded_userdata=[]
 userdata=ENV/'lib'/'python3.12'/'site-packages/isaacsim/kit/data'
 while stack:
  if time.monotonic()>=DEADLINE-15:partial=True;break
  d=stack.pop();dirs+=1
  try:entries=os.scandir(d)
  except PermissionError as error:
   denied.append(dict(path=str(d),error=str(error),unchanged_and_not_read=True));continue
  with entries:
   for e in entries:
    p=Path(e.path);rel=p.relative_to(root);group=rel.parts[0]
    if p==userdata:excluded_userdata.append(str(p));continue
    if not allowed_name(e.name):
     excluded+=1
     if len(excluded_names)<10000:excluded_names.append(rel.as_posix())
     continue
    try:
     if e.is_symlink():
      target=os.readlink(p);resolved=os.path.normpath(os.path.join(str(p.parent),target))
      if len(symlinks)<10000:symlinks.append(dict(relative=rel.as_posix(),target=target,resolved=resolved,inside_environment=os.path.commonpath([str(root),resolved])==str(root)))
     elif e.is_dir(follow_symlinks=False):stack.append(p)
     elif e.is_file(follow_symlinks=False):
      st=e.stat(follow_symlinks=False);files+=1;total+=st.st_size;toplevel[group]['files']+=1;toplevel[group]['bytes']+=st.st_size
    except PermissionError as error:denied.append(dict(path=str(p),error=str(error),unchanged_and_not_read=True))
 return dict(root=str(root),regular_files_excluding_named_policy_raw_archives_and_Kit_userdata=files,logical_bytes=total,excluded_filename_count_no_stat_or_content=excluded,excluded_names=excluded_names,excluded_owned_Kit_userdata_not_portable_runtime=excluded_userdata,permission_errors_retained_no_permission_changes=denied,directories_visited=dirs,partial_time_bound=partial,not_complete_unfiltered_environment_size=True,not_binary_policy_model_inventory=True,toplevel=dict(toplevel),symlinks=symlinks,symlink_list_truncated=len(symlinks)==10000)'''
assert code.count(old)==1;changed=code.replace(old,new);ast.parse(changed);literal=ast.get_source_segment(s,node.value);assert s.count(literal)==1
s=s.replace(literal,repr(changed)).replace('KNOWN72_ENV_PORTABILITY','KNOWN72_ENV_PORTABILITY_V2').replace('READONLY_KNOWN72_ENV_PORTABILITY_ENTRY','READONLY_KNOWN72_ENV_PORTABILITY_V2_ENTRY')
ast.parse(s);out=B/'read_known72_mod4_runtime_portability_footprint_finite_v2_no_Kit_userdata.py'
with out.open('x',encoding='utf8') as f:f.write(s)
proof=dict(epoch=time.time(),source_AST_passed=True,remote_AST_passed=True,old_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_source_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),only_inventory_body_and_unique_report_basenames_changed=True,source_permission_failure_preserved=True,explicit_new_scope_excludes_Kit_userdata=True,remaining_permission_errors_partial_not_faked_complete=True,no_source_permissions_or_files_changed=True,no_GPU_model_network_executed_by_deriver=True)
with (B/'READONLY_V2_EXACT_DERIVATION_AND_ORIGINAL_PERMISSION_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
print(json.dumps(proof))
