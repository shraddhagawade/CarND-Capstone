#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
from std_msgs.msg import Int32

import math
import numpy as np

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number
MAX_DECEL = 0.5


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below

        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        self.pose = None
        self.base_waypoints = None
        self.waypoints_2d = None
        self.waypoint_tree = None
        self.tl_waypoint_idx = -1

        self.loop()
        
    def loop(self):
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if self.pose and self.base_waypoints:
                # closest_waypoint_idx = self.get_closest_waypoint_idx()
                self.publish_waypoints()
            rate.sleep()
                
    def get_closest_waypoint_idx(self):
        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        
        # Get the index of the closest waypoint
        closest_idx = self.waypoint_tree.query([x,y],1)[1]
        
        closest_coord = self.waypoints_2d[closest_idx]
        prev_coord = self.waypoints_2d[closest_idx-1]
        
        closest_vector = np.array(closest_coord)
        prev_vector = np.array(prev_coord)
        car_vector = np.array([x,y])
        
        val = np.dot(closest_vector-prev_vector,car_vector-closest_vector)
        
        if val > 0:
            closest_idx = (closest_idx+1)%len(self.waypoints_2d)
        
        return closest_idx
    
    def publish_waypoints(self):
        # lane = Lane()
        # lane.header = self.base_waypoints.header
        # lane.waypoints = self.base_waypoints.waypoints[closest_waypoint_idx:closest_waypoint_idx+LOOKAHEAD_WPS]
        lane = self.generate_lane()
        self.final_waypoints_pub.publish(lane)
        
    def generate_lane(self):
        lane = Lane()
        lane.header = self.base_waypoints.header
        
        closest_waypoint_idx = self.get_closest_waypoint_idx()
        last_idx = closest_waypoint_idx + LOOKAHEAD_WPS
        next_waypoints = self.base_waypoints.waypoints[closest_waypoint_idx:last_idx]
        
        if (self.tl_waypoint_idx == -1) or (self.tl_waypoint_idx >= last_idx):
            lane.waypoints = next_waypoints
        else:
            lane.waypoints = self.decelerate_waypoints(next_waypoints, closest_waypoint_idx)
        
        return lane
    
    def decelerate_waypoints(self, next_waypoints, closest_waypoint_idx):
        temp = []
        for i,wp in enumerate(next_waypoints):
            
            p = Waypoint()
            p.pose = wp.pose
            
            stop_idx = max(self.tl_waypoint_idx - closest_waypoint_idx - 2, 0) # Take 2 waypoints before so that the front of the car stops before the traffic light
            dist = self.distance(next_waypoints, i, stop_idx)
            vel = math.sqrt(2*MAX_DECEL*dist)
            if vel < 1.:
                vel = 0.
            
            p.twist.twist.linear.x = min(vel, wp.twist.twist.linear.x)
            temp.append(p)
            
        return temp

    def pose_cb(self, msg):
        # TODO: Implement
        self.pose = msg

    def waypoints_cb(self, waypoints):
        # TODO: Implement
        self.base_waypoints = waypoints
        if not self.waypoints_2d:
            self.waypoints_2d = [[waypoint.pose.pose.position.x,waypoint.pose.pose.position.y] for waypoint in waypoints.waypoints]
            self.waypoint_tree = KDTree(self.waypoints_2d)

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        if(msg.data < 80):
            self.tl_waypoint_idx = -1
        else:
            self.tl_waypoint_idx = msg.data - 80 #to stop before the traffic light

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
