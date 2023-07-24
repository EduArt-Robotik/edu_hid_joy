from setuptools import setup

package_name = 'edu_hid_joy'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # ('share/ament_index/resource_index/packages',
        #     ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Christian Wendt',
    maintainer_email='christian.wendt@eduart-robotik.com',
    description='Python ROS joy node.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'edu_hid_joy = edu_hid_joy.edu_hid_joy_node:main'
        ],
    },
)
