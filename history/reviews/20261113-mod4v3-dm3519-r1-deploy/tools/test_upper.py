"""Build and test actual Linux serial transport using a PTY, without ROS stubs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'upper/ros2_ws/src/rmcs_mod4_chassis'
def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',errors='replace')
    return dict(command=list(map(str,args)),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
if __name__=='__main__':
    attempt=sys.argv[1] if len(sys.argv)>1 else 'manual'
    report=dict(attempt=attempt,time=time.strftime('%Y-%m-%dT%H:%M:%S%z'),ros_build='not_run_no_ROS2_or_rmcs_executor_installed')
    report['wire_identical']=all((ROOT/'firmware/application/mod4_rl'/name).read_bytes()==(PACKAGE/dest/name).read_bytes() for name,dest in [('mod4_wire.h','include'),('mod4_wire.c','src')])
    build=ROOT/'build/upper'
    report['configure']=run(['cmake','-S',PACKAGE,'-B',build,'-DMOD4_WITH_ROS=OFF','-DBUILD_TESTING=ON','-DCMAKE_BUILD_TYPE=RelWithDebInfo'])
    if not report['configure']['returncode']:
        report['build']=run(['cmake','--build',build,'-j','2'])
        if not report['build']['returncode']:report['test']=run(['ctest','--test-dir',build,'--output-on-failure','-V'])
    report['passed']=report['wire_identical'] and report.get('test',{}).get('returncode',1)==0
    dest=ROOT/'reports'/('upper_'+attempt+'.json');assert not dest.exists()
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
    sys.exit(0 if report['passed'] else 1)
