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

注意，因为这是一个静态的转换，它假设这个坐标系关系不会随时间变化。对于动态变化的坐标系，你通常需要写一个ROS节点来定期更新并广播这些变换。在动态场景中，这通常通过编写自己的发布者节点实现.

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

You can publish **static transforms** in three different ways:

- Through the command line
- Through a Python/C++ program
- Through Launch files

Static transforms are used for TFs that **DO NOT change over time**. The reason is that static transforms are published in the topic **tf_static** and only published when they change, significantly lowering the impact on the system's performance and resource use.

#### 3.4.1 Static Broadcaster using the Command Line

These are the commands to do so:

##### Option 1: XYZ Roll-Pitch-Yaw (radians)

If you want to define the orientation using Euler angles, the `ros2 run` command should comply with the following structure:

```
ros2 run tf2_ros static_transform_publisher --x x --y y --z z --yaw yaw --pitch pitch --roll roll --frame-id frame_id --child-frame-id child_frame_id
```

##### Option 2: XYZW Quaternion

The general scheme for defining the orientation in Quaternions is the following:

```
ros2 run tf2_ros static_transform_publisher --x x --y y --z z --qx qx --qy qy --qz qz --qw qw --frame-id frame_id --child-frame-id child_frame_id
```

However, you can also use these commands inside a launch file. That is what you will use to publish a Static Transform from the `world` (root frame of the `Cam_bot`) -> `odom` (root frame of the `TurtleBot`). Do it!

#### 3.4.2 Static Broadcaster through a launch file

```
cd ~/ros2_ws/src/my_tf_ros2_course_pkg
mkdir launch
touch launch/publish_static_transform_odom_to_world.launch.py
chmod +x launch/publish_static_transform_odom_to_world.launch.py
```

 **CMakeLists.txt**

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

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/cam_bot_odom_to_tf_pub.py
  scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

 **publish_static_transform_odom_to_world.launch.py**

```python
#! /usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    static_tf_pub = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_turtle_odom',
        output='screen',
        emulate_tty=True,
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom']  # 'odom'到'world'
    )

    return LaunchDescription(
        [
            static_tf_pub # static_tf_pub 节点名
        ]
    )
```

The above launch file defines a Node called `static_tf_pub`. This Node starts the static_transform_publisher executable from the `tf2_ros` package. This node is configured to publish a static transform between the `world` and `odom` frames using the arguments. The arguments to the node are the **translation** and **rotation** (rpy) of the transform.

Reminder:

- We are publishing the TF from `camera_bot_base_link` to `odom`, as we did in the previous section.

```
cd ~/ros2_ws && colcon build && source install/setup.bash
```

```
ros2 run my_tf_ros2_course_pkg cam_bot_odom_to_tf_pub_late_tf_fixed.py
```

```
source /home/simulations/ros2_sims_ws/install/setup.bash
```

```
rviz2 -d ~/ros2_ws/src/unit3_config.rviz
```

  **Execute in Terminal 3**

Reminder:

- We are publishing the **static** TF from `odom` to `world`.
- This will connect the `world` frame with the `odom` frame, and then the `odom` frame will be connected to the `camera_bot_base_link`, thus connecting all parts of the robot.

```
source ~/ros2_ws/install/setup.bash
ros2 launch my_tf_ros2_course_pkg publish_static_transform_odom_to_world.launch.py
```

  **Execute in Terminal 4**

Check the TF tree:

```
ros2 run rqt_tf_tree rqt_tf_tree
```



![img](https://s3.eu-west-1.amazonaws.com/notebooks.ws/tf_ROS2/img/working_completetreetf_ros2_u2.png)

Now, all the TF frames are **connected in a single TF TREE**. This allows RVIZ to render everything in space. And now, you should be able to move both robots and see that their position in space in **RVIZ2** is correct and the same as in the real world/simulation:

Move the Cam_bot:

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/cam_bot_cmd_vel
```

#### 3.4.3 Static Broadcaster via Python script

This method is similar to the standard **transform broadcaster** that you did before.

**Task:**

- Write a script to create a new frame attached to the turtle that is closer to the turtle so you get a good first plane.

```
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/scripts
touch static_broadcaster_front_turtle_frame.py
chmod +x static_broadcaster_front_turtle_frame.py
```

Update the CMake script again:

  **CMakeLists.txt**

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
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

The Python script below can be used to publish anything statically wherever you want, essentially the same as the commands you used previously:

```python
#! /usr/bin/env python3
import sys
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
import tf_transformations


class StaticFramePublisher(Node):

    def __init__(self):
        super().__init__('static_broadcaster_front_turtle_frame_node')

        # This line creates a `StaticTransformBroadcaster` object.
        # The `StaticTransformBroadcaster` object is used to publish static transforms between frames.
        self._tf_publisher = StaticTransformBroadcaster(self)

        # Publish static transforms once at startup
        self.make_transforms()

        self.get_logger().info("static_broadcaster_front_turtle_frame ready!")

    def make_transforms(self):
        static_transformStamped = TransformStamped()
        static_transformStamped.header.stamp = self.get_clock().now().to_msg()
        static_transformStamped.header.frame_id = sys.argv[1] # 在命令行指定变换矩阵
        static_transformStamped.child_frame_id = sys.argv[2]
        static_transformStamped.transform.translation.x = float(sys.argv[3])
        static_transformStamped.transform.translation.y = float(sys.argv[4])
        static_transformStamped.transform.translation.z = float(sys.argv[5])
        quat = tf_transformations.quaternion_from_euler(
            float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8]))
        static_transformStamped.transform.rotation.x = quat[0]
        static_transformStamped.transform.rotation.y = quat[1]
        static_transformStamped.transform.rotation.z = quat[2]
        static_transformStamped.transform.rotation.w = quat[3]

        self._tf_publisher.sendTransform(static_transformStamped)


def main():

    rclpy.init()
    assert len(sys.argv) > 8, "Please add all the arguments: ros2 run tf_ros2_solutions parent_frame child_frame x y z roll pitch yaw"
    node_obj = StaticFramePublisher()
    try:
        rclpy.spin(node_obj)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()


if __name__ == "__main__":
    main()
```

#### 代码解释

这段代码定义了一个ROS 2节点，用于在ROS 2的tf（transform）树中发布一个静态变换。这可以帮助在不同坐标系之间进行空间定位和导航。下面是对代码中每一部分的详细解释和注释：

Python**脚本的开头**

```python
#! /usr/bin/env python3
import sys
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
import tf_transformations
```

- `#! /usr/bin/env python3`: 这是一个shebang行，它告诉操作系统使用env来找到python3解释器。
- `import sys`: 导入sys模块，允许你访问由命令行传入的参数。
- `from geometry_msgs.msg import TransformStamped`: 导入ROS 2消息类型`TransformStamped`，用于描述两个坐标系之间的变换。
- `import rclpy`: 导入ROS 2 Python客户端库。
- `from rclpy.node import Node`: 导入Node类，所有ROS 2节点都基于此类。
- `from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster`: 导入用于发布静态变换的类。
- `import tf_transformations`: 导入tf_transformations库，用于处理变换中的旋转和转换计算。

**类定义**

```python
class StaticFramePublisher(Node):
    def __init__(self):
        super().__init__('static_broadcaster_front_turtle_frame_node')
        self._tf_publisher = StaticTransformBroadcaster(self)
        self.make_transforms()
        self.get_logger().info("static_broadcaster_front_turtle_frame ready!")
```

- `class StaticFramePublisher(Node)`: 定义一个名为StaticFramePublisher的类，它继承自Node。
- `super().__init__('static_broadcaster_front_turtle_frame_node')`: 调用父类构造器并命名节点为`static_broadcaster_front_turtle_frame_node`。
- `self._tf_publisher = StaticTransformBroadcaster(self)`: 创建一个静态变换广播器实例，用于发布变换。
- `self.make_transforms()`: 调用内部方法来创建并发送静态变换。
- `self.get_logger().info(...)`: 使用节点的日志记录器打印信息，表明节点已准备就绪。

**定义静态变换**

```python
def make_transforms(self):
        static_transformStamped = TransformStamped()
        static_transformStamped.header.stamp = self.get_clock().now().to_msg()
        static_transformStamped.header.frame_id = sys.argv[1]
        static_transformStamped.child_frame_id = sys.argv[2]
        static_transformStamped.transform.translation.x = float(sys.argv[3])
        static_transformStamped.transform.translation.y = float(sys.argv[4])
        static_transformStamped.transform.translation.z = float(sys.argv[5])
        quat = tf_transformations.quaternion_from_euler(
            float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8]))
        static_transformStamped.transform.rotation.x = quat[0]
        static_transformStamped.transform.rotation.y = quat[1]
        static_transformStamped.transform.rotation.z = quat[2]
        static_transformStamped.transform.rotation.w = quat[3]
        self._tf_publisher.sendTransform(static_transformStamped)
```

- 初始化`TransformStamped`对象来存储变换数据。
- 设置时间戳、父坐标系ID和子坐标系ID。
- 通过命令行参数读取和设置位置(x, y, z)和旋转(roll, pitch, yaw)，然后将欧拉角转换为四元数。
- 调用`sendTransform`发布变换。

**主函数**

```python
def main():
    rclpy.init()
    assert len(sys.argv) > 8, "Please add all the arguments: ros2 run tf_ros2_solutions parent_frame child_frame x y z roll pitch yaw"
    node_obj = StaticFramePublisher()
    try:
        rclpy.spin(node_obj)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()
```

- 初始化ROS 2。
- 检查确保提供了所有必要的命令行参数。
- 创建节点对象并使节点保持活动，直到被中断。

The only real difference is that you create a `StaticTransformBroadcaster` object:

唯一真正的区别是你创建了一个`StaticTransformBroadcaster`对象：

```
StaticTransformBroadcaster(self)
```

Instead of a regular `TransformBroadcaster` object as you did before:


这段文字解释了在ROS 2中使用`StaticTransformBroadcaster`与`TransformBroadcaster`之间的主要区别，以及为什么在某些情况下使用前者更有优势。

**翻译**

唯一真正的区别是你创建了一个`StaticTransformBroadcaster`对象：

```
python
Copy code
StaticTransformBroadcaster(self)
```

而不是像之前那样创建一个常规的`TransformBroadcaster`对象：

```
TransformBroadcaster(self)
```

This makes the frame permanent once published. Therefore, you do not need to publish it regularly to avoid considering it stale. That is the advantage of using a **static transform broadcaster** object.

That is why there is **no broadcasting loop**, only the spin.

这使得一旦发布，坐标系变换就变成了永久的。因此，你不需要定期发布它来避免被认为是过时的。这就是使用**静态变换广播器**对象的优势。这就是为什么没有广播循环，只需要进行spin的原因。



在ROS中，变换（transforms）可以通过两种类型的广播器发布：`TransformBroadcaster`和`StaticTransformBroadcaster`。

1. **`TransformBroadcaster`**：用于发布可能会随时间变化的变换，比如由于机器人的移动。使用这种广播器时，变换需要被连续发布，以确保变换信息是最新的，因为如果一段时间内没有更新，变换数据可能被认为是过时的。
2. **`StaticTransformBroadcaster`**：用于发布静态变换，即不随时间改变的变换。例如，机器人上的传感器相对于机器人基座的固定位置。使用静态变换广播器，变换只需发布一次，之后它会被认为是永久有效的，无需重复发布。

使用`StaticTransformBroadcaster`的优势在于，对于那些不会改变的变换，系统处理变得更为高效，因为不需要在系统中维护一个定期更新的循环。这简化了代码并减少了计算负担。

**实际应用**

在ROS 2的实践中，当你确定一个变换在系统运行期间不会改变时，应该使用`StaticTransformBroadcaster`。这通常包括固定的硬件组件关系，如摄像头安装在机器人上的位置。对于动态变换，如机器人各部分之间的关系（可能由于关节运动而变化），应该使用`TransformBroadcaster`。这样的区分确保了系统资源的有效利用和变换数据的准确性。







Now execute everything and see how your new frame appears:



```
cd ~/ros2_ws && colcon build && source install/setup.bash
rviz2 -d ~/ros2_ws/src/unit3_config.rviz
```

```
source ~/ros2_ws/install/setup.bash
ros2 launch my_tf_ros2_course_pkg publish_static_transform_odom_to_world.launch.py
```

Then consider the following parameters when launching the new `static_broadcaster_front_turtle_frame.py` script:

- parent frame = turtle_chassis
- child frame = my_front_turtle_frame (you can put any name you want)
- X = 0.4 (it is 0.4 meters in the X-axis of the parent frame)
- Y = 0.0
- Z = 0.4 (it is 0.4 meters in the Z-axis of the parent frame)
- Roll = 0.0
- Pitch = 0.7 (you want it to point at 45 degrees/0.7 radians pitch down)
- Yaw = 3.1416 (you want it to point at 180 degrees/3.1416 radians pitch down)

通过命令行 发送变换矩阵的参数arg

```
source ~/ros2_ws/install/setup.bash
ros2 run my_tf_ros2_course_pkg static_broadcaster_front_turtle_frame.py turtle_chassis my_front_turtle_frame 0.4 0 0.4 0 0.7 3.1416
```

### 3.5  TF Listener

在ROS 2（机器人操作系统 2）中，TF（Transform）监听器（Listeners）是用来接收和处理TF数据的工具。TF数据包含了各种坐标帧之间的变换关系，这对于机器人进行空间定位和导航至关重要。当一个新的节点启动一个TF监听器时，它会监听`tf`和`tf_static`两个话题（Topics）。

**工作原理**：

1. **监听`tf`和`tf_static`话题**：这两个话题传输的是坐标帧之间的变换数据。`tf`用于传输频繁更新的变换信息，而`tf_static`用于传输那些很少或不会改变的变换信息。
2. **建立缓冲区（Buffer）**：TF监听器会构建一个帧关系的缓冲区。这个缓冲区存储了各个坐标帧之间的变换关系，这些关系是自监听器启动以来发布的。
3. **解决TF查询**：使用这个缓冲区，监听器可以解决关于坐标帧之间变换的查询，比如查询一个坐标帧相对于另一个坐标帧在某一时刻的位置和方向。

**重点总结**：

- **TF监听器的局限性**：每个节点的TF监听器只能知道自己启动后发布的变换信息，这意味着如果节点启动时错过了某些变换信息，它就无法获得这些信息。
- **数据的组织和查询**：TF监听器通过管理和查询TF数据，使得应用程序可以根据需要执行空间变换，例如在机器人抓取操作或导航中定位特定的物体。
- **实时性和精确性**：通过监听`tf`和`tf_static`，TF监听器能够适应那些需要快速响应和高精度定位的应用场景。

简而言之，TF监听器是ROS 2中用于处理和利用坐标帧变换信息的关键组件，它为机器人的空间感知和交互提供了必要的数据支持。

First, create the files:

```
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/scripts
touch move_generic_model.py
chmod +x move_generic_model.py
```

  **CMakeLists.txt**

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
```

**move_generic_model.py**

```python
#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

import tf_transformations

from std_msgs.msg import String

from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
# from gazebo_msgs.msg import ModelState

from geometry_msgs.msg import Pose
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3


class Coordinates:
    def __init__(self, x, y, z, roll, pitch, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

        
class CamBotMove(Node):

    def __init__(self, timer_period=0.05, model_name="cam_bot", init_dest_frame="carrot", trans_speed=1.0, rot_speed=0.1):
        super().__init__('force_move_cam_bot')
        
        self._model_name = model_name

        self.set_destination_frame(new_dest_frame=init_dest_frame)
        self.set_translation_speed(speed=trans_speed)
        self.set_rotation_speed(speed=rot_speed)

        # For the TF listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer_period = timer_period
        self.timer_rate = 1.0 / self.timer_period
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.subscriber= self.create_subscription(
            String,
            '/destination_frame',
            self.move_callback,
            QoSProfile(depth=1))

        self.set_entity_client = self.create_client(SetEntityState, "/cam_bot/set_entity_state")
        while not self.set_entity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.get_logger().info('service READY...')
        
        # create a request
        self.req = SetEntityState.Request()

        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        self.move_step_speed()
        self.get_logger().info("Moved the Robot to frame ="+str(self.objective_frame))

    def set_translation_speed(self, speed):
        self.trans_speed = speed
    
    def set_rotation_speed(self, speed):
        self.rot_speed = speed

    def set_destination_frame(self, new_dest_frame):
        self.objective_frame = new_dest_frame

    def move_callback(self, msg):
        self.set_destination_frame(new_dest_frame=msg.data)
        
    def move_step_speed(self):
        coordinates_to_move_to = self.calculate_coord()
        if coordinates_to_move_to is not None:
            self.move_model(coordinates_to_move_to)
        else:
            self.get_logger().warning("No Coordinates available yet...")

    def get_model_pose_from_tf(self, origin_frame="world", dest_frame="camera_bot_base_link"):
        """
        Extract the pose from the TF
        """
        # Look up for the transformation between dest_frame and turtle2 frames
        # and send velocity commands for turtle2 to reach dest_frame
        try:
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(
                origin_frame,
                dest_frame,
                now)
        except TransformException as ex:
            self.get_logger().error(
                f'Could not transform {origin_frame} to {dest_frame}: {ex}')
            return None


        translation_pose = trans.transform.translation
        rotation_pose = trans.transform.rotation

        self.get_logger().info("type translation_pose="+str(type(translation_pose)))
        self.get_logger().info("type rotation_pose="+str(type(rotation_pose)))


        pose = Pose()
        pose.position.x = translation_pose.x
        pose.position.y = translation_pose.y
        pose.position.z = translation_pose.z
        pose.orientation.x = rotation_pose.x
        pose.orientation.y = rotation_pose.y
        pose.orientation.z = rotation_pose.z
        pose.orientation.w = rotation_pose.w

        return pose



    def calculate_coord(self):
        """
        Gets the current position of the model and adds the increment based on the Publish rate
        """
        pose_dest = self.get_model_pose_from_tf(origin_frame="world", dest_frame=self.objective_frame)
        self.get_logger().error("POSE DEST="+str(pose_dest))
        if pose_dest is not None:

            explicit_quat = [pose_dest.orientation.x, pose_dest.orientation.y,
                             pose_dest.orientation.z, pose_dest.orientation.w]
            pose_now_euler = tf_transformations.euler_from_quaternion(explicit_quat)

            roll = pose_now_euler[0]
            pitch = pose_now_euler[1]
            yaw = pose_now_euler[2]

            coordinates_to_move_to = Coordinates(x=pose_dest.position.x,
                                                y=pose_dest.position.y,
                                                z=pose_dest.position.z,
                                                roll=roll,
                                                pitch=pitch,
                                                yaw=yaw)
        else:
            coordinates_to_move_to = None

        return coordinates_to_move_to

    def move_model(self, coordinates_to_move_to):

    
        pose = Pose()

        pose.position.x = coordinates_to_move_to.x
        pose.position.y = coordinates_to_move_to.y
        pose.position.z = coordinates_to_move_to.z


        quaternion = tf_transformations.quaternion_from_euler(coordinates_to_move_to.roll,
                                                              coordinates_to_move_to.pitch,
                                                              coordinates_to_move_to.yaw)
        pose.orientation.x = quaternion[0]
        pose.orientation.y = quaternion[1]
        pose.orientation.z = quaternion[2]
        pose.orientation.w = quaternion[3]

        # You set twist to Null to remove any prior movements
        twist = Twist()
        linear = Vector3()
        angular = Vector3()

        linear.x = 0.0
        linear.y = 0.0
        linear.z = 0.0

        angular.x = 0.0
        angular.y = 0.0
        angular.z = 0.0

        twist.linear = linear
        twist.angular = angular

        state = EntityState()
        state.name = self._model_name
        state.pose = pose
        state.twist = twist
        state.reference_frame = "world"

        self.req.state = state

        self.get_logger().error("STATE to SEND="+str(self.req.state))

        # send the request
        try:     
            self.future = self.set_entity_client.call_async(self.req)
        except Exception as e:
            self.get_logger().error('Error on calling service: %s', str(e))
        
            

def main(args=None):
    rclpy.init()

    move_obj = CamBotMove()

    print("Start Moving")
    rclpy.spin(move_obj)


if __name__ == '__main__':
    main()
```

This script is quite complex, but let's go over the elements that define a **TF Listener**:

定义了一个TransformListener对象，注意，该节点需要一个buffer

```python
# For the TF listener
self.tf_buffer = Buffer()
self.tf_listener = TransformListener(self.tf_buffer, self)
```

从tf中获取位姿变换矩阵

```python
def get_model_pose_from_tf(self, origin_frame="world", dest_frame="camera_bot_base_link"):
    """
    Extract the pose from the TF
    """
    # Look up for the transformation between dest_frame and turtle2 frames
    # and send velocity commands for turtle2 to reach dest_frame
    try:
        now = rclpy.time.Time()
        trans = self.tf_buffer.lookup_transform(
            origin_frame,
            dest_frame,
            now)
    except TransformException as ex:
        self.get_logger().error(
            f'Could not transform {origin_frame} to {dest_frame}: {ex}')
        return None


    translation_pose = trans.transform.translation
    rotation_pose = trans.transform.rotation

    self.get_logger().info("type translation_pose="+str(type(translation_pose)))
    self.get_logger().info("type rotation_pose="+str(type(rotation_pose)))


    pose = Pose()
    pose.position.x = translation_pose.x
    pose.position.y = translation_pose.y
    pose.position.z = translation_pose.z
    pose.orientation.x = rotation_pose.x
    pose.orientation.y = rotation_pose.y
    pose.orientation.z = rotation_pose.z
    pose.orientation.w = rotation_pose.w

    return pose
```

获取当前时间：

```
now = rclpy.time.Time()
```

此处此行检查缓冲区，并在当时从Origin_frame到DEST_FRAME的转换。如果没有发现，则捕获异常。

```
        trans = self.tf_buffer.lookup_transform(origin_frame,dest_frame,now)
```



### 代码解释：

#### 导入模块部分

```python
import rclpy  # 导入ROS 2 Python客户端库
from rclpy.node import Node  # 基础节点类
from rclpy.qos import QoSProfile  # 服务质量配置
from tf2_ros import TransformException  # TF变换异常
from tf2_ros.buffer import Buffer  # TF缓冲区
from tf2_ros.transform_listener import TransformListener  # TF监听器
import tf_transformations  # 用于处理转换矩阵和四元数的库
from std_msgs.msg import String  # 标准字符串消息类型
from gazebo_msgs.srv import SetEntityState  # Gazebo服务类型
from gazebo_msgs.msg import EntityState  # Gazebo消息类型
from geometry_msgs.msg import Pose, Twist, Vector3  # 用于位置和速度的消息类型

```

#### 自定义的Coordinates类

```python
class Coordinates:
    def __init__(self, x, y, z, roll, pitch, yaw):
        self.x = x  # X坐标
        self.y = y  # Y坐标
        self.z = z  # Z坐标
        self.roll = roll  # 绕X轴旋转
        self.pitch = pitch  # 绕Y轴旋转
        self.yaw = yaw  # 绕Z轴旋转

```

#### 主类 CamBotMove

```python
class CamBotMove(Node):
    def __init__(self, timer_period=0.05, model_name="cam_bot", init_dest_frame="carrot", trans_speed=1.0, rot_speed=0.1):
        super().__init__('force_move_cam_bot')  # 初始化节点
        self._model_name = model_name  # 模型名称
        self.set_destination_frame(new_dest_frame=init_dest_frame)  # 初始化目标坐标系
        self.set_translation_speed(speed=trans_speed)  # 设置平移速度
        self.set_rotation_speed(speed=rot_speed)  # 设置旋转速度

        # TF 监听器设置
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer_period = timer_period  # 定时器周期
        self.timer = self.create_timer(self.timer_period, self.timer_callback)  # 创建定时器

        # 订阅者设置
        self.subscriber = self.create_subscription(
            String,
            '/destination_frame',
            self.move_callback,
            QoSProfile(depth=1))  # 订阅目标坐标系名称的话题

        # Gazebo服务客户端设置
        self.set_entity_client = self.create_client(SetEntityState, "/cam_bot/set_entity_state")
        while not self.set_entity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.get_logger().info('service READY...')
        
        # 创建服务请求
        self.req = SetEntityState.Request()

    def timer_callback(self):
        self.move_step_speed()  # 在定时器回调中移动模型
        self.get_logger().info("Moved the Robot to frame =" + str(self.objective_frame))

    def set_translation_speed(self, speed):
        self.trans_speed = speed  # 设置平移速度
    
    def set_rotation_speed(self, speed):
        self.rot_speed = speed  # 设置旋转速度

    def set_destination_frame(self, new_dest_frame):
        self.objective_frame = new_dest_frame  # 设置目标坐标系

    def move_callback(self, msg):
        self.set_destination_frame(new_dest_frame=msg.data)  # 当收到新的目标坐标系名称时更新

    def move_step_speed(self):
        coordinates_to_move_to = self.calculate_coord()  # 计算要移动到的坐标
        if coordinates_to_move_to is not None:
            self.move_model(coordinates_to_move_to)  # 如果坐标有效，则移动模型
        else:
            self.get_logger().warning("No Coordinates available yet...")  # 如果坐标无效，打印警告

    def get_model_pose_from_tf(self, origin_frame="world", dest_frame="camera_bot_base_link"):
        try:
            now = rclpy.time.Time()  # 获取当前时间
            trans = self.tf_buffer.lookup_transform(
                origin_frame,
                dest_frame,
                now)  # 从TF缓冲区查找变换
        except TransformException as ex:
            self.get_logger().error(
                f'Could not transform {origin_frame} to {dest_frame}: {ex}')
            return None

        # 提取位置和方向
        translation_pose = trans.transform.translation
        rotation_pose = trans.transform.rotation
        pose = Pose()
        pose.position.x = translation_pose.x
        pose.position.y = translation_pose.y
        pose.position.z = translation_pose.z
        pose.orientation.x = rotation_pose.x
        pose.orientation.y = rotation_pose.y
        pose.orientation.z = rotation_pose.z
        pose.orientation.w = rotation_pose.w

        return pose

    def calculate_coord(self):
        pose_dest = self.get_model_pose_from_tf(origin_frame="world", dest_frame=self.objective_frame)  # 获取目标坐标系的位置
        if pose_dest is not None:
            explicit_quat = [pose_dest.orientation.x, pose_dest.orientation.y,
                             pose_dest.orientation.z, pose_dest.orientation.w]
            pose_now_euler = tf_transformations.euler_from_quaternion(explicit_quat)  # 将四元数转换为欧拉角

            roll = pose_now_euler[0]  # X轴旋转
            pitch = pose_now_euler[1]  # Y轴旋转
            yaw = pose_now_euler[2]  # Z轴旋转

            coordinates_to_move_to = Coordinates(x=pose_dest.position.x,
                                                y=pose_dest.position.y,
                                                z=pose_dest.position.z,
                                                roll=roll,
                                                pitch=pitch,
                                                yaw=yaw)
        else:
            coordinates_to_move_to = None

        return coordinates_to_move_to

    def move_model(self, coordinates_to_move_to):
        # 创建一个Pose消息
        pose = Pose()
        pose.position.x = coordinates_to_move_to.x
        pose.position.y = coordinates_to_move_to.y
        pose.position.z = coordinates_to_move_to.z

        # 从欧拉角创建四元数
        quaternion = tf_transformations.quaternion_from_euler(coordinates_to_move_to.roll,
                                                              coordinates_to_move_to.pitch,
                                                              coordinates_to_move_to.yaw)
        pose.orientation.x = quaternion[0]
        pose.orientation.y = quaternion[1]
        pose.orientation.z = quaternion[2]
        pose.orientation.w = quaternion[3]

        # 创建一个Twist消息，这里设置为零表示没有线速度和角速度
        twist = Twist()
        linear = Vector3()
        angular = Vector3()

        linear.x = 0.0
        linear.y = 0.0
        linear.z = 0.0

        angular.x = 0.0
        angular.y = 0.0
        angular.z = 0.0

        twist.linear = linear
        twist.angular = angular

        # 设置EntityState消息，包括模型名称、Pose、Twist和参考坐标系
        state = EntityState()
        state.name = self._model_name
        state.pose = pose
        state.twist = twist
        state.reference_frame = "world"

        self.req.state = state

        # 发送设置实体状态的服务请求
        try:
            self.future = self.set_entity_client.call_async(self.req)
        except Exception as e:
            self.get_logger().error('Error on calling service: %s', str(e))

# 程序入口
def main(args=None):
    rclpy.init()  # 初始化ROS 2客户端库
    move_obj = CamBotMove()  # 创建CamBotMove对象
    print("Start Moving")
    rclpy.spin(move_obj)  # 进入ROS 2事件循环

if __name__ == '__main__':
    main()

```

最后，使用变换中的信息来创建一个`Pose()`对象，从而移动Cam_bot机器人到那个精确的位置。这会将机器人放置在与你通过名为`/destination_frame`的话题请求的变换相同的坐标系中。

```
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/launch/
touch start_tf_fixes.launch.xml
```

  **start_tf_fixes.launch.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<launch>

    <include file="$(find-pkg-share my_tf_ros2_course_pkg)/launch/publish_static_transform_odom_to_world.launch.py"/>

    <node pkg="my_tf_ros2_course_pkg" exec="cam_bot_odom_to_tf_pub_late_tf_fixed.py" name="cam_bot_odom_to_tf_pub_late_tf_fixed_node">
    </node>

    <node pkg="my_tf_ros2_course_pkg" exec="move_generic_model.py" name="move_generic_model_node">
    </node>

</launch>
```

compile

```
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_tf_ros2_course_pkg start_tf_fixes.launch.xml
```



```
cd ~/ros2_ws
source install/setup.bash
rviz2 -d ~/ros2_ws/src/unit3_config.rviz
```



```
ros2 run my_tf_ros2_course_pkg static_broadcaster_front_turtle_frame.py turtle_chassis my_front_turtle_frame 0.4 0 0.4 0 0.7 3.1416
```



```
ros2 topic pub /destination_frame std_msgs/msg/String "data: 'my_front_turtle_frame'"
```

After some seconds, the **Cam_bot** should be where you placed the frame `my_front_turtle_frame`.

Now, if you move the turtle, the Cam_bot should follow it:

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/turtle_cmd_vel
```



## 4  Robot State Publisher

In this unit, you will learn the following:

- The function of Robot State Publisher
- How to use it
- Robot State Publisher vs. Joint State Publisher

### 4.1  Spawn a Robot into Gazebo

Use the package you generated earlier in this course to create a launch file that spawns a robot inside Gazebo. To begin, you need a new launch file:

  **Execute in Terminal 1**

```
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/launch
```

```
touch spawn_without_robot_state_publisher.launch.py
```

  **spawn_without_robot_state_publisher.launch.py**

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    urdf_file = 'unicycle.urdf'
    package_description = 'unicycle_robot_pkg'

    urdf = os.path.join(get_package_share_directory(
        package_description), 'urdf', urdf_file)

    xml = open(urdf, 'r').read()

    xml = xml.replace('"', '\\"')

    spawn_args = '{name: \"my_robot\", xml: \"' + xml + '\" }'
    
    spawn_robot =  ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/spawn_entity',
                 'gazebo_msgs/SpawnEntity', spawn_args],
            output='screen')

    return LaunchDescription([

     spawn_robot,
    ])
```

### Code explained

When executing this launch file, it calls `generate_launch_description()` first and processes the sequence of statements in its function body.

The first few lines are used to read the robot description data into the variable `spawn_args`.

The ExecuteProcess action called `spawn_robot` is defined with the corresponding `cmd` argument. This means this launch file performs a service call to the `/spawn_entity` service as if you would execute that service call from the command line.

Finally, add `spawn_robot` to the LaunchDescription list.

That is it. This file allows you to spawn a robot model into a simulation without running the robot_state_publisher node. Spawn it and have a look at the problem.

```python
# 导入os模块，用于操作系统功能，如文件路径操作
import os

# 导入ament_index_python包的函数，用于获取ROS 2包的共享目录路径
from ament_index_python.packages import get_package_share_directory

# 导入launch模块，用于定义ROS 2的启动过程
from launch import LaunchDescription
from launch.actions import ExecuteProcess

# 导入LaunchDescription函数，用于构建启动描述
from launch.substitutions import LaunchConfiguration

# 定义一个函数生成启动描述
def generate_launch_description():
    # 定义URDF文件的名称
    urdf_file = 'unicycle.urdf'
    # 定义包的名称
    package_description = 'unicycle_robot_pkg'

    # 使用os.path.join和get_package_share_directory函数构建URDF文件的完整路径
    urdf = os.path.join(get_package_share_directory(
        package_description), 'urdf', urdf_file)

    # 打开并读取URDF文件的内容
    xml = open(urdf, 'r').read()

    # 替换XML文件中的双引号以适应后续的格式要求
    xml = xml.replace('"', '\\"')

    # 构建用于spawn_entity服务的参数字符串
    spawn_args = '{name: \"my_robot\", xml: \"' + xml + '\" }'
    
    # 定义一个执行过程的动作，调用名为/spawn_entity的服务，传入上面构建的参数
    spawn_robot = ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/spawn_entity',
                 'gazebo_msgs/SpawnEntity', spawn_args],
            output='screen')

    # 返回一个启动描述，包含spawn_robot动作，当启动文件被执行时，这个动作将被触发
    return LaunchDescription([
     spawn_robot,
    ])

```

这个启动文件执行以下几个关键步骤：

1. **读取URDF文件**：从指定包的共享目录中读取机器人的URDF文件。
2. **格式化URDF内容**：对URDF文件内容进行适当的格式化处理，以确保在作为参数传递时符合语法要求。
3. **定义并执行服务调用**：通过ExecuteProcess动作，调用`/spawn_entity`服务，将格式化后的URDF内容作为参数传递，以在Gazebo等仿真环境中生成机器人实体。
4. **启动描述返回**：将定义的动作包含在启动描述中，使得当启动文件执行时可以触发这个动作。

通过这种方式，该文件允许你将一个机器人模型导入到仿真环境中，而无需运行`robot_state_publisher`节点。

```
source /home/simulations/ros2_sims_ws/install/setup.bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_tf_ros2_course_pkg spawn_without_robot_state_publisher.launch.py
```

Important: Source the ros2_ws in this new terminal first:

In [ ]:



```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2
```

Add the following **RVIZ2 elements** and their configuration as explained in the previous unit:

- Configure the Fixed Frame to `odom` frame.
- Add a TF display.
- Add a robot model. Note that the **Topic** option will not work as **Description Source**. You will not find any `/robot_description` topic.
- The reason is that you do not have any `robot_state_publisher` node running.

Notice that two tf frames are indeed being published. The best way to see them is to unset the checkmark corresponding to the robot model and use the mouse wheel to zoom in.

So why is that?

- First, we already explained that the frames of the different body parts and the `/robot_description` topic of the robot are not being published. The one in charge is typically **the ROBOT STATE PUBLISHER**.
- Second, the two frames published are `unicycle_base_link` and `odom`. These frames are published by a plugin inside the robot URDF called **differential_drive**. It receives velocity commands to move the robot around and publish the transform to the odometry frame.



You can have a better look at this through **topic info**:

  **Execute in Terminal 3**

Check who is publishing in the `/tf` topic:

```
source ~/ros2_ws/install/setup.bash
```



```
ros2 topic info /tf --verbose
```

You can see that the only publisher here of TFs is **differential_drive_controller**. And this controller **ONLY publishes the transform** between the `unicycle_base_link` of the robot and the `odom` frame.

If you move the robot, the **TFs will move without any issue**.

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard cmd_vel:=unicycle_cmd_vel
```

### 4.2  Robot State Publisher

The Robot State Publisher has several functions that we will review now:

- It takes the URDF or XACRO robot model description file as an **INPUT**.
- It publishes this description into the topic by default `/robot_description`, from which other tools like **Gazebo** or **RVIZ** will read.
- It publishes the **transforms** between ALL links (body parts) defined in the robot model. There are mainly **two kinds of joints** that connect links and, therefore, need TFs broadcasted:
  - FIXED joints: Their TFs are directly published, because the robot_state_publisher does not need extra info. The URDF is more than enough because it states the transformations between connected links.
  - MOVABLE joints: The robot_state_publisher needs one additional piece of information to publish these transforms: the `joint_states`. This refers to the **information on the angles or position of all the joints** that can be moved, like wheels, heads, arms, and grippers. In real robots, this is typically published by the robot controllers. In Gazebo, start the **joint_state_publisher** node or use a Gazebo Plugin to insert it into the URDF or XACRO robot model description file.

“机器人状态发布器（Robot State Publisher）具有多个功能，我们现在将进行回顾：

1. 它将URDF或XACRO机器人模型描述文件作为输入。
2. 它默认将此描述发布到主题`/robot_description`，其他工具如Gazebo或RVIZ将从中读取。

它发布在机器人模型中定义的所有链接（身体部分）之间的变换。主要有两种连接链接的关节，因此需要广播TF：

- 固定关节（FIXED joints）：它们的TF直接发布，因为`robot_state_publisher`不需要额外信息。URDF文件已足够，因为它声明了连接的链接之间的转换。
- 可移动关节（MOVABLE joints）：`robot_state_publisher`需要一条额外信息才能发布这些转换：joint_states。这指的是所有可移动关节（如轮子、头部、手臂和夹具）的角度或位置的信息。在真实的机器人中，这通常由机器人控制器发布。在Gazebo中，启动`joint_state_publisher`节点或使用Gazebo插件将其插入到URDF或XACRO机器人模型描述文件中。”

#### 解释总结：

`robot_state_publisher`节点在ROS系统中扮演了非常关键的角色，它的主要职责是处理和发布机器人的状态信息，这包括机器人模型的结构描述以及模型各个部分之间的空间关系（即TF变换）。

- **模型描述**：`robot_state_publisher`可以处理URDF（统一机器人描述格式）或XACRO（XML Macros）文件，这些文件详细描述了机器人的各个部件和它们是如何连接的。
- **发布描述**：该节点默认将机器人的模型描述发布到`/robot_description`主题，这使得如Gazebo这样的仿真工具或如RVIZ这样的可视化工具可以轻松访问和使用这些信息。
- **TF广播**：它还负责广播固定和可移动关节之间的变换。对于固定关节，由于它们之间的空间关系不变，所以可以直接从URDF中读取并发布。对于可移动关节，它需要实时的关节状态信息（例如关节的当前角度），这通常由传感器或控制器提供。

In a ROS2 Python **launch file**, add a **joint_state_publisher** node by creating a Node object like this and then include this object in the list of arguments that you pass into the LaunchDescription function:

```python
   joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

....

   return LaunchDescription([
        ....
        ....
        joint_state_publisher_node,
        robot_state_publisher_node,
        ......
        ......
    ])
```

Create a new **launch file**, which, in this case, starts the **robot_state_publisher**:

```cmd
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/launch
touch spawn.launch.py
```

  **spawn.launch.py**

```python
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
```

As you can see, the part of **Gazebo spawning is the same**.

And the **Robot State Publisher** is also similar.

You remap to use the topic `/unicycle_bot_robot_description` instead of the `/robot_description` topic.

Now you can start:

  **Execute in Terminal 1**



```
source /home/simulations/ros2_sims_ws/install/setup.bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_tf_ros2_course_pkg spawn.launch.py
```

  **Execute in Terminal 2**

Start RVIZ2 and add the element again or load a saved config file.



```
source /home/simulations/ros2_sims_ws/install/setup.bash
rviz2
```

- Set the `fixed_frame` to `odom`. Note that now, in the dropdown menu, you have many more coordinate frames.
- The `robot_state_publisher` publishes these new frames.
- Add a **robot model** element, and set the **topic** to `/unicycle_robot_description`.
- Add also a **TF element**. Set the **marker scale** to **5**. This increases the size of the TF markers.

  **Execute in Terminal 3**

Check who is publishing in the `/tf` topic:

```
ros2 topic info /tf --verbose
```

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard cmd_vel:=unicycle_cmd_vel
```

You can have a look also to see what **Robot State Publisher does** with the `ros2 node info` command:

  **Execute in Terminal 3**

```
ros2 node info /unicycle_robot_state_publisher
```

- See how it has as input `joint_states`
- It has `/tf`, `/tf_static` (for the fixed joints), and `/unicycle_bot_robot_description` as output.
