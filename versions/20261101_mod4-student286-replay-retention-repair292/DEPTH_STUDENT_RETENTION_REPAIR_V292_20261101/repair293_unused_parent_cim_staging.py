"""Preserve unused staging version; permit its own sequential local waiter."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;P=N/'postround292';R=N/'reports'
p=P/'run293_eval_once_template.py';old=p.read_bytes()
with (P/'run293_eval_once_template_v1_UNEXECUTED.py').open('xb')as f:f.write(old)
text=old.decode().replace("patterns='postround292|collect292_|", "patterns='collect292_|")
assert text!=old.decode();ast.parse(text);p.write_bytes(text.encode())
with (R/'POSTROUND293_UNUSED_STAGING_PARENT_CIM_REPAIR.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original_template_preserved=True,reason='Known local waiting parent is alive but not an SSH/controller lease while sequential subprocess evaluates; matching it made single-client CIM reject legitimate child.',repair='Remove local waiter regex from unused future evaluation; retain active collect/launch/eval clients. Actual292 frozen production untouched.',old_SHA=hashlib.sha256(old).hexdigest(),new_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),old_template_executed=False),f,indent=2)
work=json.loads((R/'CURRENT_ACTUAL292_REPLAY_EVAL_CONTINUE_WORK_ORDER.json').read_bytes())
work.update(epoch=time.time(),postround_worker_pending=False,postround_worker=dict(pid=48920,script=str(N/'postround292_finish_replay_eval_once.py'),launch_receipt=str(R/'POSTROUND292_WAITER_LAUNCH.json'),scope='local waiting; collects at original900 then newCPU/eval293/replay/decision, no automatic GO',check='Never duplicate normal/CPU/eval while this exact process alive. New SSH only after exact fresh CIM shows no active remote controller.'))
with (R/'CURRENT_ACTUAL292_REPLAY_EVAL_CONTINUE_WORK_ORDER_V2.json').open('x',encoding='utf8')as f:json.dump(work,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=True,postround_pid=48920)))
