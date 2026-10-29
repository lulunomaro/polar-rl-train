"""Root-helper parent-path correction; selected remote entry remains UNUSED."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent;P=B/'run_NEW_E2_V4_original_flat_height_reviewed_secure_ingress_UNUSED_once.py'
s=P.read_text(encoding='utf8');a="B=Path(__file__).resolve().parent;L=B.parent;R=B/'reports'"
assert s.count(a)==1
s=s.replace(a,"B=Path(__file__).resolve().parent;L=B.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=B/'reports'")
ast.parse(s);exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
