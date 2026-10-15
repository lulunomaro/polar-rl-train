"""Preserve bounded network failures and exact pending scope without new Git objects."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
R = D / 'reports'
REPO = D.parent / 'polar-rl-train'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldprompt = D / 'MONITOR_S5_WHITEV2_COMPLETE30_NOMINAL_LOW_STEP_PREPARATION_ACTUAL_20261015.txt'
assert H(oldprompt) == '2f07f7a2a8fefdbe84aabb279039cd6d10e769d6932db95f3c958e3ec8774eb4'
prompt = D / 'MONITOR_S5_WHITEV2_COMPLETE30_EXISTING_GIT_PUSH_PENDING_ACTUAL_20261015.txt'
prefix = '''最新Git actual优先：完整30完成审查已经只生成一次ordinary commit e411cb07f275b287f3644a69c4159737a3b0edc3（base d3b0066），不是新trial/tag。原push发生RPC curl55 connection reset/sideband unexpected disconnect，随后独立read-only lsremote Schannel握手失败；再独立本地tracked SHA审查后的有界existingobject recovery也在remote读取前Schannel失败，没再push/record/tag/commit。Remote main是否已接收目前UNKNOWN，不能凭Everything up-to-date字样称已同步，也不能凭Git错误冒GPU故障。全部错误保存在M/reports/WHITEV2_COMPLETE30_ORDINARY_APPEND_ORIGINAL_ERROR_*、WHITEV2_COMPLETE30_POST_PUSH_REMOTE_READ_TLS_FAILURE_ACTUAL与WHITEV2_COMPLETE30_EXISTING_ORDINARY_RECOVERY_ORIGINAL_ERROR_*。
下一原1hheartbeat或独立实质工作后只续现有e411objects及remote main/tag/peeled/all1346oldtags/tracked核，不能重run首次append helper/record/tag/commit；已有resume reader若再用以当前actualHEAD严格审，先rawremote只读，不密集网络重试/关证书校验/改全局Git配置。只有原现有commit实际remote验证后，才另ordinarysupplement补所有postcapture失败/恢复源/监控/receipt；目前明确pending list为reports/WHITEV2_COMPLETE30_POST_CAPTURE_PENDING_GIT_LIST_ACTUAL.json。网络重试不阻CPU nominal/低台阶准入准备，不停/重GPU，不改预算。物理30完成/父子自然退出及独立审查仍真实，以下旧Git段以本最新及lateractual优先。

'''
with prompt.open('x', encoding='utf8', newline='\n') as f:
    f.write(prefix + oldprompt.read_text(encoding='utf8'))
index = REPO / 'history/evidence' / D.name / 'ordinary_complete30_two_profile_audit_and_next_admission_v1/REPORT_CAPTURE_INDEX.json'
archived = {(x['source_path'], x['sha256']) for x in json.loads(index.read_bytes())['entries']}
pending = []
paths = set([*D.glob('*.py'), *D.glob('*.txt'), *D.glob('*.json'), *(p for p in R.rglob('*') if p.is_file())])
for p in sorted(paths):
    b = p.read_bytes()
    h = hashlib.sha256(b).hexdigest()
    if (str(p.resolve()), h) not in archived:
        pending.append(dict(path=str(p.resolve()), bytes=len(b), sha256=h, pending_ordinary_supplement_after_existing_objects_remote_verified=True))
out = R / 'WHITEV2_COMPLETE30_POST_CAPTURE_PENDING_GIT_LIST_ACTUAL.json'
v = dict(epoch=time.time(), existing_commit='e411cb07f275b287f3644a69c4159737a3b0edc3',
    existing_capture_commit_local=True, remote_main_unknown_due_to_bounded_TLS_RPC_failures=True,
    no_new_record_tag_commit_push_retry_after_last_TLS_failure=True, entries=pending,
    this_list_and_future_native_monitor_UTF8_verification_report_also_pending=True,
    pending_future_verification_report=str(R / 'WHITEV2_COMPLETE30_GIT_PENDING_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json'),
    physical_complete30_and18pairs_independently_passed=True,
    no_GPU_SSH210_249_PPO_or_budget_action=True)
with out.open('x', encoding='utf8') as f:
    json.dump(v, f, indent=2)
print(json.dumps(dict(prompt=str(prompt), prompt_SHA=H(prompt), pending_list=str(out), entries=len(pending))))
