from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;p=N/'install_two101_producer_reference_metadata_extension_CPU_once.py';s=p.read_text();node=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='PRE' for y in x.targets));pre=ast.literal_eval(node.value)
a="stage=owned/'MOD4_TWO101_USER_FLAT20_NATIVE_2610v100'";assert pre.count(a)==1;pre=pre.replace(a,"stage=Path(v['old_owner_root']).parent");ast.parse(pre)
lines=s.splitlines(keepends=True);s=''.join(lines[:node.lineno-1])+'PRE='+repr(pre)+'\n'+''.join(lines[node.end_lineno:]);a="dict(root=root,GPU=spec['GPU_UUID'],mode=mode,manifest=manifest,old100_root=";assert s.count(a)==1;s=s.replace(a,"dict(root=root,GPU=spec['GPU_UUID'],mode=mode,manifest=manifest,old_owner_root=launched['owner_root'],old100_root=")
s=s.replace('TWO101_INSTALL_SOURCE_CPU_CONSUMED_ACTUAL.json','TWO101_INSTALL_V2_SOURCE_CPU_CONSUMED_ACTUAL.json').replace('TWO101_SOURCE_INSTALL_ORIGINAL_ERROR_ACTUAL.json','TWO101_SOURCE_INSTALL_V2_ORIGINAL_ERROR_ACTUAL.json');ast.parse(s)
entry=N/'install_two101_previous_owner_path_corrected_metadata_CPU_v2_once.py';entry.write_text(s,encoding='utf8')
(N/'reports/ORIGINAL101_INSTALLER_PRECOPY_PREVIOUS_OWNER_PATH_ERROR_AND_V2_DATA_BINDING_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),old_before_remote_root_creation_or_copy_or_CPU=True,old_error_and_once_preserved=True,reason='Global label rename also renamed a historical original100 owner directory literal',new_previous_owner_path_from_original_actual_launch_receipt=True,entry=str(entry),SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),original_account_and_resource_guards_kept=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,entry=str(entry))))
