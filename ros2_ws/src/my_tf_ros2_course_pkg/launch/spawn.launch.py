import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():


    # Position and orientation
    # [X, Y, Z]
    position = [0.0, 0.0, 1.0]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    # Base Name or robot
    robot_base_name = "unicycle_bot"


    entity_name = robot_base_name

    # Spawn ROBOT Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='cam_bot_spawn_entity',
        output='screen',
        emulate_tty=True,
        arguments=['-entity',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]
                                                     ), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]
                                                        ), '-Y', str(orientation[2]),
                   '-topic', '/unicycle_bot_robot_description'
                   ]
    )

    ####### DATA INPUT ##########
    urdf_file = 'unicycle.urdf'
    #xacro_file = "box_bot.xacro"
    package_description = "unicycle_robot_pkg"

    ####### DATA INPUT END ##########
    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)

    robot_desc = xacro.process_file(robot_desc_path)
    xml = robot_desc.toxml()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='unicycle_robot_state_publisher',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': xml}],
        remappings=[("/robot_description", "/unicycle_bot_robot_description")
        ],
        output="screen"
    )


    # create and return launch description object
    return LaunchDescription(
        [
            spawn_robot,
            robot_state_publisher_node
        ]
    )