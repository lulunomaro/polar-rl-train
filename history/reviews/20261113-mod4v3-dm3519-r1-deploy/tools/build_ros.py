"""Build real RMCS dependencies and our plugin inside the task's private overlay."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    attempt=sys.argv[1] if len(sys.argv)>1 else 'manual'
    report=dict(attempt=attempt,time=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    private=ROOT/'toolchain/gcc13_jammy/root'
    compiler=private/'usr/bin/g++-13'
    use_private=compiler.exists()
    suffix='ros2_gcc13' if use_private else 'ros2'
    env=os.environ.copy()
    if use_private:
        env['LD_LIBRARY_PATH']=str(private/'usr/lib/x86_64-linux-gnu')+':'+env.get('LD_LIBRARY_PATH','')
    args=['colcon','--log-base',str(ROOT/'reports'/('colcon_'+attempt)),'build',
          '--base-paths',str(ROOT/'reference/RMCS/rmcs_ws/src/rmcs_utility'),str(ROOT/'reference/RMCS/rmcs_ws/src/rmcs_executor'),str(ROOT/'upper/ros2_ws/src/rmcs_mod4_chassis'),
          '--build-base',str(ROOT/'build'/suffix),'--install-base',str(ROOT/'install'/suffix),
          '--executor','sequential','--event-handlers','console_direct+',
          '--cmake-args','-DBUILD_TESTING=OFF','-DCMAKE_BUILD_TYPE=Release']
    if use_private:args += ['-DCMAKE_C_COMPILER='+str(private/'usr/bin/gcc-13'),'-DCMAKE_CXX_COMPILER='+str(compiler)]
    command='source /opt/ros/humble/setup.bash && exec '+shlex.join(args)
    p=subprocess.run(['bash','-c',command],capture_output=True,text=True,encoding='utf-8',errors='replace',env=env)
    report.update(command=command,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,passed=p.returncode==0)
    dest=ROOT/'reports'/('ros_'+attempt+'.json');assert not dest.exists()
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));sys.exit(p.returncode)
