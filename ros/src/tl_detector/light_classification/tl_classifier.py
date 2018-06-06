from styx_msgs.msg import TrafficLight
import tensorflow as tf
import rospy
import cv2
import numpy as np

class TLClassifier(object):
    def __init__(self):
        #TODO load classifier
        pass

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        #TODO implement light color prediction
        import numpy as np
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0,140,120])
        upper_red = np.array([50,255,255])
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
        count = np.count_nonzero(mask0)
        print count
        
        if(count>=200):
            return TrafficLight.RED
        else:
            return TrafficLight.UNKNOWN
