cmake_minimum_required(VERSION 3.8)
project(my_tf_ros2_course_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/cam_bot_odom_to_tf_pub.py
  scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
  scripts/static_broadcaster_front_turtle_frame.py
  scripts/move_generic_model.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()