#pragma once
#include "rmcs_mod4_chassis/bridge.hpp"
#include <cmath>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float32.hpp>
#include <std_msgs/msg/float32_multi_array.hpp>
#include <std_msgs/msg/u_int32.hpp>

namespace mod4 {
class Endpoint final : public rclcpp::Node {
public:
    explicit Endpoint(const std::string& name):Node(name),bridge_(declare_parameter<std::string>("device","/dev/ttyACM0")) {
        const auto qos=rclcpp::QoS(1).reliable().durability_volatile();
        velocity_=create_subscription<geometry_msgs::msg::TwistStamped>("/mod4/cmd_vel",qos,[this](const geometry_msgs::msg::TwistStamped::SharedPtr m){
            const auto& t=m->twist;
            if(t.linear.z!=0||t.angular.x!=0||t.angular.y!=0){source_.velocity(NAN,0,0,steady_ms());return;}
            if(!source_.velocity(static_cast<float>(t.linear.x),static_cast<float>(t.linear.y),static_cast<float>(t.angular.z),steady_ms()))
                RCLCPP_WARN(get_logger(),"Rejected out-of-contract chassis velocity");
        });
        height_=create_subscription<std_msgs::msg::Float32>("/mod4/height",qos,[this](const std_msgs::msg::Float32::SharedPtr m){source_.height(m->data);});
        arm_=create_subscription<std_msgs::msg::Bool>("/mod4/arm",qos,[this](const std_msgs::msg::Bool::SharedPtr m){source_.arm(m->data,steady_ms());});
        estop_=create_subscription<std_msgs::msg::Bool>("/mod4/estop",qos,[this](const std_msgs::msg::Bool::SharedPtr m){source_.estop(m->data);});
        status_=create_publisher<std_msgs::msg::UInt32>("/mod4/status",qos);
        state_=create_publisher<std_msgs::msg::Float32MultiArray>("/mod4/state",qos);
        bridge_.on_telemetry=[this](const Telemetry& t){
            std_msgs::msg::UInt32 status;status.data=t.status;status_->publish(status);
            std_msgs::msg::Float32MultiArray state;
            state.data.insert(state.data.end(),t.q.begin(),t.q.end());state.data.insert(state.data.end(),t.qd.begin(),t.qd.end());
            state.data.insert(state.data.end(),t.gyro.begin(),t.gyro.end());state.data.insert(state.data.end(),t.gravity.begin(),t.gravity.end());
            state.data.insert(state.data.end(),t.action.begin(),t.action.end());state.data.insert(state.data.end(),t.model_torque.begin(),t.model_torque.end());
            state_->publish(state);
        };
        timer_=create_wall_timer(std::chrono::milliseconds(5),[this]{
            if(!bridge_.connected())source_.disarm();
            const auto now=steady_ms();bridge_.update(now,source_.sample(now));
            if(!bridge_.connected())RCLCPP_WARN_THROTTLE(get_logger(),*get_clock(),2000,"MOD4 serial: %s",bridge_.error().c_str());
        });
    }
private:
    CommandSource source_;SerialBridge bridge_;
    rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr velocity_;
    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr height_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr arm_,estop_;
    rclcpp::Publisher<std_msgs::msg::UInt32>::SharedPtr status_;
    rclcpp::Publisher<std_msgs::msg::Float32MultiArray>::SharedPtr state_;
    rclcpp::TimerBase::SharedPtr timer_;
};
}
