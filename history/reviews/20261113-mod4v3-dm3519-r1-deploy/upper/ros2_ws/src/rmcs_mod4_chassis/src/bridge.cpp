#include "rmcs_mod4_chassis/bridge.hpp"
#include <cerrno>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <utility>

namespace mod4 {
std::uint64_t steady_ms() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
}
bool CommandSource::velocity(float vx,float vy,float wz,std::uint64_t now) {
    if (!std::isfinite(vx)||!std::isfinite(vy)||!std::isfinite(wz)||
        std::fabs(vx)>2.2f||vy!=0||std::fabs(wz)>14.137168f) {
        have_velocity_=false; disarm(); return false;
    }
    command_.vx=vx;command_.vy=0;command_.wz=wz;velocity_ms_=now;have_velocity_=true;return true;
}
bool CommandSource::height(float h) {
    if (!std::isfinite(h)||h<.2f||h>.4f) { disarm(); return false; }
    command_.height=h;return true;
}
void CommandSource::arm(bool value,std::uint64_t now) {
    if (!value) armed_=false;
    else if (!last_arm_ && !estop_ && have_velocity_ && now-velocity_ms_<=100) armed_=true;
    last_arm_=value;
}
void CommandSource::estop(bool value) { estop_=value;if(value)disarm(); }
void CommandSource::disarm() { armed_=false; }
Command CommandSource::sample(std::uint64_t now) {
    if (!have_velocity_||now-velocity_ms_>100) disarm();
    Command out=command_;
    if (!armed_) { out.vx=out.vy=out.wz=0; }
    out.flags=estop_?MOD4_WIRE_ESTOP:armed_?MOD4_WIRE_ARM:0;
    return out;
}
SerialBridge::SerialBridge(std::string device):device_(std::move(device)) {}
SerialBridge::~SerialBridge() { if(fd_>=0)::close(fd_); }
void SerialBridge::close_port(const std::string& reason) {
    if(fd_>=0)::close(fd_);
    fd_=-1;used_=offset_=0;parser_={};first_frame_=true;error_=reason;
}
bool SerialBridge::open_port() {
    fd_=::open(device_.c_str(),O_RDWR|O_NOCTTY|O_NONBLOCK|O_CLOEXEC);
    if(fd_<0){error_=std::strerror(errno);return false;}
    termios t{};
    if(tcgetattr(fd_,&t)<0){close_port(std::strerror(errno));return false;}
    cfmakeraw(&t);cfsetispeed(&t,B115200);cfsetospeed(&t,B115200);
    t.c_cflag=(t.c_cflag&~(CSIZE|PARENB|CSTOPB|CRTSCTS))|CS8|CLOCAL|CREAD;
    t.c_cc[VMIN]=0;t.c_cc[VTIME]=0;
    if(tcsetattr(fd_,TCSANOW,&t)<0){close_port(std::strerror(errno));return false;}
    tcflush(fd_,TCIOFLUSH);error_.clear();first_frame_=true;return true;
}
bool SerialBridge::flush() {
    if(offset_==used_)return true;
    const auto n=::write(fd_,tx_.data()+offset_,used_-offset_);
    if(n>0)offset_+=static_cast<std::size_t>(n);
    else if(n<0&&errno!=EAGAIN&&errno!=EWOULDBLOCK&&errno!=EINTR){close_port(std::strerror(errno));return false;}
    return true;
}
void SerialBridge::frame(void *ctx,std::uint8_t type,std::uint32_t sequence,const std::uint8_t *p,std::uint16_t n) {
    auto& self=*static_cast<SerialBridge*>(ctx);
    if(type!=MOD4_WIRE_TELEMETRY||n!=128)return;
    Telemetry t;t.sequence=sequence;t.board_ms=mod4_wire_u32(p);t.status=mod4_wire_u32(p+4);
    for(unsigned i=0;i<6;i++){
        t.q[i]=mod4_wire_float(p+8+4*i);t.qd[i]=mod4_wire_float(p+32+4*i);
        t.action[i]=mod4_wire_float(p+80+4*i);t.model_torque[i]=mod4_wire_float(p+104+4*i);
    }
    for(unsigned i=0;i<3;i++){t.gyro[i]=mod4_wire_float(p+56+4*i);t.gravity[i]=mod4_wire_float(p+68+4*i);}
    if(self.on_telemetry)self.on_telemetry(t);
}
void SerialBridge::update(std::uint64_t now,const Command& command) {
    if(fd_<0){
        if(tried_&&now-retry_ms_<1000)return;
        retry_ms_=now;tried_=true;if(!open_port())return;
    }
    std::uint8_t bytes[512];
    for(unsigned batch=0;batch<4;batch++){
        const auto n=::read(fd_,bytes,sizeof(bytes));
        if(n>0)mod4_wire_feed(&parser_,bytes,static_cast<std::size_t>(n),frame,this);
        else if(n==0||(n<0&&(errno==EAGAIN||errno==EWOULDBLOCK||errno==EINTR)))break;
        else {close_port(std::strerror(errno));return;}
    }
    if(offset_<used_){
        if(now-pending_ms_>100){close_port("serial write timeout");return;}
        if(!flush()||offset_<used_)return;
    }
    if(!first_frame_&&now-sent_ms_<20)return;
    std::uint8_t payload[20];Command out=command;
    // Always send a disarm first on each new connection.
    if(first_frame_){out.flags=0;out.vx=out.vy=out.wz=0;}
    mod4_wire_put_float(payload,out.vx);mod4_wire_put_float(payload+4,out.vy);
    mod4_wire_put_float(payload+8,out.wz);mod4_wire_put_float(payload+12,out.height);
    mod4_wire_put_u32(payload+16,out.flags);
    used_=mod4_wire_encode(MOD4_WIRE_COMMAND,sequence_++,payload,20,tx_.data());offset_=0;
    sent_ms_=pending_ms_=now;first_frame_=false;flush();
}
}
