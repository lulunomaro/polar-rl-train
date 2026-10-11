"""Keep generated reader error, fix only the one-argument JSON reader invocation."""
from entry_second_io import *
def main():
 rows=[]
 for src,dest,word in [('verify_entry_second_startup_save_cpu_actual.py','verify_entry_second_saved_CPU_call_reviewed_actual.py','root'),('read_entry_second_own_formal_cpu_actual.py','read_entry_second_own_formal_CPU_call_reviewed_actual.py','run')]:
  p=D/src;a=p.read_text();old="c=j("+word+"/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')";new="c=j("+word+"/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')"
  assert a.count(old)==1;b=a.replace(old,new);compile(b,dest,'exec');q=D/dest;assert not q.exists();q.write_text(b,encoding='utf8',newline='\n')
  rows.append(dict(original_path=str(p),original_SHA=H(p.read_bytes()),new_path=str(q),new_SHA=H(q.read_bytes()),only_extra_argument_to_one_argument_reader_removed=True))
 save('SAVED_CPU_READER_CALL_SCHEMA_ACTUAL_REPAIR.json',dict(epoch=time.time(),original_TypeError='<lambda>() takes 1 positional argument but 2 were given',original_reader_error_retained=True,changes=rows,startup_eighth_entry_receipt_validation_unchanged=True,all_CPU_fullstate_and_PPO_positive_validators_unchanged=True,not_physical_fault_or_GPU_replay=True))
 print(json.dumps(dict(reader_only_repaired=True,no_GPU_or_source_mutation=True)))
if __name__=='__main__':main()
