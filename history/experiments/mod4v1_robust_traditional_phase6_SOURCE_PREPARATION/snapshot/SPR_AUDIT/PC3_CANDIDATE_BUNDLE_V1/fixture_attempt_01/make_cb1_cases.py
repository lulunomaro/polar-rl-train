"""Materialize unchanged saved raw inputs/goldens for NEW one-shot native QA.
No old code import, SDK, executable, physics or transport. Full f32 bit target is
saved ROUNDTRIP's typed decimal JSON; old C_REPLAY's integer -0 printing is only
numeric cohort corroboration (not the signed-zero acceptance oracle).
"""
from pathlib import Path
import csv,hashlib,json,struct,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];V3=ROOT/'SPR_AUDIT/portable_control_v3_current';IO=ROOT/'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def hx(x):return f32(x).hex()+'f'
def main():
 receipt=HERE/'FIXTURE_RECEIPT.json';assert not receipt.exists()
 rev=HERE/'fixture_attempt_01';rev.mkdir(exist_ok=False);shutil.copy2(Path(__file__),rev/Path(__file__).name)
 freeze=json.loads((HERE/'SOURCE_REFERENCES.json').read_bytes());refs={r['path']:r['sha256']for r in freeze['references']}
 files=[V3/'REFERENCE_VECTORS.csv',V3/'REFERENCE_LAYOUT.json',V3/'C_REPLAY_01.jsonl',IO/'ROUNDTRIP_01.jsonl']
 for p in files:assert sha(p)==refs[p.relative_to(ROOT).as_posix()]
 layout=json.loads(files[1].read_bytes());offsets=layout['offsets'];old=[json.loads(s)for s in files[2].read_text().splitlines()];saved=[json.loads(s)for s in files[3].read_text().splitlines()]
 with files[0].open(newline='')as f:rows=list(csv.reader(f))[1:]
 assert len(rows)==len(old)==len(saved)==3200
 def group(row,name):start,n=offsets[name];return [float(x)for x in row[start:start+n]]
 out=['/* New QA data only: synthetic metadata declarations, no operator permission. */','#ifndef CB1_CASES_H','#define CB1_CASES_H','#include <stdint.h>','typedef struct {uint32_t scenario,arm,accref,sequence,mode,count;uint64_t stamp,now,begin;float config5[5],raw18[18],gold48[48];} cb1_case;','static const cb1_case cb1_cases[]={']
 distinct=0;counts={};cohort=0
 for i,(row,prev,rec)in enumerate(zip(rows,old,saved)):
  one=lambda n:group(row,n)[0]
  case=int(one('SCENARIO'));r=rec['reply'];assert rec['fixture_row']==i and rec['case']==case and prev['row']==i and prev['scenario']==case
  assert r['VALID']==1 and r['status']==0
  for a,b in zip(r['STATE14']+r['MATH_TAU'],prev['state14']+prev['tau']):assert f32(a)==f32(b);cohort+=1
  raw=sum((group(row,n)for n in ('GYRO','ACCEL','Q4','DQ4','SPIN2','FORWARD','YAW_COMMAND')),[]);assert len(raw)==18
  gold=r['STATE14']+r['REF14']+r['MATH_TAU']+r['GUARDED_TAU']+[r[n]for n in ('SHAPER_V','SHAPER_W','SHAPER_A','YAW_I')]+[r['REF14'][7],r['REF14'][8],r['SHAPER_A'],r['ROLL']];assert len(gold)==48
  distinct+=int(f32(r['SHAPER_V'])!=f32(r['REF14'][7])or f32(r['SHAPER_W'])!=f32(r['REF14'][8]));counts[case]=counts.get(case,0)+1
  ints=[case,int(one('ARM')),int(one('ACCREF')),int(one('SEQUENCE')),int(one('MEAN_MODE')),int(one('MEAN_COUNT'))]
  stamps=[int(one(n))for n in ('STAMP','NOW','WINDOW_BEGIN')]
  config=group(row,'OFFSET')+[one('ACC_CORR'),one('RADIUS')]
  out.append('{'+','.join(str(x)+'u'for x in ints)+','+','.join('UINT64_C('+str(x)+')'for x in stamps)+',{' +','.join(hx(x)for x in config)+'},{'+','.join(hx(x)for x in raw)+'},{'+','.join(hx(x)for x in gold)+'}},')
 out+=['};','#define CB1_CASE_COUNT 3200u','#endif'];assert distinct>0
 with (HERE/'cb1_cases.h').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(out)+'\n')
 v=dict(rows=3200,scenarios=counts,internal_effective_distinct_rows=distinct,old_nonzero_or_signless_zero_numeric_cohort_checks=cohort,strict_signed_zero_oracle='saved typed ROUNDTRIP_01.jsonl f32 bits',actual_expected_float_values=3200*48,case_header_sha256=sha(HERE/'cb1_cases.h'),source_hashes={p.relative_to(ROOT).as_posix():sha(p)for p in files},old_SDK_or_executable_runs=0,physics=0)
 with receipt.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v,indent=2))
if __name__=='__main__':main()
