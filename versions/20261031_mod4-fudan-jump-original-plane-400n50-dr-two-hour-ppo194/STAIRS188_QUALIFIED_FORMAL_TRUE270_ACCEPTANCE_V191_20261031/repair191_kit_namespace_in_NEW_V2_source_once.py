"""Narrow repair of the proved pre-App namespace assertion, in NEW V2 only."""
from pathlib import Path
import ast,hashlib,json,time

B=Path(__file__).resolve().parent
V=B/'V2_KIT_NAMESPACE_BINDING_REPAIR';V.mkdir(exist_ok=False);(V/'reports').mkdir()
oldroot='/mnt/mod4_linux_durable_20261013/MOD4_STAIRS188_FORMAL40050_TRUE270_EVAL_20261031v191'
newroot=oldroot+'_v2'
oldexpected='/mnt/mod4_linux_durable_20261013/MOD4_DELIVERED4999_PLAN40050_DR_STEP270_EVAL_20261031v191_v2/kit_isolation'
actual=json.loads((B/'reports/ROOT191V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes())
assert actual['original_waited'] and actual['returncode']==1 and actual['private_EX_released']
error=next(json.loads(row['UTF8']) for row in actual['full_UTF8'] if row['relative'].endswith('ORIGINAL_EVALUATION_ERROR.json'))
assert 'zonglin2_app_launcher.py' in error['traceback'] and 'assert root == expected and root.is_dir()' in error['traceback']
rows=[]
for name in ('evaluate191_qualified188_actor40050_step270_once.py','FROZEN_EVAL191_TASK.json',
             'zonglin2_app_launcher.py','remote191_postcopy_and_frozen_eval.txt',
             'install_evaluate191_qualified188_frozen_once.py'):
    raw=(B/name).read_bytes();value=raw.decode('utf8')
    if name=='zonglin2_app_launcher.py':
        assert value.count(oldexpected)==1
        value=value.replace(oldexpected,newroot+'/kit_isolation')
    elif name in ('remote191_postcopy_and_frozen_eval.txt','install_evaluate191_qualified188_frozen_once.py'):
        assert oldroot in value
        value=value.replace(oldroot,newroot)
        if name.startswith('install_'):
            assert 'T=N.parent;W=T.parent' in value
            value=value.replace('T=N.parent;W=T.parent','T=N.parent.parent;W=T.parent')
            # Resource72 allocation snapshot already returned in V1; this new
            # finite needs fresh authority, not another unrelated GPU query.
            begin=value.index(',resources72_GPU_UUID_free_util=')
            end=value.index('unknown_process_or_GPU_PID_reads=0',begin)+len('unknown_process_or_GPU_PID_reads=0')
            value=value[:begin]+value[end:]
    elif name=='FROZEN_EVAL191_TASK.json':
        task=json.loads(value)
        task['new_V2_purpose']='Original V1 consumed pre-App namespace assertion; model reads0/physics0. V2 fixes only own Kit storage path and uses a new output root.'
        value=json.dumps(task,indent=2,ensure_ascii=False)
    if name.endswith('.py') or name.endswith('.txt'):ast.parse(value)
    dest=V/name;dest.write_text(value,encoding='utf8',newline='\n')
    new=dest.read_bytes();rows.append(dict(name=name,before_SHA=hashlib.sha256(raw).hexdigest(),new_SHA=hashlib.sha256(new).hexdigest(),bytes=len(new)))
launcher=ast.parse((V/'zonglin2_app_launcher.py').read_text('utf8'))
expected=next(node.value.args[0].value for node in ast.walk(launcher) if isinstance(node,ast.Assign)
              and any(isinstance(target,ast.Name) and target.id=='expected' for target in node.targets))
assert expected==newroot+'/kit_isolation'
assert (B/'evaluate191_qualified188_actor40050_step270_once.py').read_bytes()==(V/'evaluate191_qualified188_actor40050_step270_once.py').read_bytes()
manifest=json.loads((B/'FROZEN_EVAL191_COMPLETE_MANIFEST.json').read_bytes())
manifest['files']=[dict(relative=name,local_relative=name,bytes=(V/name).stat().st_size,
    SHA=hashlib.sha256((V/name).read_bytes()).hexdigest()) for name in
    ('evaluate191_qualified188_actor40050_step270_once.py','FROZEN_EVAL191_TASK.json','zonglin2_app_launcher.py')]
manifest['new_namespace_V2_exact_Kit_binding']=dict(remote=newroot,expected_kit_root=expected,
                                                  original_error_retained=True,source_model_or_physics_changed=False)
with (V/'FROZEN_EVAL191_COMPLETE_MANIFEST.json').open('x',encoding='utf8') as f:json.dump(manifest,f,indent=2,ensure_ascii=False)
with (V/'reports/ROOT191_V2_KIT_SOURCE_REPAIR_FROZEN_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),passed_source=True,original_V1_error=error,original_model_and_physics_calls_before_failure=0,
                   original_V1_waited_and_private_EX_released=True,new_root=newroot,expected_kit=expected,
                   evaluator_bytes_unchanged=True,source_changes=rows,model_reads=0,SDK=0,remote=0),f,indent=2)
print(json.dumps(dict(passed_source=True,new_namespace=newroot,exact_Kit_binding=True,
                      evaluator_byte_unchanged=True,new_entry=str(V/'install_evaluate191_qualified188_frozen_once.py'))))
