from styx_msgs.msg import TrafficLight
import tensorflow as tf
import rospy
import cv2
import numpy as np

class TLClassifier(object):
    def __init__(self):
        #TODO load classifier
        tf.reset_default_graph()
        
        frozen_graph="./light_classification/model.pb"
        with tf.gfile.GFile(frozen_graph, "rb") as f:
            restored_graph_def = tf.GraphDef()
            restored_graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(
            restored_graph_def,
            input_map=None,
            return_elements=None,
            name=""
        )
        self.graph = graph
        self.sess = tf.Session(graph=graph)
        
        self.prediction = self.graph.get_tensor_by_name("prediction:0")
        self.input = self.graph.get_tensor_by_name("input:0")        
        self.keep_prob = self.graph.get_tensor_by_name("keep_prob:0")

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
            print 'RED'
            return TrafficLight.RED
        else:
            print 'GO'
            return TrafficLight.UNKNOWN
