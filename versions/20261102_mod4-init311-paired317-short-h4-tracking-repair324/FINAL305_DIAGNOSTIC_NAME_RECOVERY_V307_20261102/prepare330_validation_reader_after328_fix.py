"""Retain327 static rejection and make the corrected328-aware read-only validator."""
from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent;P=T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102'
s=(N/'validate327_frozen324_static_and_save_work_order.py').read_text('utf8')
s=s.replace("runner=D/'postround325/run325_eval_once_template.py'", "runner=T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102/run328_eval_once_template.py'")
s=s.replace("str(P/'source/evaluate325.py')","str(P/'source/evaluate328.py')").replace('from contract325 import','from contract328 import').replace('RESULT325.json','RESULT328.json')
s=s.replace("    def visit_Constant(self,node):", "    def visit_Attribute(self,node):\n        node.attr=node.attr.replace('324','X').replace('320','X').replace('305','X').replace('315','X');return self.generic_visit(node)\n    def visit_Constant(self,node):")
s=s.replace('STATIC327_FULL324_PACKAGE_VALIDATION','STATIC330_FULL324_PACKAGE_VALIDATION').replace('CURRENT_ACTUAL327_311_317_H4_REPAIR324_WORK_ORDER','CURRENT_ACTUAL330_311_317_H4_REPAIR324_WORK_ORDER').replace('LOCAL327_READER_AND_PRODUCER_ERRORS_RETAINED','LOCAL330_READER_AND_PRODUCER_ERRORS_RETAINED')
s=s.replace('remoteeval325parent_AST_matches','remoteeval328parent_AST_matches')
s=s.replace("script=str(D/'postround325_finalize324_replay_eval_once.py'),index=str(D/'INDEX325_POSTROUND_FOR324_FROZEN.json')", "script=str(T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102/postround328_finalize324_replay_eval_once.py'),index=str(T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102/INDEX328_POSTROUND_FOR324_FROZEN.json')")
s=s.replace("bind_after_first=str(D/'bind326_after324_first_and_launch_postround_once.py')", "bind_after_first=str(T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102/bind329_after324_first_and_launch_postround_once.py')")
s=s.replace('bind326writes','bind329writes').replace('eval325seed','eval328seed').replace('validateFIRST via bind326;solepostround325','validateFIRST via bind329;solepostround328')
s=s.replace("unused321='Frozen", "old325postround='Unusedliteralparentretained308causedstatic327rejection; correctedindependent328actualparentASTpasses,neverexecuteold325.',\n    unused321='Frozen")
s=s.replace("model_reads=0,controls=64,comparison=probe['comparison']", "model_reads=0,controls=64,raw_kind_names='defaultzero_initisahistoricalmisnomer;actualoriginalresetgroupjointqisnonzero,referencegroupfullstatewrite;originalrawretained',comparison=probe['comparison']")
ast.parse(s)
path=N/'validate330_corrected_package_and_save_work_order.py';path.write_bytes(s.encode())
print(str(path))
