from pathlib import Path
import ast
D=Path(__file__).resolve().parent
s=(D/'publish_fullroute_once.py').read_text(encoding='utf8')
s=s.replace('FULL_ROUTE_PUBLISH','PROXY_ROUTE_PUBLISH').replace('FULL_ROUTE_XYZ_CPU_PREPARED','FULL_ROUTE_PROXY_CPU_PREPARED').replace('FULL_ROUTE_PUBLISHED','PROXY_ROUTE_PUBLISHED').replace('E1-G1-FULLROUTE-PUBLISH-01','E1-G1-PROXY-ROUTE-PUBLISH-02').replace('d3-119-','d3-120-')
s=s.replace("assert collected['evaluator']['receipts']['ATTENTION'] is None","assert json.loads((R/'E1_FULL_ROUTE_REVIEW_WORKER_ADMITTED.json').read_bytes())['admission']['shared_GPU_lock_was_free']")
s=s.replace('worker_not_restarted=True','failed_worker_replaced_after_actual_exit_lockfree=True')
ast.parse(s);p=D/'publish_proxy_route_once.py';assert not p.exists();p.write_text(s,encoding='utf8')
s=(D/'collect_fullroute.py').read_text(encoding='utf8').replace('new119','new120').replace('E1_CURRICULUM_INTERFACE','E1_FULL_ROUTE_REVIEW').replace('eval_worker_e1_curriculum_interface_review.py','eval_worker_e1_full_route_review.py').replace('FULL_ROUTE_PUBLISHED','PROXY_ROUTE_PUBLISHED').replace('FULL_ROUTE_COLLECT','PROXY_ROUTE_COLLECT').replace('E1-G1-FULLROUTE-COLLECT-01','E1-G1-PROXY-ROUTE-COLLECT-02')
ast.parse(s);p=D/'collect_proxy_route.py';assert not p.exists();p.write_text(s,encoding='utf8')
