"""Run the real ROS node or RMCS plugin against a PTY; never opens a motor port."""
import binascii
import json
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
def encode(kind,seq,payload):
    data=b'M4RL'+struct.pack('<BBHI',1,kind,len(payload),seq)+payload
    return data+struct.pack('<H',binascii.crc_hqx(data,0xffff))

if __name__=='__main__':
    import rclpy
    from geometry_msgs.msg import TwistStamped
    from std_msgs.msg import Bool,Float32,UInt32
    mode=sys.argv[1]
    assert mode in ('node','rmcs')
    attempt=sys.argv[2] if len(sys.argv)>2 else 'attempt1'
    dest=ROOT/'reports'/f'ros_loopback_{mode}_{attempt}.json'
    assert not dest.exists()
    report=dict(mode=mode,attempt=attempt,physical_ports_opened=0,telemetry='synthetic fixture, not measured motors')
    master,slave=pty.openpty();port=os.ttyname(slave);os.set_blocking(master,False)
    config=ROOT/'reports'/f'ros_loopback_{mode}_{attempt}.yaml'
    config.write_text('rmcs_executor:\n  ros__parameters:\n    update_rate: 1000.0\n    components: ["mod4::ChassisComponent -> mod4_chassis"]\nmod4_chassis:\n  ros__parameters:\n    device: '+port+'\n',encoding='utf-8')
    args=['ros2','run','rmcs_executor','rmcs_executor'] if mode=='rmcs' else ['ros2','run','rmcs_mod4_chassis','mod4_chassis_node']
    args+=['--ros-args','--params-file',str(config)]
    log=ROOT/'reports'/f'ros_loopback_{mode}_{attempt}_process.log'
    process=None;node=None;buffer=bytearray();commands=[];statuses=[];seq=0
    try:
        with log.open('w',encoding='utf-8') as out:
            process=subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        rclpy.init();node=rclpy.create_node('mod4_loopback_test')
        vel=node.create_publisher(TwistStamped,'/mod4/cmd_vel',1)
        arm=node.create_publisher(Bool,'/mod4/arm',1)
        estop=node.create_publisher(Bool,'/mod4/estop',1)
        height=node.create_publisher(Float32,'/mod4/height',1)
        sub=node.create_subscription(UInt32,'/mod4/status',lambda m:statuses.append(m.data),1)
        def pump(seconds,send_velocity=True):
            global seq
            deadline=time.monotonic()+seconds;next_pub=0
            while time.monotonic()<deadline:
                assert process.poll() is None, f'process exited {process.returncode}'
                now=time.monotonic()
                if send_velocity and now>=next_pub:
                    m=TwistStamped();m.header.stamp=node.get_clock().now().to_msg();m.twist.linear.x=.2;m.twist.angular.z=.3;vel.publish(m);next_pub=now+.02
                payload=struct.pack('<II30f',1234,1024,*([0.0]*30))
                os.write(master,encode(2,seq,payload));seq+=1
                rclpy.spin_once(node,timeout_sec=.005)
                if select.select([master],[],[],.005)[0]:
                    try:buffer.extend(os.read(master,4096))
                    except BlockingIOError:pass
                while len(buffer)>=14:
                    if buffer[:4]!=b'M4RL':del buffer[0];continue
                    n=struct.unpack_from('<H',buffer,6)[0]
                    if n>160:del buffer[0];continue
                    if len(buffer)<14+n:break
                    frame=bytes(buffer[:14+n]);del buffer[:14+n]
                    if binascii.crc_hqx(frame[:-2],0xffff)!=struct.unpack_from('<H',frame,len(frame)-2)[0]:continue
                    if frame[5]==1 and n==20:
                        vx,vy,wz,h,flags=struct.unpack_from('<4fI',frame,12)
                        commands.append(dict(vx=vx,vy=vy,wz=wz,height=h,flags=flags))
        deadline=time.monotonic()+12
        while (vel.get_subscription_count()==0 or arm.get_subscription_count()==0) and time.monotonic()<deadline:
            pump(.2)
        pump(.2)
        assert vel.get_subscription_count()>0 and arm.get_subscription_count()>0, 'ROS discovery failed'
        arm.publish(Bool(data=False));estop.publish(Bool(data=False));height.publish(Float32(data=.30));pump(.2)
        start=len(commands);arm.publish(Bool(data=True));pump(.4)
        active=[c for c in commands[start:] if c['flags']==1]
        assert active and abs(active[-1]['vx']-.2)<1e-6 and abs(active[-1]['wz']-.3)<1e-6 and abs(active[-1]['height']-.30)<1e-6,'arm/velocity/height not delivered'
        pump(.3,False);assert commands[-1]['flags']==0,'command source timeout did not disarm'
        pump(.2);assert commands[-1]['flags']==0,'velocity refresh auto rearmed'
        arm.publish(Bool(data=False));pump(.1);arm.publish(Bool(data=True));pump(.2)
        assert commands[-1]['flags']==1,'explicit rearm failed'
        estop.publish(Bool(data=True));pump(.2);assert commands[-1]['flags']==2,'estop not delivered'
        assert statuses and statuses[-1]==1024,'telemetry not published as real ROS status'
        report.update(passed=True,commands=len(commands),statuses=len(statuses),last_commands=commands[-8:],checks=['real_ROS_discovery','plugin_load' if mode=='rmcs' else 'standalone_node','vx_wz_height_arm','100ms_velocity_timeout','no_auto_rearm','explicit_rearm','estop','telemetry_ROS_publication'])
    except Exception:
        report.update(passed=False,error=traceback.format_exc(),commands=commands[-12:],statuses=len(statuses))
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid,signal.SIGINT)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=5)
        if node is not None:node.destroy_node();rclpy.shutdown()
        os.close(master);os.close(slave)
    report['process_log']=str(log);report['config']=str(config)
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
    sys.exit(0 if report['passed'] else 1)
