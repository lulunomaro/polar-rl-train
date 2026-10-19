from pathlib import Path
import json,tomllib
B=Path(__file__).resolve().parent;R=B/'reports'
old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert old['status']=='ACTIVE' and '最新actual V34' in old['prompt']
note='最新prepared CPU V34B（当前实际训练仍以下V34的原两GO）：在任何新远端/GPU尝试前，独立CPU复核发现原unused repair preparer的H1旧worker绑定取错了failed hour11。H1保留source来自健康hour10，previous_runtime_root也为hour10，故normalize前一worker必须使用J/payload/h1的实际hour9 sourcefilename/Adam绑定。K/reports/PREPARED_H1_HEALTHY_RUNTIME_BINDING_MISMATCH_AND_V2_CPU_ACTUAL.json已用真实worker AST重现旧prepared mismatch并核新V2通过，未重任何GPU/Task/native/PT/费用。原future_partial_hour_repair_templates保留，不执行；仅用K/future_partial_hour_repair_templates_V2五文件，其H1共享helper仍在controller copy之后覆盖并部署前exactbytes核验。此为未执行模板修正，不冒H1已恢复；其余实际owner318576两路GO、原预算和自然闭合交接保持。\n\n'
prompt=note+old['prompt'].replace('K/future_partial_hour_repair_templates全部五文件','K/future_partial_hour_repair_templates_V2全部五文件')
args=dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
with (B/'AUTOMATION_PREPARED_HEALTHY_BINDING_V34B_ARGS.json').open('x',encoding='utf8') as stream:json.dump(args,stream,ensure_ascii=False,indent=2)
print('Existing monitor correction arguments prepared.')
