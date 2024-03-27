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



### QoS

在ROS 2（机器人操作系统 2）中，QoS（Quality of Service，服务质量）策略是一组配置，用于定义ROS 2节点之间通信的行为。这些配置影响数据的可靠性、存储时长以及如何处理网络波动或延迟等问题。在给定的代码片段中，QoS策略通过`QoSProfile`对象来配置，具体包括深度（`depth`）、持久性（`durability`）和可靠性（`reliability`）三个参数：

1. **深度（`depth`）**：这是一个整数，指定了消息队列的大小。在这个例子中，深度设置为1，意味着订阅者节点的消息队列中最多只会保留一个消息。如果新的消息到达而旧消息还未被处理，旧消息将被丢弃。
2. **持久性（`DurabilityPolicy.VOLATILE`）**：这个设置决定了系统是否应该保存那些在订阅者连接到发布者之前就已经发布的消息。`VOLATILE`表示不保存这些消息，即订阅者只能收到在其订阅之后发布的消息。
3. **可靠性（`ReliabilityPolicy.BEST_EFFORT`）**：这个设置决定了通信的可靠性等级。`BEST_EFFORT`表示系统不会尝试重传丢失的消息，这通常用于对实时性要求高但可以容忍丢包的应用场景。

总结而言，这段代码中的QoS策略配置了一个对实时性要求较高但可以接受消息丢失的通信行为。这种配置适用于如视频流或高频率传感器数据等场景，其中最新的数据比保持所有数据的完整性更重要。



## 2  TF Basics

In this unit, you will learn the following:

- The tools that ROS2 has to introspect and interact with the TF2 library
- Visualizing TF frames through TF trees
- Visualizing TF frames through RVIZ2

### 2.1  场景介绍

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

### 3.2  Broadcasting (广播)

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




TF（Transform）广播器在ROS中是用来发布坐标系之间相对位置和方向的关系。在ROS的TF变换系统中，广播器（Broadcaster）负责发送变换信息（transforms），而监听器（Listener）则负责接收这些信息。这个机制允许系统中的不同部分知道如何相对于彼此定位和导向。

#### 广播器做什么？

TF广播器负责：

- **创建和发送变换信息**：它将一个坐标系相对于另一个坐标系的位置和方向的信息发送出去。这些信息包括平移（三维空间中的移动）和旋转（四元数表示的方向）。
- **定期更新变换信息**：在动态环境中，物体或机器人的位置可能会不断变化，TF广播器可以定期更新这些变换信息。

#### 它广播了什么？

TF广播器广播`TransformStamped`消息，该消息包含：

- **时间戳**：变换信息的时间戳，表示这个变换是什么时候有效的。
- **父坐标系ID** (`header.frame_id`)：这个变换是相对于哪个坐标系定义的。
- **子坐标系ID** (`child_frame_id`)：这个变换定义了子坐标系相对于父坐标系的位置和方向。
- **平移**：三维向量，表示子坐标系原点相对于父坐标系原点的位置。
- **旋转**：四元数，表示子坐标系相对于父坐标系的方向。

#### 谁会接收广播？

TF变换信息的接收者是TF监听器（Listener）。监听器可以是ROS系统中的任何节点，它们需要知道坐标系之间的相对位置和方向。例如，一个路径规划节点可能需要知道机器人当前位置（坐标系）相对于世界坐标系或地图坐标系的变换信息。

#### 怎么接收广播？

接收TF广播的节点会使用`tf2_ros`包中的`TransformListener`对象来订阅TF消息。`TransformListener`会自动订阅`/tf`和`/tf_static`话题，并处理接收到的变换信息。节点可以使用`TransformListener`查询特定时间点的两个坐标系之间的变换信息，例如，查询机器人坐标系相对于世界坐标系的位置和方向。

```python
# TF广播器初始化和使用
self.br = tf2_ros.TransformBroadcaster(self)
...
# 构造TransformStamped消息并发送
t = TransformStamped()
t.header.stamp = self.get_clock().now().to_msg()
t.header.frame_id = "world"
t.child_frame_id = self._robot_base_frame
t.transform.translation = ...
t.transform.rotation = ...
self.br.sendTransform(t)

```

在上面的示例中，广播器`self.br`被用来发送一个坐标系相对于另一个坐标系的变换信息。这个变换信息通过`TransformStamped`消息表示，并通过`sendTransform`方法发布。系统中的其他节点可以通过监听器来接收这些信息，并据此计算物体在不同坐标系中的位置。



#### 如何知道对应的是哪个变换？

你可以通过观察`TransformStamped`消息中的`header.frame_id`和`child_frame_id`来识别对应的变换。这些字段分别指定了变换的参考坐标系（父坐标系）和被变换的坐标系（子坐标系）。例如，如果一个变换消息的`header.frame_id`是`"world"`，而`child_frame_id`是`"robot_base_link"`，那么这个变换描述的就是`"robot_base_link"`坐标系相对于`"world"`坐标系的位置和方向。



#### 在系统中跟踪变换

- **监听和查询变换**：在ROS系统中，其他节点可以使用`tf2_ros.TransformListener`来监听变换消息，并根据需要查询特定时间点的特定坐标系之间的变换。这使得节点能够根据动态变化的位置和方向信息进行操作，如导航、避障等。
- **可视化工具**：使用如RViz这样的可视化工具，可以直观地查看和理解坐标系之间的变换关系。RViz能够显示坐标系的结构和动态变换，帮助开发者和用户跟踪系统中的空间关系。



#### 1 创建my_tf_ros2_course_pkg功能包

**Task:**

Create a Python script named **cam_bot_odom_to_tf_pub.py** inside the package named **my_tf_ros2_course_pkg**.

This script extracts the odometry of the **Cam_bot** and publishes a static TF transform from the **camera_bot_base_link** to the frame **world**.

**该脚本提取了cam_bot的里程计，并发布了从camera_bot_base_link到框架世界的静态TF变换。**

```
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_tf_ros2_course_pkg --dependencies tf2_ros geometry_msgs nav_msgs
```

#### 2 创建 cam_bot_odom_to_tf_pub.py

Since this package is of build type `ament_cmake`, create a folder called `scripts` to place a Python script there.

```
mkdir my_tf_ros2_course_pkg/scripts
touch my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
chmod +x my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
```

#### 3 修改CMakeLists

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

#### 4 编译

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



#### 代码解释：

通过定于cam_bot的里程计信息，将里程计信息做TF变换，再广播。

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
        # 发送广播
        self.br.sendTransform(self.transform_stamped)

# 定义main函数，用于初始化节点并进入循环等待回调函数触发
def main(args=None):
    rclpy.init(args=args)  # 初始化rclpy
    odom_to_tf_obj = CamBotOdomToTF()  # 创建CamBotOdomToTF类的实例
    rclpy.spin(odom_to_tf_obj)  # 保持节点运行，直到被终止

if __name__ == '__main__':
    main()

```

### 3.3  tf2_monitor

`tf2_monitor`是ROS（Robot Operating System）中一个非常有用的工具，专门用于监测和分析TF（Transform）数据的延迟和连通性。这个工具对于确保系统中的空间数据一致性至关重要，特别是在处理传感器数据和执行机器人导航等操作时。

#### 延迟检查

- **直接连接的坐标系**：如果两个坐标系（frames）是直接连接的，`tf2_monitor`可以用来测量从一个坐标系到另一个坐标系变换信息的发布延迟。
- **间接连接的坐标系**：如果两个坐标系不是直接连接的，那么延迟时间将包括从原始坐标系到目标坐标系之间的所有连接坐标系的累积延迟。

#### 为什么需要`tf2_monitor`?

在ROS系统中，时间戳非常关键。例如，传感器数据通常会被分配一个时间戳，表明数据是何时被采集的。这些数据随后可能会被用于不同的目的，如导航、定位或避障。为了正确地处理这些传感器数据，系统需要确保数据所引用的坐标系的TF信息是最新的，且与传感器数据的时间戳一致。如果TF信息过时，或者与传感器数据的时间戳不匹配，那么这些数据可能会被丢弃，因为它们被认为是不可靠的。

#### 使用`tf2_monitor`提高系统性能

通过使用`tf2_monitor`，开发者可以：

- **监测TF延迟**：了解系统中不同坐标系之间TF信息的延迟，帮助识别可能的性能瓶颈或配置错误。
- **确保数据一致性**：确保处理传感器数据时，TF信息是最新的且与传感器数据时间戳一致，减少数据丢失的风险。
- **系统调试和优化**：通过监测TF的连通性和延迟，可以帮助开发者调试和优化系统的性能，特别是在复杂的多传感器或多机器人系统中。

#### 示例命令

```
tf2_monitor
```

这个命令将启动`tf2_monitor`工具，开始分析和报告系统中的TF延迟和连通性情况。你可以指定特定的坐标系来关注分析，或者让它分析整个TF树。



This tool is used to check the delay between transforms. This means how much time passes between the publication of one frame and another connected frame.

- If they are directly connected, it is the time between those frames.
- However, suppose the frames are NOT connected directly. In that case, the time will be accumulated from the publication of the original frame to the publication of the destination frame.

And why do you need this? One common and critical system is the timestamps. The sensor data, referred to as a frame, must be consistent with the TF time publication. Otherwise, the sensor data will be discarded.

Have a look at your system to understand this better.

**Execute in Terminal 3**

Now see the times from frame `camera_bot_base_link` to `rgb_camera_link_frame`:

```
ros2 run tf2_ros tf2_monitor camera_bot_base_link rgb_camera_link_frame
```

Output：

```bash
RESULTS: for camera_bot_base_link to rgb_camera_link_frame
Chain is: rgb_camera_link_frame -> chassis -> camera_bot_base_link
Net delay     avg = 3.23952e+08: max = 1.70257e+09

Frames:
Frame: camera_bot_base_link, published by , Average Delay: 0.000354682, Max Delay: 0.00420332
Frame: chassis, published by , Average Delay: 1.70257e+09, Max Delay: 1.70257e+09
Frame: rgb_camera_link_frame, published by , Average Delay: 1.70257e+09, Max Delay: 1.70257e+09

All Broadcasters:
Node:  155.869 Hz, Average Delay: 1.28033e+09 Max Delay: 1.70257e+09
```

Now see the times from frame `world` to `camera_bot_base_link`:

```
ros2 run tf2_ros tf2_monitor world camera_bot_base_link
```

Output：

```
RESULTS: for world to camera_bot_base_link
Chain is: world -> camera_bot_base_link
Net delay     avg = 0.00443906: max = 0.0457809

Frames:
Frame: camera_bot_base_link, published by , Average Delay: 0.000344517, Max Delay: 0.00268316

All Broadcasters:
Node:  157.413 Hz, Average Delay: 1.28033e+09 Max Delay: 1.70257e+09
```

You can see that:

- Average delay for `rgb_camera_link_frame` -> `chassis` -> `camera_bot_base_link` == 3.23952e+08 seconds
- Average delay for `world` -> `camera_bot_base_link` == 0.00443906 seconds

Why is the delay for the transform from `rgb_camera_link_frame` to `chassis` to `camera_bot_base_link` so high?

- This is because these transforms are static or behave as static transforms. This means that the TF delay is, in reality, zero. The fact that the delay is so high reflects that, even when it is counterintuitive.
- 都是静态变换，延迟应该是0啊，这明显是不合理的。
- So what is the issue then?

The issue is that the average delay of the transform **world -> camera_bot_base_link** is 0.00443906 seconds ( 4.4 ms). And **4 ms** is too much for the image module in RVIZ to consider these transforms acceptable.

时间不一致会导致延迟，主要是因为在处理传感器数据和执行基于这些数据的操作时，系统需要确保数据的时间戳和当前的上下文或其他相关数据的时间戳是匹配的。

#### 为什么时间不一致会导致延迟？

1. **数据处理延迟**：在复杂的机器人系统中，从传感器采集数据到数据被处理和使用，中间可能会有处理延迟。如果TF变换的时间戳不反映原始传感器数据的采集时间，那么基于这些变换进行的计算可能不再准确，因为它们不代表当前的物理状态。
2. **系统同步问题**：在分布式系统中，不同组件可能在不同的物理设备上运行，这些设备的时钟可能没有完全同步。如果没有适当的时间同步机制，就可能导致数据时间戳之间的不一致。
3. **数据依赖性**：许多机器人系统中的决策和操作都依赖于同时满足多个数据源的信息。如果这些数据源的时间戳不一致，系统可能需要等待或插值以获得一致的视图，从而增加了延迟。

#### 为什么会出现时间不一致的情况？

1. **传感器和处理系统的延迟**：传感器数据在被处理和使用之前可能需要经过多个步骤，每个步骤都可能引入延迟。此外，数据在网络上传输时也可能会有延迟。
2. **时钟不同步**：在分布式系统或多个硬件设备中，时钟不同步是常见问题。不同设备的内部时钟可能以微小但累积的方式偏离，导致时间戳的不一致。
3. **缓冲和队列**：为了处理高数据率或突发数据，系统可能使用缓冲区或队列暂存数据。这种做法虽然可以平滑数据流，但也可能导致处理过程中的延迟。
4. **软件设计**：软件设计和架构决策也会影响时间一致性。例如，如果系统没有恰当地管理和同步时间戳，就可能导致数据时间戳的不一致。

So what can you do? Well, there was a slight error in the original code that generated all this mess:

- **使用传感器数据的时间戳**：解决方案是在生成TF变换时，提取并使用传感器数据（如里程计）的时间戳。这样可以确保TF数据与传感器数据时间一致，从而消除两个坐标系之间的延迟。
- **代码更正**：在原始代码中进行更正，确保使用正确的时间戳，可以解决因时间不一致导致的问题。

- Extract the time of the sensor data and use it in the TF. In this case, the odometry time.
- The TF data will be consistent, and there will not be a delay between the two frames. Now make these corrections to create a new script:

```bash
cd ~/ros2_ws/src
touch my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
chmod +x my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
```

Update the `CMakeLists.txt` script to include this new Python script file:

```
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
  scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

Use the code editor window to paste the code below into the script:

**cam_bot_odom_to_tf_pub_late_tf_fixed.py**

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
        time_header = self.cam_bot_odom.header
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # Set the timestamp of the TF message.
        # The timestamp of the TF message is set to the odom message time.
        self.transform_stamped.header.stamp = time_header.stamp

        # Set the translation of the TF message.
        # The translation of the TF message should be set to the current position of the robot.
        self.transform_stamped.transform.translation.x = position.x
        self.transform_stamped.transform.translation.y = position.y
        self.transform_stamped.transform.translation.z = position.z

        # Set the rotation of the TF message.
        # The rotation of the TF message should be set to the current orientation of the robot.
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

Note that the only thing that has changed is that you now use the time from the **odometry data messages**, instead of the current clock time.

```python
...
        # Get the current odometry data.
   		# 从里程计消息中获取时间戳
        time_header = self.cam_bot_odom.header
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # Set the timestamp of the TF message.
        # The timestamp of the TF message is set to the odom message time.
        # 将TF消息的时间戳设置为里程计消息的时间戳
        self.transform_stamped.header.stamp = time_header.stamp
...
```

编译

```
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 run my_tf_ros2_course_pkg cam_bot_odom_to_tf_pub_late_tf_fixed.py
```

Source the workspace where the meshes are located and execute the `RVIZ2` configured.

```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2 -d ~/ros2_ws/src/unit3_config.rviz
```

Check the average time for the transform:

```
ros2 run tf2_ros tf2_monitor world camera_bot_base_link
```

Output

```
RESULTS: for world to camera_bot_base_link
Chain is: world -> camera_bot_base_link
Net delay     avg = 1.6717e+09: max = 1.70257e+09

Frames:
Frame: camera_bot_base_link, published by , Average Delay: 1.70257e+09, Max Delay: 1.70257e+09

All Broadcasters:
Node:  157.79 Hz, Average Delay: 1.49486e+09 Max Delay: 1.70257e+09
```

Now you have the following:

- Average transform delay for the chain `world` -> `camera_bot_base_link` == 1.6717e+09 seconds.
- This indicates that it behaves like a static transform, meaning the delay is null.

Great! However, now you have to solve the following issues:

- The transform frames for the turtle are not represented correctly in RVIZ2.
- This is because neither robot frame is **CONNECTED**.

Fix that using a **static transform**.

### 3.4  Static Broadcaster































