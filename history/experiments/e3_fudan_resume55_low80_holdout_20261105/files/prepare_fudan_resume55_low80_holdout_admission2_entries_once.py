"""New unused admission after actual Root8 holdout zero-start; reuse original bounded release controller."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'prepare_fudan_low80_admission2_release_entries_once.py').read_text(encoding='utf8')
changes={
 'FDNLOW80_CONFIRM_ADMISSION2_':'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_',
 'FDNLOW80_CONFIRM_THREE_SEED_N80_20261105_074818_1793836098533851800':'FDNRESUME55_LOW80_HOLDOUT_THREE_SEED_N80_20261105_105212_1793847132730709700',
 'FDNLOW80_CONFIRM_':'FDNRESUME55_LOW80_HOLDOUT_',
 'stage_fudan_low80_confirm_admission2_once.py':'stage_fudan_resume55_low80_holdout_admission2_once.py',
 'dispatch_fudan_low80_confirm_admission2_once.py':'dispatch_fudan_resume55_low80_holdout_admission2_once.py',
 'collect_fudan_low80_confirm_admission2_once.py':'collect_fudan_resume55_low80_holdout_admission2_once.py',
 'stage_fudan_low80_confirm_once.py':'stage_fudan_resume55_low80_holdout_once.py',
 'dispatch_fudan_low80_confirm_once.py':'dispatch_fudan_resume55_low80_holdout_once.py',
 'collect_fudan_low80_confirm_once.py':'collect_fudan_resume55_low80_holdout_once.py',
 'run_fudan_low80_after_zero_start_release_once.py':'run_fudan_resume55_low80_holdout_after_zero_start_release_once.py',
 'fdn_low80_confirm_admission2_outer_wait.py':'fdn_resume55_low80_holdout_admission2_outer_wait.py',
 'fdn_low80_confirm_outer_wait.py':'fdn_resume55_low80_holdout_outer_wait.py',
 'LOW80_CONFIRM_ADMISSION2_PROGRESS':'RESUME55_LOW80_HOLDOUT_ADMISSION2_PROGRESS',
 'LOW80_CONFIRM_ADMISSION2_CLOSED':'RESUME55_LOW80_HOLDOUT_ADMISSION2_CLOSED',
 'LOW80_CONFIRM_PROGRESS':'LOW80_CONFIRM_PROGRESS',
 'LOW80_CONFIRM_CLOSED':'LOW80_CONFIRM_CLOSED',
 'source_fudan_frozen_low80_confirm_v1':'source_fudan_frozen_low80_holdout_v2_resume55',
 'reports/FDN_N20000_W12_LRSCHEDULE001_20261105_065807/CLOSED_RESULT.json':'reports/FDN_N20000_W14_RESUME55_ADMISSION2_20261105_101210/CLOSED_RESULT.json',
 '6a2b446951dffc7aad45f7b42d2ef7d98ada33b82a822aaee82019ff79631662':'663bb6c0b8f0e52d97f169db0240de03a2b8507b9d246d9c31cecc0e0b3cfe27',
 '1641988':'1650042','157753080':'158855248','1641981':'1650035','157753059':'158855229',
 'c9cc481aa7d06d9d8d01db0b51ffb6386c8b6142ee18d50bf4a21bcb3668c9e1':'5f3e6d621f28ca9de7b95dbcf2ef0fafddc5287537680631a1e63fdd682e963c',
 'b9e47b31f6684f1485bbce83f268c08b70f3d798d171c809dd744d5ae74a17d4':'2544ae2552e3a88d118005794ea81035b9a99a737f7d74e8f4fe2c8067c89a40',
 'ONEGPU_E3_LOW80_THREE_SEED_CONFIRM_NO_LEARNING':'ONEGPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55_NO_LEARNING',
 '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt':'/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W14_ADMISSION2_20261105_094946_1793843386314498300/roles/E3/production/fudan_seq20k_full_u000050_wu000025_c00001200_s0002.pt',
 'MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000':'MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W14_ADMISSION2_20261105_094946_1793843386314498300',
 '146247985':'146251569','55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7':'8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32',
 '20260929':'20261002','20260930':'20261003','20261001':'20261004'
}
restore={}
for i,(old,new)in enumerate(sorted(changes.items(),key=lambda x:len(x[0]),reverse=True)):
 if old==new:continue
 assert old in s,old;token='[REDACTED]'+str(i)+'__';s=s.replace(old,token);restore[token]=new
for token,new in restore.items():s=s.replace(token,new)
exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
