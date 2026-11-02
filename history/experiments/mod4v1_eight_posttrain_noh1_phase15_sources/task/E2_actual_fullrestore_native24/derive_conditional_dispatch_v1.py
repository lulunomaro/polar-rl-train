"""E2 conditional new-purpose staging: requires its actual fresh80 PASS/exit first."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
s=(ROOT/'E0_actual_fullrestore_native24/prepare_dispatch_a92_no_update_once.py').read_text(encoding='utf-8').replace('E0','E2').replace('e0','e2').replace('A92','B3').replace('a92','b3')
s=s.replace('b3c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1')
s=s.replace("SOURCE=BASE+'/tasks/MOD4V1_E2_FRESH80_ATTEMPT2_20261102_015129_1793555489733223300'","SOURCE=BASE+'/tasks/MOD4V1_E2_FRESH80_FULLDR_20261102_023610_1793558170021229000'")
s=s.replace('MOD4_E2_PPO50_GAS400_2610v89d','MOD4_E2_PPO50_GAS400_2610v93').replace('final_valid_update82.pt','final_valid_update92.pt').replace('14031973','14615089')
a="B=pathlib.Path(%r);S=pathlib.Path(%r);assert not B.exists() and (S/'runtime').is_dir()"
b=a+"\nfresh=json.loads((S/'FINAL.json').read_bytes());closed=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes())\nassert fresh['passed'] is True and closed['all_own_children_waited'] is True and closed['original_private_lock_released'] is True and closed['original_shared_lock_released'] is True,'Fresh80 actualPASS and clean original locks exit REQUIRED before any source permission'"
assert a in s;s=s.replace(a,b)
a="B.mkdir();shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)"
b=a+"\nif (S/'lib').is_dir():shutil.copytree(S/'lib',B/'lib',ignore=ignore)"
assert a in s;s=s.replace(a,b)
ast.parse(s)
out=HERE/'prepare_dispatch_b3_no_update_once.py'
with out.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'new_dispatcher':str(out),'gate':'Remote fresh80 actualPASS and both locks released','PT_read_by_derivation':0},indent=2))
