from pathlib import Path
import ast,hashlib,json,re,time
T=Path(__file__).resolve().parent.parent
OLD=T/"H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029"
S=T/"H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029"
assert not S.exists();(S/"code").mkdir(parents=True);(S/"reports").mkdir()
replacements=[
("fudan108","fudan112"),("native108","native112"),("FROZEN108","FROZEN112"),("NEW108","NEW112"),
("MOD4_H1_NATIVE107_FUDAN270_FROZEN_MOTION_WM_DIAG_","MOD4_H1_NATIVE111_FUDAN270_FROZEN_MOTION_WM_DIAG_"),
("20261029v108","20261029v112"),
("TWO107_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1","TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3"),
("NATIVE106_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json","NATIVE111_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json"),
("TWO107_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json","TWO111_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json"),
("MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029","MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029"),
("MOD4_H1_FUDAN270_EPISODE20_2610v107CPUv2","MOD4_H1_FUDAN270_REWARD_COHERENCE_2610v111"),
("36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef","24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12"),
("256234249","256235849"),
("qualified107","qualified111"),("FROZEN_NATIVE107","FROZEN_NATIVE111"),
("requires original104 closed","requires original111 closed"),
("after actual107 closed","after actual111 closed"),
("admitted107 coherent20s runtime for qualified111 output","admitted111 coherent-reward runtime for qualified111 output")]
files=[*sorted((OLD/"code").glob("*.py")),OLD/"run_NEW108_qualified107_fixed20s_Fudan270_motion_paired_WM_UNUSED_once.py",OLD/"verify_SOURCE108_actual_phase_and_contiguous_window_CPU_synthetic_UNUSED_once.py"]
deriv=[]
for p in files:
 s=p.read_text(encoding="utf8")
 for a,b in replacements:s=s.replace(a,b)
 for a,b in [(172720,185970),(17272,18597),(16632,17893)]:s=re.sub(r"\b"+str(a)+r"\b",str(b),s)
 name=p.name.replace("108","112").replace("qualified107","qualified111")
 if name=="fudan112_frozen_diag_driver_v1.py":
  old="labels=phases[start:start+horizon];air=[x['airborne_both_above5mm_and_unloaded'] for x in labels]"
  new=old+"\n    input_phase=phases[start-1] if start>0 else None\n    input_known=input_phase is not None\n    input_air=input_phase['airborne_both_above5mm_and_unloaded'] if input_known else None\n    input_supported=input_phase['both_supported'] if input_known else None"
  assert s.count(old)==1;s=s.replace(old,new)
  a="starts_grounded_not_air=not air[0],contains_actual_airborne=any(air),grounded_start_then_air=not air[0] and any(air[1:])"
  b="input_phase_known=input_known,input_phase=input_phase,starts_grounded_not_air=bool(input_known and input_supported and not input_air),contains_actual_airborne=any(air),grounded_start_then_air=bool(input_known and input_supported and not input_air and any(air))"
  assert s.count(a)==1;s=s.replace(a,b)
 ast.parse(s)
 dest=S/("code" if p.parent.name=="code" else "")/name
 with dest.open("x",encoding="utf8",newline="\n") as f:f.write(s)
 deriv.append(dict(original_source=str(p),original_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),selected_source=str(dest),selected_SHA=hashlib.sha256(dest.read_bytes()).hexdigest()))
value=dict(source_only=True,new_purpose="qualified111 coherent-reward own-plant fixed20s motion/worldheading/velocity/contact/reward/maskedgoal/actual8and32stepWM; no learner",input_formal_SHA="24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12",source_iteration=18597,world_updates=185970,policy_updates=17893,files=deriv,old108_model_raw_or_runtime_not_replayed=True,paired_phase_label_fix="Use previous actual terminal as window input; first control input unknown, grounded needs actual support; no inferred ground from absence of air.",actual112_case_not_run=True)
with (S/"SOURCE112_NEW_PURPOSE_EXACT_DERIVATION.json").open("x",encoding="utf8") as f:json.dump(value,f,indent=2)
print(json.dumps(dict(prepared=str(S),files=len(deriv),remote_or_model=False)))

