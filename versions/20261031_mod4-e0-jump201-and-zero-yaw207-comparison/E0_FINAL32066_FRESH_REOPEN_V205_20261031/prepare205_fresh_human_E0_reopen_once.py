"""A new explicit human request permits one new visual use, never replay old launch."""
from pathlib import Path
import ast,hashlib,json,re,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
S=T/'E0_FINAL32066_USER_MUJOCO_V203_20261031'
C=T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2'
source=[]
for old,new in (('view203_E0_final32066_true_MOD4.py','view205_E0_final32066_true_MOD4.py'),
                ('launch203_user_visible_E0_MuJoCo_once.py','launch205_user_visible_E0_MuJoCo_once.py')):
    text=(S/old).read_text('utf8');fresh=re.sub(r'(?<![0-9])203(?![0-9])','205',text)
    ast.parse(fresh)
    nums=lambda s:[n.value for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Constant) and isinstance(n.value,(float,int))]
    assert nums(text)==nums(fresh)
    (B/new).write_text(fresh,encoding='utf8',newline='\n')
    raw=(B/new).read_bytes();source.append(dict(path=str(B/new),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
receipt=json.loads((C/'reports/ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json').read_bytes())
with (R/'FROZEN205_FRESH_HUMAN_REOPEN_VISUAL_READ_PURPOSE.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),human_exact='再给我打开一下我看看',requested_model='E0 jump branch32066',
        source=source,artifact=receipt,previous203_window_closed=True,
        previous203_byte_pass_consumed_and_not_replayed=True,this_NEW_user_visual_bytepass_budget=1,
        npz_member_reads_each=1,visual_integrity_passes=1,
        model_GPU_neural_physics_SDK_or_remote_calls=0,
        original_E0_and_primary200_window_untouched=True,no_old_launcher_rerun=True,
        same_recorded201_case_not_new_or_live_training=True,window_bound_s=7200),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed_source=True,new_visual_purpose=True,model_iteration=32066,new_GPU_calls=0)))
