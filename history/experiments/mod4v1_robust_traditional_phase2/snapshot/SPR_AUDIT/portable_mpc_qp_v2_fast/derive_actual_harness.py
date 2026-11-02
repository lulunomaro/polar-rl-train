"""Reuse the identical sealed actual-H fixture/header and comparison logic."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'C_MPC8_NUMERIC_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace_once(s,old,new):
 assert s.count(old)==1,old
 return s.replace(old,new,1)
def main():
 records={x['path']:x for x in json.loads((BASE/'INDEX.json').read_text(encoding='utf-8'))['files']}
 for n in ['actual_hessian_driver.c','compare_results.py']:assert sha(BASE/n)==records[n]['sha256']
 s=(BASE/'actual_hessian_driver.c').read_text(encoding='utf-8')
 s=replace_once(s,'#include "../portable_mpc_qp_v1/boxqp.h"','#include "boxqp_fast.h"')
 s=replace_once(s,'#include "actual_fixtures.h"','#include "../C_MPC8_NUMERIC_V1/actual_fixtures.h"')
 s=replace_once(s,'bqp_workspace w;bqp_options o;bqp_problem p;bqp_result r;progress_state progress;',
               'bqp_workspace w;bqp_options o;bqp_problem p;bqp_result r;bqp_fast_info info;progress_state progress;')
 s=replace_once(s,'(void)bqp_solve(&p,&o,&w,&r);runs++;','(void)bqp_solve_fast(&p,&o,&w,&r,1u,&info);runs++;')
 old=r'fprintf(out,"]}\n");'
 new=r'fprintf(out,"],\"free_tried\":%u,\"free_solve_finite\":%u,\"free_feasible\":%u,\"free_metrics_valid\":%u,\"free_kkt_met\":%u,\"free_selected\":%u,\"free_kkt_f32\":%.9g}\n",(unsigned)info.free_tried,(unsigned)info.free_solve_finite,(unsigned)info.free_feasible,(unsigned)info.free_metrics_valid,(unsigned)info.free_kkt_met,(unsigned)info.free_selected,(double)info.free_projected_kkt_inf);'
 s=replace_once(s,old,new);s=replace_once(s,'ACTUAL_H_DRIVER runs=','FAST_ACTUAL_H_DRIVER runs=')
 target=HERE/'fast_actual_driver.c';assert not target.exists();target.write_text(s,encoding='utf-8')
 c=(BASE/'compare_results.py').read_text(encoding='utf-8')
 c=replace_once(c,"(HERE/'actual_model_vectors.json')","(HERE.parent/'C_MPC8_NUMERIC_V1/actual_model_vectors.json')")
 c=replace_once(c,"(HERE/'comparison_error_02.txt')","(HERE/'fast_comparison_error_01.txt')")
 target2=HERE/'compare_results.py';assert not target2.exists();target2.write_text(c,encoding='utf-8')
 provenance={'shared_actual_fixture_header':{'path':str(BASE/'actual_fixtures.h'),'sha256':sha(BASE/'actual_fixtures.h')},
             'shared_vector_oracles':{'path':str(BASE/'actual_model_vectors.json'),'sha256':sha(BASE/'actual_model_vectors.json')},
             'driver_source':{'path':str(BASE/'actual_hessian_driver.c'),'sha256':sha(BASE/'actual_hessian_driver.c')},
             'comparison_source':{'path':str(BASE/'compare_results.py'),'sha256':sha(BASE/'compare_results.py')},
             'method':'new-file changes only to fast call/header/diagnostics; no fixture/model/oracle or C1 edit'}
 (HERE/'ACTUAL_HARNESS_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8');print(json.dumps(provenance))
if __name__=='__main__':main()
