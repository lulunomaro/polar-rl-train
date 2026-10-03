from pathlib import Path
import shutil

d=Path(__file__).parent
orig=d/'mild_dr.py'
backup=d/'mild_dr_original.py'
if not backup.exists(): shutil.copy2(orig,backup)
s=backup.read_text(encoding='utf-8')
s=s.replace('import warp as wp','import warp as wp\nfrom autonomy_policy import DR_PROFILES')
s=s.replace('self.robot = robot = env.scene[\'robot\']',"self.profile = os.environ.get('RM_MILD_DR_PROFILE', '')\n        self.recipe = DR_PROFILES[self.profile]\n        self.robot = robot = env.scene['robot']")
s=s.replace('torch.linspace(.8, 1., 32)',"torch.linspace(*self.recipe['friction'], 32)")
s=s.replace('uniform_(.95, 1.05, generator=self.generator)',"uniform_(*self.recipe['mass'], generator=self.generator)",1)
s=s.replace('uniform_(.95, 1.05, generator=self.generator)',"uniform_(*self.recipe['motor'], generator=self.generator)")
s=s.replace(".94999 <= s['min'] <= s['max'] <= 1.05001", "self.recipe['motor'][0]-1e-5 <= s['min'] <= s['max'] <= self.recipe['motor'][1]+1e-5")
s=s.replace("return {'profile': 'white_v1',", "return {'profile': self.profile, 'registered_ranges': self.recipe,")
s=s.replace("if os.environ.get('RM_MILD_DR_PROFILE', '') != 'white_v1':\n        return", "profile = os.environ.get('RM_MILD_DR_PROFILE', '')\n    if profile in ('', 'nominal'):\n        return\n    if profile not in DR_PROFILES:\n        raise ValueError('Unregistered whitelist DR profile: '+profile)")
orig.write_text(s,encoding='utf-8')
for name in ['spin_rate_probe.py','validate_speed.py']:
    p=d/name; before=d/(name+'.before')
    if not before.exists():shutil.copy2(p,before)
    text=before.read_text(encoding='utf-8').replace("choices=['nominal','white_v1']","choices=['nominal','white_v1','white_v2','white_v3']")
    p.write_text(text,encoding='utf-8')
# Latest-cap BODY arc regression, no change to training commands or rewards.
s=(d.parent/'MOD4_FPS_TURN_STAGE_20261003/turn_probe.py').read_text(encoding='utf-8')
s=s.replace("choices=['nominal','white_v1']","choices=['nominal','white_v1','white_v2','white_v3']")
s=s.replace("p.add_argument('--seed',", "p.add_argument('--max-rate',type=float,required=True);p.add_argument('--seed',")
s=s.replace('wz=4.,','wz=args.max_rate,').replace('wz=-4.,','wz=-args.max_rate,')
(d/'autonomy_turn_probe.py').write_text(s,encoding='utf-8')
for name in ['mod4_task.py','turn_mod4_task.py']:
    p=d/name
    if not p.exists():continue
    backup=d/(name+'.before')
    if not backup.exists():shutil.copy2(p,backup)
    s=backup.read_text(encoding='utf-8')
    old='os.environ.get("RM_MILD_DR_PROFILE", "") == "white_v1"'
    new='os.environ.get("RM_MILD_DR_PROFILE", "") in ("white_v1", "white_v2", "white_v3")'
    assert s.count(old)==1,'Unexpected actuator recipe'
    p.write_text(s.replace(old,new),encoding='utf-8')
