import rclpy
from std_msgs.msg import String
import os


def start_car_callback(msg: String):
    if msg.data in ["PR001", "PR002"]:
        car_name = msg.data
        os.system(f"ros2 run gazebo_ros spawn_entity.py -database prius_hybrid -entity {car_name} -x 93 -y -11.7 -Y -1.57")
        print(f'Starting car: {car_name}')
    else:
        print(f'Invalid car name: {msg.data}')


def main():
    rclpy.init()
    node = rclpy.create_node('start_car_node')
    subscription = node.create_subscription(String, '/start_car', start_car_callback, 10)
    rclpy.spin(node)


if __name__ == '__main__':
    main()