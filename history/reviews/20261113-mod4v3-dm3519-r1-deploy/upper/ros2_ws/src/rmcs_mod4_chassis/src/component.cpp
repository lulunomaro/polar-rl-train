#include "endpoint.hpp"
#include <pluginlib/class_list_macros.hpp>
#include <rmcs_executor/component.hpp>

namespace mod4 {
// ROS subscriptions above are real ROS topics. RMCS only schedules this wrapper.
class ChassisComponent final : public rmcs_executor::Component {
public:
    ChassisComponent() {
        if(!rclcpp::ok())rclcpp::init(0,nullptr);
        node_=std::make_shared<Endpoint>(get_component_name());executor_.add_node(node_);
    }
    void update() override { executor_.spin_some(std::chrono::milliseconds(1)); }
private:
    std::shared_ptr<Endpoint> node_;
    rclcpp::executors::SingleThreadedExecutor executor_;
};
}
PLUGINLIB_EXPORT_CLASS(mod4::ChassisComponent,rmcs_executor::Component)
