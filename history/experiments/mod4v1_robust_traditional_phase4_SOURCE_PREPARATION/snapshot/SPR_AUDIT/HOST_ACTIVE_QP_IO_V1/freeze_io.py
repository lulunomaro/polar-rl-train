"""Source hashes/schema/integer-clock vectors only; no physics/solver import."""
from pathlib import Path
import hashlib,json,random
HERE=Path(__file__).resolve().parent;SEALED=HERE.parent/'ACTIVE_BOX_QP_V3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):
 p=HERE/name
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def row(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 old=json.loads((SEALED/'SOURCE_FREEZE.json').read_text());index=json.loads((SEALED/'INDEX.json').read_text());records={r['path']:r for r in old['old_files']+old['real_MPC_references']}
 for r in index['files']:
  p=SEALED/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];records[str(p.resolve())]=row(p)
 for name in ['INDEX.json','VALIDATION.json','MANIFEST.json','index_validation_01.log']:
  p=SEALED/name;records[str(p.resolve())]=row(p)
 for r in records.values():
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],p
 core=row(SEALED/'active_box_qp.c');header=row(SEALED/'active_box_qp.h')
 assert core['sha256']=='b726c0acf09a13fe0114da1e1161fb2a7f57a4e138c7caf239c5fdd157ec653e'
 assert header['sha256']=='e8b52347608370314dff3e48d5b4de1f4821b7b0e5f978a2ffae66958a0f8cba'
 dump('SOURCE_FREEZE.json',{'scope':'new IO bridge only; parent H4 neither read nor modified','core':core,'header':header,'old_files':list(records.values()),'reference_cases':row(SEALED/'PROBLEMS.json'),'reference_direct_C':row(SEALED/'C_RUNS_02.jsonl'),'compiler':r'C:\MinGW\bin\gcc.exe','Python':r'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe'})
 fields=[]
 for name,kind in [('status','u32'),('valid','u32'),('fatal','u32'),('request_n','u32'),('result_n','u32'),('warm_present','u32'),('clock_failed','u32'),('diagnostic_valid','u32'),('cost','f32'),('kkt_estimate','f32'),('kkt_upper','f32'),('maximum_gradient_roundoff_bound','f32'),('diagnostic_kkt_estimate','f32'),('diagnostic_kkt_upper','f32'),('pivots','u32'),('factorizations','u64'),('factor_cells','u64'),('releases','u64'),('bound_hits','u64'),('gradient_evaluations','u64'),('clock_polls','u64'),('last_phase','u32'),('abort_phase','u32'),('start_us','u64'),('last_us','u64'),('elapsed_us','u64')]:fields.append({'name':name,'type':kind})
 fields.extend({'name':'z'+str(i),'type':'f32'} for i in range(16));assert len(fields)==42
 dump('PROTOCOL_SCHEMA.json',{'magic':'ABQPIO','version':1,'max_n':16,'max_frame_bytes':32768,'max_tokens':400,'boot_fields':['max_n','pointer_bits','uint64_bits','float_mantissa','clock_source','float_environment','core_sha256','header_sha256'],'solve_prefix':['n','max_pivots','tolerance','budget_us','warm_present','H_count','vector_count'],'solve_data_order':['H_rowmajor_nxn','f_n','lo_n','hi_n','warm_n_only_if_present'],'solve_count':'7+n*n+3*n+(warm_present?n:0)','header':['magic','version','operation','sequence_u64','payload_token_count_u32'],'request_operations':{'S':'SOLVE','Q':'QUIT, zero payload'},'response_operations':{'B':'BOOT, seq0','R':'SOLVE reply, 42 fields','E':'fatal protocol reply, 42 fields','A':'QUIT ack, zero payload'},'reply_fields':fields,'status_names':['CONVERGED','MAX_PIVOTS','DEADLINE','CLOCK_ERROR','BAD_ARGUMENT','BAD_SHAPE','BAD_OPTIONS','BAD_ALIAS','NONFINITE','ASYMMETRIC','NOT_SPD','NUMERIC','NO_PROGRESS','CYCLE','ROUNDOFF_LIMIT','BAD_BOX'],'protocol_status':{'1001':'BAD_HEADER','1002':'BAD_COUNT','1003':'BAD_INTEGER','1004':'BAD_SHAPE','1005':'BAD_SEQUENCE','1006':'BAD_FLOAT','1007':'BAD_OPTION','1008':'TRUNCATED','1009':'OVERSIZE','1010':'BAD_ASCII','1011':'HOST_CLOCK_FAILURE','1012':'HOST_FP_ENV','1013':'BAD_OPERATION'},'fatal_solver_statuses':[3,4,5,6,7,8,9,10,11,15],'core_sha256':core['sha256'],'header_sha256':header['sha256'],'acceptance':'status0 AND valid1 only; all non0 accepted z/cost/KKT0, stats retained; diagnostics separately labeled','sequence':'first positive uint64 arbitrary; subsequent exactly previous+1, no wrap; Q obeys same rule; SDK EOF-closes at exhaustion','clock':'QPC absolute monotonic us; exact checked integer conversion; relative ASQP START budget, cooperative only','SDK_wall':'solve-entry through full response validation/lifecycle, perf_counter_ns; NOT complete parent cycle deadline qualification'})
 text='#ifndef AQ_IO_BUILD_H\n#define AQ_IO_BUILD_H\n#define AQ_CORE_SHA "'+core['sha256']+'"\n#define AQ_HEADER_SHA "'+header['sha256']+'"\n#define AQ_REPLY_FIELDS 42u\n#define AQ_MAX_FRAME 32768u\n#define AQ_MAX_TOKENS 400u\n#endif\n';(HERE/'aq_io_build.h').write_text(text,encoding='utf-8')
 maximum=(1<<64)-1;rng=random.Random(2026110219);pairs=[(0,1),(1,1),(maximum,1),(maximum,maximum),(maximum,1000000),(maximum,1000001),(maximum//1000000,1),(maximum//1000000+1,1),(maximum,0),(maximum,maximum-1),(maximum-1,maximum),(1<<63,1<<63),(1<<63,(1<<63)-1),(123456789012345,10000000)]
 for i in range(240):pairs.append((rng.getrandbits(64),rng.getrandbits(64) if i%3 else rng.randrange(1,100000001)))
 vectors=[]
 for ticks,freq in pairs:
  value=ticks*1000000//freq if freq else maximum+1;vectors.append({'ticks':ticks,'frequency':freq,'ok':int(value<=maximum),'expected_us':value if value<=maximum else 0})
 dump('CLOCK_VECTORS.json',vectors)
 h=['#ifndef AQ_CLOCK_VECTORS_H','#define AQ_CLOCK_VECTORS_H','#include <stdint.h>','typedef struct {uint64_t ticks,frequency,expected;unsigned ok;} aq_clock_vector;','static const aq_clock_vector aq_clock_vectors[]={']
 h.extend('{UINT64_C(%d),UINT64_C(%d),UINT64_C(%d),%du},'%(r['ticks'],r['frequency'],r['expected_us'],r['ok']) for r in vectors);h+=['};','#endif'];(HERE/'clock_vectors.h').write_text('\n'.join(h)+'\n',encoding='utf-8')
 print(json.dumps({'old_files_frozen':len(records),'clock_vectors':len(vectors),'core_sha256':core['sha256'],'schema_reply_fields':len(fields)}))
if __name__=='__main__':main()
