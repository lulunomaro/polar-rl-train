"""Preserve position separately from 1N completion, matching original reader."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;s=(D/'yawpi_actual_reader_components_v3.py').read_text()
old="   assert pos==contact,'Actual original1N support and signed wheel position disagree'\n";assert s.count(old)==1;s=s.replace(old,'')
assert s.count('position_contact_agree=True')==1;s=s.replace('position_contact_agree=True','position_contact_agree=pos==contact')
old='original_two_wheel_before_after200mm_and1N_margin=True,WORLD_forward_complete='
new="original_two_wheel_before_after200mm_and1N_margin=True,position_contact_agree_all_episodes=all(ep['position_contact_agree'] for x in per for ep in x['all_valid_episodes']),WORLD_forward_complete="
assert s.count(old)==1;s=s.replace(old,new);p=D/'yawpi_actual_reader_components_v4.py';assert not p.exists();p.write_text(s,encoding='utf8')
for name in ('review_yawpi_own_native_or_full_actual_CPU','review_yawpi_direct_same_WORLD_prefix_actual_CPU'):
 s=(D/(name+'_v3.py')).read_text().replace('import yawpi_actual_reader_components_v3 as m','import yawpi_actual_reader_components_v4 as m');p=D/(name+'_v4.py');assert not p.exists();p.write_text(s,encoding='utf8')
o=D/'reports/ACTUAL_READER_V4_ORIGINAL_SUPPORT_CLASSIFICATION_REPAIR_PREPARED.json';assert not o.exists();o.write_text(json.dumps(dict(epoch=time.time(),original_V3_actual_native_pass_and_source_retained=True,original_negative_test_EXIT1_retained=True,why='Synthetic lower1N test correctly exposed that helper asserted position==contact. Original route reader retains both outcomes and consistency flag; loss of support is valid behavioral failure, not data corruption. Independent V4 retains original contact completion criterion and separately records position disagreement. No physics/query/contact/COM threshold changed.',no_GPU_SSH_PPO=True,Git_pending_root=True),indent=2),encoding='utf8')
