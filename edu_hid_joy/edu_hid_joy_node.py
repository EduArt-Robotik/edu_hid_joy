# Very thanks to Michael Schmidpeter for providing code snippets.
import rclpy 
from rclpy.node import Node
from sensor_msgs.msg import Joy
import hid

from . import joy
from . import joy_ps4

class HidJoyNode(Node):
  def __init__(self):
    super().__init__('edu_hid_joy_node')
    #parameters
    self.declare_parameter('rate', 20.0)
    self.declare_parameter('device_name', 'Wireless')

    self.rate = self.get_parameter('rate').get_parameter_value().double_value
    self.device_name = self.get_parameter('device_name').get_parameter_value().string_value

    #print params
    self.get_logger().info('---------------------------------')
    self.get_logger().info('-- Parameters --')
    self.get_logger().info('rate: {}'.format(self.rate))
    self.get_logger().info('device_name: {}'.format(self.device_name))
    self.get_logger().info('---------------------------------')

    self.gamepad = None
    self.pub_joy = self.create_publisher(Joy, 'joy', 10)
    self.timer = self.create_timer(1/self.rate, self.timer_callback)

  #find device
  def find_device(self, device_str: str) -> hid.Device:
    devices = hid.enumerate()
    controller_id = None
    controller_vendor = None
    for e in devices:
      # print(f"{e['product_string']}")
      if device_str in e['product_string']:
        controller_id = e['product_id']
        controller_vendor = e['vendor_id']
        break
    if controller_id is None:
      return None
    #valid device
    device = hid.Device(controller_vendor, controller_id)
    # device.open(controller_vendor, controller_id)
    # device.darwin_set_open_exclusive(0)
    # device.set_nonblocking(True)

    return device

  def joy_callback(self, joy_msg: joy.Joy):
    axis_6 = 0.0 #cross btn left right
    if joy_msg.btn_left:
      axis_6 = 1.0
    elif joy_msg.btn_right:
      axis_6 = -1.0

    axis_7 = 0.0 #cross btn up down
    if joy_msg.btn_up:
      axis_7 = 1.0
    elif joy_msg.btn_down:
      axis_7 = -1.0

    ros_joy = Joy()
    ros_joy.header.stamp = self.get_clock().now().to_msg()
    ros_joy.header.frame_id = 'gamepad'

    axis_5 = (1.0 - (joy_msg.trigger_r * 2))  #forward
    axis_2 = (1.0 - (joy_msg.trigger_l * 2))  #backward


    ros_joy.axes = [
                    joy_msg.stick_l_x,  #0 
                    joy_msg.stick_l_y,  #1 
                    axis_2,  #2 
                    joy_msg.stick_r_x * -1,  #3 
                    joy_msg.stick_r_y * -1,  #4 
                    axis_5,  #5
                    axis_6,  #6
                    axis_7,  #7
                    0.0,  #8
                    0.0,  #9
                    0.0   #10
                    ]


    ros_joy.buttons = [joy_msg.btn_a,
                      joy_msg.btn_b,
                      joy_msg.btn_x,
                      joy_msg.btn_y,
                      joy_msg.btn_l1,
                      joy_msg.btn_r1,
                      joy_msg.btn_up,
                      joy_msg.btn_right,
                      joy_msg.btn_left,
                      joy_msg.btn_down,
                      joy_msg.btn_l2,
                      joy_msg.btn_r2,
                      joy_msg.btn_share,
                      joy_msg.btn_options,
                      joy_msg.btn_stick_l,
                      joy_msg.btn_stick_r,
                      ]
    self.pub_joy.publish(ros_joy)


  def timer_callback(self):
    if self.gamepad is None:
      self.gamepad = self.find_device(self.device_name)
      if self.gamepad is None:
        print("No device found, retrying in 1s")
        return
      print("Device found")
    try:
      rdy = False 
      #read untill no data is available
      while not rdy:
        if report:=self.gamepad.read(64):
          joy = joy_ps4.JoyPS4()
          joy.from_list(report)
          self.joy_callback(joy)
        else:
          rdy = True
    except OSError:
      print("Device disconnected")
      self.gamepad = None
      return

def main(args=None):
  rclpy.init(args=args)

  node = HidJoyNode()

  #fix exception
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass

  node.destroy_node()
  # rclpy.shutdown()


if __name__ == '__main__':
    main()
