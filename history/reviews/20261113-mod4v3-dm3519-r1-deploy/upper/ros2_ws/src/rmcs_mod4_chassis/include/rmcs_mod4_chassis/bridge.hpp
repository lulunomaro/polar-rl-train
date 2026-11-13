#pragma once
#include "mod4_wire.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <string>

namespace mod4 {
struct Command {
    float vx=0, vy=0, wz=0, height=.28f;
    std::uint32_t flags=0;
};
struct Telemetry {
    std::uint32_t sequence=0, board_ms=0, status=0;
    std::array<float,6> q{}, qd{}, action{}, model_torque{};
    std::array<float,3> gyro{}, gravity{};
};
// Receipt-time freshness uses steady milliseconds; ROS clock changes do not arm.
class CommandSource {
public:
    bool velocity(float vx,float vy,float wz,std::uint64_t now);
    bool height(float metres);
    void arm(bool value,std::uint64_t now);
    void estop(bool value);
    void disarm();
    Command sample(std::uint64_t now);
private:
    Command command_{};
    std::uint64_t velocity_ms_=0;
    bool have_velocity_=false, last_arm_=false, armed_=false, estop_=false;
};
class SerialBridge {
public:
    explicit SerialBridge(std::string device);
    ~SerialBridge();
    SerialBridge(const SerialBridge&)=delete;
    SerialBridge& operator=(const SerialBridge&)=delete;
    // Nonblocking, bounded I/O. Call every 20ms or faster.
    void update(std::uint64_t now,const Command& command);
    bool connected() const { return fd_>=0; }
    const std::string& error() const { return error_; }
    std::function<void(const Telemetry&)> on_telemetry;
private:
    static void frame(void*,std::uint8_t,std::uint32_t,const std::uint8_t*,std::uint16_t);
    bool open_port();
    void close_port(const std::string& reason);
    bool flush();
    std::string device_, error_;
    int fd_=-1;
    bool tried_=false, first_frame_=true;
    std::uint64_t retry_ms_=0, sent_ms_=0, pending_ms_=0;
    std::uint32_t sequence_=0;
    Mod4WireParser parser_{};
    std::array<std::uint8_t,MOD4_WIRE_FRAME_MAX> tx_{};
    std::size_t used_=0, offset_=0;
};
std::uint64_t steady_ms();
}
