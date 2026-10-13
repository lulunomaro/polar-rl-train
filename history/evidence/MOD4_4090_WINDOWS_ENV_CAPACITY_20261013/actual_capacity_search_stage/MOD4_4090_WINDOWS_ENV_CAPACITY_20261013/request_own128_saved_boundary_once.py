"""New human-approved environment resize: own save-stop, no signal/restart."""
from pathlib import Path
import json,time,sys,base64
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';S=R+'/temporary_scope128_memory20GB_logger_ready_v12_20261013'
def main():
 out=D/'reports/OWN128_ENV_INCREASE_SAVE_STOP_ACTUAL.json';assert not out.exists()
 code="""from pathlib import Path;import psutil,json,time,os
s=Path('"""+S+"""');a=s/'attempts/temporary2048_train_v1';r=json.loads((a/'DISPATCH_RECEIPT.json').read_bytes());latest=json.loads((a/'output/WINDOWS4090_LATEST_COMPLETE.json').read_bytes())
assert latest['actual_updates']>0 and not (a/'EXIT_RECEIPT.json').exists()
for name in ('parent','child'):
 row=r[name];p=psutil.Process(row['pid']);assert p.create_time()==row['created'] and p.cmdline()==row['argv']
stop=a/'STOP_AFTER_SAVE';receipt=dict(epoch=time.time(),human_authorized_environment_count_increase=True,reason='complete_current_update_save_exit_for_new_capacity_scope',owner=r,latest=latest,no_process_signal_no_oldscope_restart_no_budgetwrite=True)
if stop.exists():receipt['previous_existing_request']=json.loads(stop.read_bytes());receipt['new_request_created']=False
else:
 with stop.open('x',encoding='utf8') as f:f.write(json.dumps(receipt,indent=2));f.flush();os.fsync(f.fileno())
 receipt['new_request_created']=True
print(json.dumps(receipt))
"""
 enc=base64.b64encode(code.encode()).decode();actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+enc+"'))\"",35));out.write_text(json.dumps(actual,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),save_stop_requested=actual['new_request_created'],current_saved_updates=actual['latest']['actual_updates'])))
if __name__=='__main__':main()
