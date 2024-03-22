# Ros2-TF

## 1  TF Intro

在ROS中，“TF”代表“transform”，它指的是机器人的坐标系（frame）之间的相对位置和姿态。一个TF被创建和定义来表达一个坐标系相对于另一个坐标系的三维空间关系。这些关系可以包括平移（x, y, z坐标）和旋转（通常表示为四元数）。

一个TF是通过广播（publishing）一个`geometry_msgs/TransformStamped`消息到`/tf`话题来创建和定义的。在ROS中，`tf2_ros`库提供了相关的工具和方法来管理和广播TF信息。

- **创建和定义TF**： 通过编写一个节点（可能是C++或Python），使用`tf2_ros`库中的`TransformBroadcaster`来广播坐标系之间的关系。
- **广播TF**： 实现TF广播的节点将不断地将坐标系转换关系发送到`/tf`话题。ROS中的其他节点可以订阅这个话题，接收到这些转换数据，并用它们来计算物体在不同坐标系中的位置。

```
ros2 run tf2_ros static_transform_publisher x y z yaw pitch roll frame_id child_frame_id
```

这里的参数是：

- `x y z`：父坐标系相对于子坐标系的平移部分，以米为单位。
- `yaw pitch roll`：围绕Z轴、Y轴和X轴的旋转，以弧度为单位。
- `frame_id`：父坐标系的名称。
- `child_frame_id`：子坐标系的名称。

举个例子，如果你想要将名为`child_frame`的坐标系相对于`world`坐标系在X轴上偏移1米，无旋转，可以使用如下命令：

```
ros2 run tf2_ros static_transform_publisher 1 0 0 0 0 0 world child_frame
```

这条命令会广播一个静态的TF，将`child_frame`坐标系定位在`world`坐标系的(1, 0, 0)位置上，不进行任何旋转。

注意，因为这是一个静态的转换，它假设这个坐标系关系不会随时间变化。对于动态变化的坐标系，你通常需要写一个ROS节点来定期更新并广播这些变换。在动态场景中，这通常通过编写自己的发布者节点实现



RVIZ

```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2
```

### What Is This Course About?

This course teaches the importance of **coordinate frames** and **transforms** in robotics.

In this course, you will learn:

- What coordinate frames are, and why are they are required
- The role of transforms
- The TF2 library and how it helps to manage coordinate frames and transforms
- The tools that ROS2 has to introspect and interact with the TF2 library
- How to write a static transform broadcaster
- How to broadcast dynamic transforms
- What the Robot State Publisher node is and its role

By writing and running exercises, practice what you have learned and receive quick feedback to see how the concepts work in practice. You will apply your knowledge to simulated robots using ROS2.

## 2  TF Basics

In this unit, you will learn the following:

- The tools that ROS2 has to introspect and interact with the TF2 library
- Visualizing TF frames through TF trees
- Visualizing TF frames through RVIZ2

### 2.1  Scene Intro

This simulation has **two different robots**:

- Cam_bot
- Turtle

### 2.2  Where Is The Turtle?

- **Where is the turtle?**
- **How can you place the Cam_bot in a fixed position with respect to the turtle**?
- **How can you calculate the movements of translation and rotation that the Cam_bot should do when the turtle moves?**

这个简单的场景引出了一系列问题，比如乌龟的位置在哪里，如何将Cam_bot相对于乌龟固定在一个位置，以及当乌龟移动时Cam_bot应如何计算平移和旋转的运动等。所有这些问题都涉及到一个核心概念：坐标系之间的转换（transforms）。

坐标系转换是指如何将在一个坐标系中表达的数据转换到另一个坐标系中。比如，即使摄像头检测到了乌龟，你仍然不知道乌龟在空间中的确切位置。要确定这一点，你需要知道Cam_bot在空间中的位置、Cam_bot的中心（通常称为base_link）到摄像头传感器的距离，以及从摄像头传感器到乌龟的距离。这就需要使用坐标系和它们之间的转换。

为了在机器人编程中使用有用的值，你需要追踪其在空间中的位置。为此，你需要一个固定的参考点来评估其位置和方向。这就是为什么在描述场景中的任何对象之前，你需要一个坐标系。

在ROS中，与坐标系工作涉及使用特定的工具和库，这些工具和库可以帮助可视化和调试TF（变换框架）问题。这一单元的剩余部分旨在概述对于处理TF问题有用的工具和库。

### 2.3  View_frames in PDF Format

To **view_frames**, the ROS2 node generates a diagram with the current TF tree of the system.

Now, generate the TF tree of the current system.

The following command produces a **PDF file** in the directory where it is run:

```
ros2 run tf2_tools view_frames
```

You should now have a **PDF file** named `frames_XXXXX.pdf` containing the current **TF tree** that is currently being broadcast in the system, where `XXX` is the date when the file was generated.

- Open the `frames_XXXXX.pdf` file located where you executed the previous `view_frames` command. In this case, it is `/hose/user/frames_XXXXX.pdf`.
- Open it directly inside the IDE:

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/viewframse1_humble.png)



Here, you can see what is called a **TF tree**. It depicts all the frames of the robots in the system and their connections. The above TF tree shows 16 **coordinate frames**. Please reload the simulation if you see fewer than that, as the robots may not have appeared.

As you can see at the top, the **world** coordinate frame is the root of the tree structure. It also gives you some extra information:

- **Broadcaster**: That is the name of the TF data broadcaster.
- The **average rate** of publication, in this case, is around 5.2Hz.
- **The most recent transform** number and how old it is. **0.0** means that it is a constant transform or **Static Transform**.
- How much data the **TF buffer** has stored; in this case, 4.93 seconds of data.

### 2.4  View TF Frames Using `rqt_tf_tree`

**rqt_tf_tree** gives the same functionality as the **view_frames**, with an interesting extra:

- **You can refresh and see changes without generating another PDF file each time.**

This is useful when testing new TF broadcasts and checking if what you are using is still publishing or if it is an old publication

In this example, learn how to use the **rqt_tf_tree** tool and update the changes with a click of the refresh button when changing the TF published.

### 2.5  View TF Frames in the Terminal Using `tf_echo`

Underneath, ROS uses topics to communicate transforms. As a result, you can see all this raw data through topics.

There is a topic named **/tf** and another named **/tf_static**, where all the TFs are published. The only problem is that ALL of the frames are published there.

There is a handy command line tool that filters which transform you are interested in and shows you that one. Or, more importantly, **it calculates an indirect transform** between **two connected frames, but not directly**. This is useful and used for many applications.

**它可以计算两个连接帧之间的间接变换，但不是直接的**

The `/tf` topic only publishes the direct TFs, not all the transforms between all the frames. **tf_echo** returns the transforms between any connected frames to you.

In this example, see how to echo the **/tf** topic and then use the **tf_echo** tool to filter the `/tf` topic data.

Execute the following command to see one publication of the /tf topic directly:

```
ros2 topic echo /tf
```

output

```
transforms:
- header:
    stamp:
      sec: 4501
      nanosec: 299000000
    frame_id: odom
  child_frame_id: turtle_base_link
  transform:
    translation:
      x: -0.0026619430167396235
      y: -1.0362233570186838
      z: 0.05966079087107041
    rotation:
      x: -0.0033527500224697616
      y: -2.7084494229150955e-05
      z: 0.008117683583956063
      w: 0.9999614300296525
```

As you can see, a lot of data is published every second. So, it is difficult or impossible to get the needed data because here, you are only publishing the **TF transforms** from **one frame to the next connected frame**.

只能publishing the **TF transforms**从一个frame到下一个连接的frame。

However, if you are interested in two frames that are not directly connected, you need another tool: **tf2_echo**.

但是，如果您对未直接连接的两个frame感兴趣，则需要另一个工具：TF2_ECHO。

Now, filter the TF data with the **tf2_echo** tool to see only the transform between the `/rgb_camera_link_frame` frame and `/turtle_chassis` frame. Here are the path and accumulated transforms that this system performs and, in the end, delivers a result:


![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/tftransformecho_ros2_1.png)

The **tf2_echo** command has to be run with the following general structure:

```
ros2 run tf2_ros tf2_echo [reference_frame] [target_frame]
```

两个参数分别是开始和结束

In this scheme:

- [reference_frame] is where you **start** the transform, for instance `rgb_camera_link_frame`.
- [target_frame] is where you want to **finish** the transform, for instance, `turtle_chassis`.

This means you want to know the translation and rotation from the **reference_frame** to the **target_frame**.

```
ros2 run tf2_ros tf2_echo rgb_camera_link_frame turtle_chassis
```

Output

```
At time 1531.383000000
- Translation: [-0.200, 0.001, -0.890]
- Rotation: in Quaternion [-0.000, -0.000, 0.000, 1.000]
- Rotation: in RPY (radian) [-0.000, -0.000, 0.000]
- Rotation: in RPY (degree) [-0.003, -0.000, 0.015]
- Matrix:
  1.000 -0.000 -0.000 -0.200
```

Here, with its time stamp, you can see the translation and rotation from **rgb_camera_link_frame** to **turtle_chassis**.

**Move the turtle and see how this transform changes when you move:**

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/turtle_cmd_vel
```



### 2.6  View_frames Using RVIZ2

One of the best ways to confirm that TFs are being published and view changes is by visualizing each frame in 3D space. RVIZ2 can help with this.

RVIZ2 serves several purposes:

- **可视化/tf话题**：
  - RViz2能够可视化/tf话题发布的内容。在RViz2中，你可以直观地看到各种坐标系（frames）如何在三维空间中相互关联。
  - `/tf`话题通常用于发布各种坐标系之间的关系，这对于机器人的导航和空间定位至关重要。
- **故障排查**：
  - 如果一个坐标系（TF）没有被发布，它在RViz2中会显示为灰色并最终消失。这个可视化提示能够帮助识别和排查系统中存在的问题。
  - RViz2通过这种方式提供关于系统状态的重要信息，尤其是在坐标系关系可能存在问题时。
- **固定框架（Fixed Frame）设置**：
  - 为了在RViz2中正确渲染传感器数据或任何需要TF的信息，必须正确设置固定框架（Fixed Frame）。固定框架是用来参照渲染其他坐标系的基准点。
  - 如果固定框架没有正确设置，或者存在多个根坐标系导致TF树破损，RViz2将无法渲染相关数据。
- **多机器人系统的常见问题**：
  - 在多机器人系统中，常见的问题之一是有几个根坐标系，这会导致TF树破损。由于坐标系之间的关系在多机器人系统中可能更加复杂，维护一个健全的TF树变得尤为重要。

In this example, you represent the `/tf` topic data in 3D space and see how it changes when moving the turtle. You also tell the camera to follow a particular frame.

Execute the teleoperation command to move the turtle around with the keyboard

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/turtle_cmd_vel
```

Start RVIZ:

- Source so **RVIZ** can find the robot's meshes installed in the workspace `ros2_sims_ws`.
- To learn more about **ROS2 workspaces**, please look at the [ROS2 Basics Course](https://app.theconstructsim.com/courses/132).

```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2
```

Now, add the following elements to RVIZ and configurations:

- Set the 'Fixed Frame' to `/world` as shown below:

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/rviz2_config_1.png)

- Add two robot models with different topic configurations:
  - Find the 'Add' buttons at the bottom of the 'Displays' group and click them to add each robot model.
  - Use the 'Rename' function to set the name displayed for each model. In the image below, use the names 'TurtleRobotModel' and 'CamBotRobotModel', but you can choose any name you prefer. This name only identifies the robot model within RVIZ's left-side panel.
  - Configure the first robot model to read from the topic turtle_robot_description.
  - Configure the second robot model to read from the topic cam_bot_robot_description.
  - Check that the QoS settings are correct.

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/rviz2_config_4.png)

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/rviz2_config_3.png)

- Add an **image** reading from the topic `/camera/image_raw` and set up the correct **QoS**.

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/rviz2_config_5.png)

- Of course, add the `tf`to visualize the TFs in action:
  - Change the marker scale to 1.0 to see the frames better.

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/rviz2_config_2.png)

You should save the **RVIZ config file** somewhere so that you do not have to set this up every time you open RVIZ2.

We recommend you save it inside the **`/home/user/ros2_ws/src/`** directory and use names such as `tf_ros2_course.rviz`.

You should now see something similar to this:

**RVIZ view**

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/cambotrviz_humble1.png)

Now, notice that a frame always follows the turtle. This frame is called `turtle_attach_frame`.

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/turtlefollowframe_humble1.png)

Tell the **Cam_bot** to mimic the **position and orientation** of the `turtle_attach_frame`. By doing so, it follows the **turtle** around, and the camera captures the **turtle** all the time.

告诉cam_bot模仿turtle_attach_frame的位置和方向。通过这样做，它跟随乌龟周围，相机一直捕获乌龟。

To do so, execute the following command:

This script activates the **movement to a frame system of the Cam_bot**.

**Execute in Terminal 3**

```
source /home/simulations/ros2_sims_ws/install/setup.bash
ros2 run turtle_tf_3d_ros2 move_generic_model.py
```

Send a command to the topic `/desired_frame` to tell the **Cam_bot** to move and mimic that frame's position and orientation.

使用`ros2 topic pub`命令来发布消息到一个ROS 2话题，从而指示名为`Cam_bot`的机器人移动到并模仿另一个名为`turtle_attach_frame`的坐标系（frame）的位置和方向。

 **Execute in Terminal 4**

```
ros2 topic pub /destination_frame std_msgs/msg/String "data: 'turtle_attach_frame'"
```

- You should now get the Cam_bot following the turtle wherever it goes.

- `ros2 topic pub`是一个命令行工具，它允许你从终端向ROS 2话题发布消息，这个命令不需要编写完整的发布者节点代码。它对于快速测试和调试非常有用。
- `/destination_frame`是要发布消息的目标话题。在这个例子中，该话题可能被`Cam_bot`监视，以便它知道要移动到哪个坐标系。
- `std_msgs/msg/String`是消息类型。`std_msgs`是标准ROS消息类型之一，它提供了许多基础数据类型的消息定义，`String`是其提供的字符串消息类型。
- `"data: 'turtle_attach_frame'"`是具体的消息数据。在这种情况下，它是一个字符串类型的消息，内容是`'turtle_attach_frame'`，这表明`Cam_bot`应该移动并模仿这个名为`turtle_attach_frame`的坐标系。



As you can see, using the TFs published, the **Cam_bot** can follow the orientation that you want to target, in this case, the **turtle**.

## 3 TF Broadcasting and Listening

In this unit, you will do the following:

- Create a Static TF Broadcaster
- Create a TF Listener
- Understand the relationship between time and TFs

### 3.1  Scene Intro

In this unit, learn the basics of **TF Broadcasting and Listening** through the following scene:

- This is a slightly new simulation.
- The main difference, apart from the world, is the fact that:
  - Cam_bot does not publish its TF from `cam_bot_base_link`to `world`. This means that you cannot position the **Cam_bot** in the world.
  - The **turtle** `odom` frame is **NOT** connected to the `world` frame, which makes a **two-tree TF scene, one for each robot**.
  - The **Cam_bot** does not have this system for following frames; therefore, it is not easy to follow the turtle using only the basic control.

### 3.2  Broadcasting

**Objective**: Solve the issue in which the **Cam_bot** does not have a transform from `cam_bot_base_link`to `world`.

```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2
```

You should see that the graphical tools window pops up automatically. You should see RVIZ open in an unconfigured state a few seconds later. If it does not open automatically, click the "Open Graphical Tools" button in the bottom bar to manually open it.

**Tasks**:

- Add two **RobotModel** items to the display list: one for the **Cam_bot**, and the other one for the **turtle**. Topics have to be properly configured.
- Add a new **TF** display to see the TF frames in the 3D view with the grid.
- Select "world" as the Fixed Frame in Global Options.
- Also, add an **Image** display to show the view from the perspective of the robot's camera. Remember that you have to fill in your "Image Topic".
- You should now have an image window that is used later on.

Hint:

The commands `ros2 topic list` and `ros2 topic info -v` are useful to help you configure some Rviz settings.

**Task:**

Create a Python script named **cam_bot_odom_to_tf_pub.py** inside the package named **my_tf_ros2_course_pkg**.

This script extracts the odometry of the **Cam_bot** and publishes a static TF transform from the **camera_bot_base_link** to the frame **world**.

```
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_tf_ros2_course_pkg --dependencies tf2_ros geometry_msgs nav_msgs
```

Since this package is of build type `ament_cmake`, create a folder called `scripts` to place a Python script there.

```
mkdir my_tf_ros2_course_pkg/scripts
touch my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
chmod +x my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
```

Add the install commands to the **CMakeLists.txt** file so that you can execute the Python scripts.
You can use the example below to help you modify the pre-made script.

```cmake
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

install(PROGRAMS
  scripts/cam_bot_odom_to_tf_pub.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

`ament_cmake`是ROS 2中用于构建CMake项目的构建系统和CMake的扩展，它特别适用于C++项目。在ROS 2中，不同于ROS 1的`catkin_make`，`ament_cmake`是用于构建和安装软件包的推荐系统。

对于Python项目，`ament_cmake`不是必须的，因为Python通常不需要编译过程。然而，如果你的ROS 2包包含C++代码或需要一些特定的构建步骤（例如安装脚本、运行时配置等），那么`ament_cmake`就会被使用。

在ROS 2包中，即使是纯Python包，你也可能会看到`CMakeLists.txt`文件。这是因为ROS 2的工具链允许混合使用Python和C++，而`ament_cmake`提供了一个便捷的方式来处理这些复杂的构建情况。

当你使用`ament_cmake`时，会在`CMakeLists.txt`中配置相关的命令，如`ament_python_install_package()`或者`install(PROGRAMS ... DESTINATION ...)`, 来安装Python脚本和节点。这就是为什么即使是Python节点，也可能被放在`src/`目录而不是`scripts/`目录，因为`ament_cmake`会处理它们的安装过程。

**cam_bot_odom_to_tf_pub.py**

```python
#! /usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, DurabilityPolicy, QoSProfile
import tf2_ros
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry


class CamBotOdomToTF(Node):

    def __init__(self, robot_base_frame="camera_bot_base_link"):
        super().__init__('odom_to_tf_broadcaster_node')

        self._robot_base_frame = robot_base_frame
        
        # Create a new `TransformStamped` object.
        # A `TransformStamped` object is a ROS message that represents a transformation between two frames.
        self.transform_stamped = TransformStamped()
        # This line sets the `header.frame_id` attribute of the `TransformStamped` object.
        # The `header.frame_id` attribute specifies the frame in which the transformation is defined.
        # In this case, the transformation is defined in the `world` frame.
        self.transform_stamped.header.frame_id = "world"
        # This line sets the `child_frame_id` attribute of the `TransformStamped` object.
        # The `child_frame_id` attribute specifies the frame that is being transformed to.
        # In this case, the robot's base frame is being transformed to the `world` frame.
        self.transform_stamped.child_frame_id = self._robot_base_frame

        self.subscriber = self.create_subscription(
            Odometry,
            '/cam_bot_odom',
            self.odom_callback,
            QoSProfile(depth=1, durability=DurabilityPolicy.VOLATILE, reliability=ReliabilityPolicy.BEST_EFFORT))

        # This line creates a new `TransformBroadcaster` object.
        # A `TransformBroadcaster` object is a ROS node that publishes TF messages.
        self.br = tf2_ros.TransformBroadcaster(self)

        self.get_logger().info("odom_to_tf_broadcaster_node ready!")

    def odom_callback(self, msg):
        self.cam_bot_odom = msg
        # print the log info in the terminal
        self.get_logger().debug('Odom VALUE: "%s"' % str(self.cam_bot_odom))
        self.broadcast_new_tf()

    def broadcast_new_tf(self):
        """
        This function broadcasts a new TF message to the TF network.
        """

        # Get the current odometry data.
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # Set the timestamp of the TF message.
        # The timestamp of the TF message is set to the current time.
        self.transform_stamped.header.stamp = self.get_clock().now().to_msg()

        # Set the translation of the TF message.
        # The translation of the TF message is set to the current position of the robot.
        self.transform_stamped.transform.translation.x = position.x
        self.transform_stamped.transform.translation.y = position.y
        self.transform_stamped.transform.translation.z = position.z

        # Set the rotation of the TF message.
        # The rotation of the TF message is set to the current orientation of the robot.
        self.transform_stamped.transform.rotation.x = orientation.x
        self.transform_stamped.transform.rotation.y = orientation.y
        self.transform_stamped.transform.rotation.z = orientation.z
        self.transform_stamped.transform.rotation.w = orientation.w

        # Send (broadcast) the TF message.
        self.br.sendTransform(self.transform_stamped)


def main(args=None):

    rclpy.init()
    odom_to_tf_obj = CamBotOdomToTF()
    rclpy.spin(odom_to_tf_obj)

if __name__ == '__main__':
    main()
```



Compile and execute:

  **Execute in Terminal 1**

```
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 run my_tf_ros2_course_pkg cam_bot_odom_to_tf_pub.py
```

Now, open **RViz2** and check it:

  **Execute in Terminal 2**

```
source /home/simulations/ros2_sims_ws/install/setup.bash
```

Assuming you saved Rviz's configuration on the previous exercise:

```
rviz2 -d ~/ros2_ws/src/unit3_config.rviz
```

See if you can observe the robot move. To publish commands by pressing keys on the keyboard, start the teleop node again.

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/cam_bot_cmd_vel
```

- Check your **TF Tree** and see how it has changed:

```
ros2 run rqt_tf_tree rqt_tf_tree
```

Switch to the Graphical Tools window. At this point, you should see a graph that looks like the image below:

![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/worldtree_humble.png)



代码解释：

```python
#! /usr/bin/env python3

# 导入ROS 2 Python客户端库
import rclpy
from rclpy.node import Node  # Node类是所有ROS 2节点的基类
# 导入用于设置QoS（服务质量）参数的库
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
import tf2_ros  # TF2 ROS库，用于处理坐标系变换
# 导入消息类型
from geometry_msgs.msg import TransformStamped  # 用于存储单个坐标系变换的消息类型
from nav_msgs.msg import Odometry  # 用于接收机器人里程计信息的消息类型

# 定义CamBotOdomToTF类，继承自Node
class CamBotOdomToTF(Node):
    def __init__(self, robot_base_frame="camera_bot_base_link"):
        # 调用Node类的构造函数来初始化节点
        # 'odom_to_tf_broadcaster_node'是这个节点的名称
        super().__init__('odom_to_tf_broadcaster_node')

        # 机器人基座的名称，可以通过参数来修改，默认为"camera_bot_base_link"
        self._robot_base_frame = robot_base_frame
        
        # 创建一个TransformBroadcaster对象，用于广播TF变换
        self.br = tf2_ros.TransformBroadcaster(self)

        # 创建一个TransformStamped对象，该对象包含了变换信息
        self.transform_stamped = TransformStamped()
        # 设置变换的父坐标系为"world"
        self.transform_stamped.header.frame_id = "world"
        # 设置变换的子坐标系为机器人基座
        self.transform_stamped.child_frame_id = self._robot_base_frame

        # 创建一个订阅者，订阅"/cam_bot_odom"话题以接收Odometry消息
        # 设置QoS策略以适应实时数据流和网络条件
        self.subscriber = self.create_subscription(
            Odometry,
            '/cam_bot_odom',
            self.odom_callback,
            QoSProfile(depth=1, durability=DurabilityPolicy.VOLATILE, reliability=ReliabilityPolicy.BEST_EFFORT))

    # 定义处理Odometry消息的回调函数
    def odom_callback(self, msg):
        # 存储接收到的里程计数据
        self.cam_bot_odom = msg
        # 输出接收到的里程计值，用于调试
        self.get_logger().debug('Odom VALUE: "%s"' % str(self.cam_bot_odom))
        # 调用函数来广播新的TF变换
        self.broadcast_new_tf()

    # 定义一个方法来广播新的TF变换
    def broadcast_new_tf(self):
        # 从里程计数据中提取位置和方向
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # 设置变换的时间戳为当前时间
        self.transform_stamped.header.stamp = self.get_clock().now().to_msg()

        # 设置变换的平移部分为机器人的当前位置
        self.transform_stamped.transform.translation.x = position.x
        self.transform_stamped.transform.translation.y = position.y
        self.transform_stamped.transform.translation.z = position.z

        # 设置变换的旋转部分为机器人的当前方向
        self.transform_stamped.transform.rotation.x = orientation.x
        self.transform_stamped.transform.rotation.y = orientation.y
        self.transform_stamped.transform.rotation.z = orientation.z
        self.transform_stamped.transform.rotation.w = orientation.w

        # 使用TransformBroadcaster对象来广播变换
        self.br.sendTransform(self.transform_stamped)

# 定义main函数，用于初始化节点并进入循环等待回调函数触发
def main(args=None):
    rclpy.init(args=args)  # 初始化rclpy
    odom_to_tf_obj = CamBotOdomToTF()  # 创建CamBotOdomToTF类的实例
    rclpy.spin(odom_to_tf_obj)  # 保持节点运行，直到被终止

if __name__ == '__main__':
    main()

```











