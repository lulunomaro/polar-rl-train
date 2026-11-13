#include "rmcs_mod4_chassis/bridge.hpp"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <pty.h>
#include <stdexcept>
#include <unistd.h>
#include <vector>
#define CHECK(x) do {if(!(x))throw std::runtime_error(#x);}while(0)

struct Commands {std::vector<mod4::Command> values;};
static void received(void *context,std::uint8_t type,std::uint32_t,const std::uint8_t *p,std::uint16_t n) {
    if(type!=1||n!=20)return;
    static_cast<Commands*>(context)->values.push_back({mod4_wire_float(p),mod4_wire_float(p+4),mod4_wire_float(p+8),mod4_wire_float(p+12),mod4_wire_u32(p+16)});
}
int main() {
    try {
        mod4::CommandSource source;
        source.arm(true,1000);CHECK(source.sample(1000).flags==0);
        CHECK(source.velocity(.2f,0,.3f,1000));source.arm(false,1000);source.arm(true,1000);
        CHECK(source.sample(1000).flags==1 && source.sample(1000).vx==.2f);
        CHECK(source.sample(1101).flags==0);source.velocity(.2f,0,0,1102);source.arm(true,1102);
        CHECK(source.sample(1102).flags==0);source.arm(false,1103);source.arm(true,1103);CHECK(source.sample(1103).flags==1);
        source.estop(true);CHECK(source.sample(1104).flags==2);source.estop(false);CHECK(source.sample(1105).flags==0);
        CHECK(!source.velocity(0,.1f,0,1110));CHECK(!source.height(NAN));CHECK(!source.height(.5f));CHECK(source.height(.30f));
        std::puts("PASS command_contract_freshness_explicit_rearm");
        int master=-1,slave=-1;char name[128]{};
        CHECK(openpty(&master,&slave,name,nullptr,nullptr)==0);fcntl(master,F_SETFL,O_NONBLOCK);
        mod4::SerialBridge bridge(name);mod4::Command cmd{.2f,0,.3f,.28f,1};
        bridge.update(2000,cmd);CHECK(bridge.connected());
        std::uint8_t bytes[4096];Mod4WireParser command_parser{};Commands commands;
        auto read_commands=[&]{const auto n=::read(master,bytes,sizeof(bytes));CHECK(n>0);mod4_wire_feed(&command_parser,bytes,static_cast<std::size_t>(n),received,&commands);};
        read_commands();CHECK(commands.values.size()==1 && commands.values.back().flags==0);
        bridge.update(2020,cmd);read_commands();CHECK(commands.values.size()==2 && commands.values.back().flags==1);
        CHECK(commands.values.back().vx==cmd.vx && commands.values.back().wz==cmd.wz);
        unsigned telemetry_count=0;
        bridge.on_telemetry=[&](const mod4::Telemetry& t){
            telemetry_count++;CHECK(t.sequence==7 && t.board_ms==1234 && t.status==1024);
            CHECK(t.q[0]==2.2480165f && t.qd[4]==20.0f && t.gravity[2]==-1.0f && t.model_torque[5]==-2.0f);
        };
        std::uint8_t payload[128]{},frame[174];mod4_wire_put_u32(payload,1234);mod4_wire_put_u32(payload+4,1024);
        mod4_wire_put_float(payload+8,2.2480165f);mod4_wire_put_float(payload+48,20);mod4_wire_put_float(payload+76,-1);mod4_wire_put_float(payload+124,-2);
        const auto length=mod4_wire_encode(2,7,payload,128,frame);
        auto bad=std::vector<std::uint8_t>(frame,frame+length);bad[33]^=1;CHECK(::write(master,bad.data(),bad.size())==static_cast<ssize_t>(bad.size()));
        bridge.update(2021,cmd);CHECK(telemetry_count==0);
        for(std::size_t i=0;i<length;i++){CHECK(::write(master,frame+i,1)==1);bridge.update(2022+i,cmd);}
        CHECK(telemetry_count==1);
        std::puts("PASS posix_pty_commands_crc_partial_telemetry");
        ::close(slave);::close(master);bridge.update(2220,cmd);CHECK(!bridge.connected());
        std::puts("PASS serial_hangup_detected");return 0;
    } catch(const std::exception& e){std::fprintf(stderr,"FAIL %s\n",e.what());return 1;}
}
