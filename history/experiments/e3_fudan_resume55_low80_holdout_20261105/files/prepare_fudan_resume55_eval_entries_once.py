"""Five new-use evaluation entries. Metadata/frontdoor only, no selected model or SDK operations."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent;F='source_fudan_frozen_native_eval_v8_resume55';P='source_fudan_frozen_parent_v8_resume55';H=lambda b:hashlib.sha256(b).hexdigest()
newnames=('stage_fudan_resume55_frozen_original_once.py','export_fudan_resume55_pi_for_mujoco_once.py','dispatch_fudan_resume55_frozen_original_once.py','collect_fudan_resume55_frozen_original_once.py','evaluate_fudan_resume55_pi_mujoco31_lowrise_once.py');assert all(not(D/n).exists()for n in newnames)
mean=(D/F/'frozen_sequence_mean.py').read_bytes();tree=ast.parse(mean.decode('utf8'));mean_sha=H(mean);constants={}
for n in tree.body:
 if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
  try:constants[n.targets[0].id]=ast.literal_eval(n.value)
  except (ValueError,TypeError):pass
B='FDN_FULL_LEARNER_CONTINUATION_55AFA_FRESH_N20000_ENV';K='fdn_full_learner_resume55afa_n20000_finite25';source55='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7';assert constants['BRANCH_KIND']==B and constants['SOURCE_KIND']==K
# The closed metadata gate is adapted from an actually executed full-learner continuation, not a fresh warm save.
s=(D/'stage_fudan_timeout8_frozen_original_once.py').read_text(encoding='utf8')
for a,b in [('FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_TIMEOUT8_ENV',B),('fdn_n20000_full_learner_timeout8_source',K),('FDNTIMEOUT8_FROZEN_','FDNRESUME55_FROZEN_'),('source_fudan_frozen_native_eval_v3_timeout8',F),('source_fudan_frozen_parent_v3_timeout8',P),('386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2','a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9'),('8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78',source55)]:s=s.replace(a,b)
s=s.replace('BASE = dict(updates=133, policy_optimizer_steps=2660,\n            encoder_optimizer_steps=2660, transitions_seen=78822912)','BASE = dict(updates=25, policy_optimizer_steps=500, encoder_optimizer_steps=500, transitions_seen=24000000)').replace('["version"] == 3','["version"] == 8').replace('Qualified version3 timeout8 E3 full save required','Qualified Root8 complete learner continuation required').replace('Pinned base133','Pinned base25').replace('need(wu > 0 and','need(0 < wu <= 25 and').replace('SINGLE_GPU_E3_FDN_TIMEOUT8_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN','SINGLE_GPU_E3_FDN_RESUME55_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN')
s=s.replace('intent["parent_pid"] == f["parent_pid"]','f["resource_binding"]["actual_parent_pid"] == f["parent_pid"]')
s=s.replace('f["original_mother_reads"] == 0 and f["ancestor_N4096_reads"] == 0 and f["learner_source_reads"] == 1 and\n           source_receipt["ancestor_N4096_reads"] == 0 and\n           f["ancestral_N4096_checkpoint"]["source_sha256"] == SOURCE_4K_SHA,','f["original_mother_reads"] == 0 and f["learner_source_reads"] == 1 and source_receipt["original_mother_reads"] == 0 and source_receipt["learner_source_reads"] == 1,')
s=s.replace('                         ("ancestral_N4096_checkpoint", f["ancestral_N4096_checkpoint"]),\n','').replace('latest["original_mother_reads"] == 0 and latest["ancestor_N4096_reads"] == 0 and latest["learner_source_reads"] == 1','latest["original_mother_reads"] == 0 and latest["learner_source_reads"] == 1').replace('f["task_runtime_overlay"]["bytes"] == 8571','f["task_runtime_overlay"]["bytes"] == 12745')
a='    selected = dict(';i=s.index(a)
s=s[:i]+'''    need(source_receipt["source_schema_version"] == 7 and source_receipt["source_bytes"] == 146247985 and
         source_receipt["physical_byte_opens"] == source_receipt["SHA_calculations"] == source_receipt["CPU_decodes"] == 1 and
         source_receipt["complete_learner_loaded"] is True and source_receipt["learner_load_uses_unchanged_core_clone"] is True and
         lineage["source_native_policy_steps"] == lineage["source_optimized_control_steps"] == 1200 and
         lineage["source_unoptimized_control_steps"] == lineage["source_pending_rollout_completed_control_steps"] == 0,
         "Actual Root7 complete55 source one-read cloned learner continuation required")
    for packet in (f, latest, intent):
        need(packet["full_learner_resume"] is True and packet["bad_candidate_reads"] == packet["inherited_old_iterations"] == 0,
             "Full learner continuation, no bad or RSL iteration inheritance")
    for key, expected in dict(initial_std=.05, learning_rate=1e-5, min_learning_rate=1e-7,
                              max_learning_rate=1e-4, encoder_learning_rate=.001).items():
        need(init["learner_config"][key] == expected, "Unchanged source configuration required: " + key)
''' +s[i:]
assert 'ancestral_N4096_checkpoint' not in s and 'ancestor_N4096_reads' not in s
labels=('MOTHER','EXCLUDED_N4096','EXCLUDED_PREVIOUS_N20000','EXCLUDED_TIMEOUT8','EXCLUDED_FRESH25','EXCLUDED_HEIGHTGATE','EXCLUDED_LOWSTD005','EXCLUDED_SOURCE55')
# Some old paths use string concatenation; extract literal constant expressions safely from AST only.
values={}
def val(n):
 if isinstance(n,ast.Constant):return n.value
 if isinstance(n,ast.Name):return values[n.id]
 if isinstance(n,ast.BinOp)and isinstance(n.op,ast.Add):return val(n.left)+val(n.right)
 raise ValueError('Not a constant')
for n in tree.body:
 if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
  try:values[n.targets[0].id]=val(n.value)
  except (ValueError,KeyError):pass
paths=tuple(values[l+'_PATH']for l in labels);shas=tuple(values[l+'_SHA']for l in labels);assert len(set(paths))==len(set(shas))==8
s=s.replace('PREFIX = "FDNRESUME55_FROZEN_"','EXCLUDED_SOURCE_PATHS = '+repr(paths)+'\nEXCLUDED_SOURCE_SHAS = '+repr(shas)+'\nPREFIX = "FDNRESUME55_FROZEN_"').replace('selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA)','selected["sha256"] not in EXCLUDED_SOURCE_SHAS and str(selected_path) not in EXCLUDED_SOURCE_PATHS')
# Exact same closed-metadata gate for wholeCPU deployment export; preserve actual network extraction/serialization.
e=(D/'export_fudan_lrschedule001_pi_for_mujoco_once.py').read_text(encoding='utf8').replace('source_fudan_frozen_native_eval_v7_lrschedule001',F).replace('FDNLR001_PI_ONLY_EXPORT_','FDNRESUME55_PI_ONLY_EXPORT_').replace('c2253bc20b40b09b0d5d131ddeee528a8eba708c48e9c74e2699212e12b3ccae',mean_sha)
start='    closed_path = Path(args.closed)\n';se='    # All closure validation above precedes every mkdir, connector import and upload.\n';ee='    # Every check above is the existing closed metadata gate, before marker/mkdir/connect.\n';gate=s[s.index(start):s.index(se)];e=e[:e.index(start)]+gate+e[e.index(ee):]
# Header constants used by the identical gate must also match; remote literal has separate own imports.
st=ast.parse(s);et=ast.parse(e);replace_headers={'KIND','BRANCH','EVAL_KIND','BASE','COUNTERS','MOTHER_SHA','SOURCE_4K_SHA','LEARNER_SHA','SOURCE_KIND','OVERLAY_SHA','TASKS','EXCLUDED_SOURCE_PATHS','EXCLUDED_SOURCE_SHAS'}
sl=s.splitlines(keepends=True);header=''.join(''.join(sl[n.lineno-1:n.end_lineno])for n in st.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in replace_headers for t in n.targets));el=e.splitlines(keepends=True)
for n in reversed(et.body):
 if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in replace_headers for t in n.targets):del el[n.lineno-1:n.end_lineno]
e=''.join(el);loc=e.index('PREFIX = ');e=e[:loc]+header+e[loc:]
e=e.replace('EXCLUDED_LOWSTD005_PATH,EXCLUDED_LOWSTD005_SHA\n','EXCLUDED_LOWSTD005_PATH,EXCLUDED_LOWSTD005_SHA,EXCLUDED_SOURCE55_PATH,EXCLUDED_SOURCE55_SHA\n').replace('EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_LOWSTD005_PATH))and','EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_LOWSTD005_PATH,EXCLUDED_SOURCE55_PATH))and').replace("EXCLUDED_HEIGHTGATE_SHA,EXCLUDED_LOWSTD005_SHA),'Qualified own NEW N20000 source only'","EXCLUDED_HEIGHTGATE_SHA,EXCLUDED_LOWSTD005_SHA,EXCLUDED_SOURCE55_SHA),'Qualified own NEW N20000 source only'")
p=(D/'dispatch_fudan_lrschedule001_frozen_original_once.py').read_text(encoding='utf8').replace('FDNLR001_FROZEN_','FDNRESUME55_FROZEN_').replace('fdn_lrschedule001_frozen_outer_wait.py','fdn_resume55_frozen_outer_wait.py')
c=(D/'collect_fudan_lrschedule001_frozen_original_once.py').read_text(encoding='utf8').replace('FDNLR001_FROZEN_','FDNRESUME55_FROZEN_').replace('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V7_LRSCHEDULE001','FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V8_RESUME55')
j=(D/'evaluate_fudan_lrschedule001_pi_mujoco31_lowrise_once.py').read_text(encoding='utf8').replace('source_fudan_frozen_native_eval_v7_lrschedule001',F).replace('FDN_LR001_MUJOCO31_','FDN_RESUME55_MUJOCO31_').replace('c2253bc20b40b09b0d5d131ddeee528a8eba708c48e9c74e2699212e12b3ccae',mean_sha).replace("p['schema_version']==7","p['schema_version']==8").replace("'cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244')","'cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244','"+source55+"')")
texts=(s,e,p,c,j)
for name,text in zip(newnames,texts):ast.parse(text);compile(text,name,'exec')
remote=next(n.value.value for n in ast.parse(e).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='REMOTE_EXPORT'for t in n.targets));rt=ast.parse(remote);compile(rt,'resume55_cpu_export','exec');available={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}|set(values);imports={a.name for n in ast.walk(rt)if isinstance(n,ast.ImportFrom)and n.module=='frozen_sequence_mean'for a in n.names};assert imports<=available and {'EXCLUDED_SOURCE55_PATH','EXCLUDED_SOURCE55_SHA'}<=imports
old=ast.parse((D/'evaluate_fudan_lrschedule001_pi_mujoco31_lowrise_once.py').read_text(encoding='utf8'));new=ast.parse(j)
for name in('MotherMean','body_contact_forces','reset_pose','run_case'):assert ast.dump(next(n for n in old.body if getattr(n,'name',None)==name),include_attributes=False)==ast.dump(next(n for n in new.body if getattr(n,'name',None)==name),include_attributes=False)
for name in ('publish_fudan_resume55_closed_quality_once.py','freeze_fudan_resume55_w13_first_real_metadata_once.py'):
 text=(D/name).read_text(encoding='utf8');ast.parse(text);compile(text,name,'exec')
for name,text in zip(newnames,texts):(D/name).write_text(text,encoding='utf8',newline='\n')
print('Five UNUSED Root8 entries ready; exact shared closed frontdoor; original resources/physics/network preserved; AST only/no physical/model/SDK/SSH')
