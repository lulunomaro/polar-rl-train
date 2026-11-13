#include "endpoint.hpp"
int main(int argc,char **argv) {
    rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<mod4::Endpoint>("mod4_chassis"));rclcpp::shutdown();return 0;
}
