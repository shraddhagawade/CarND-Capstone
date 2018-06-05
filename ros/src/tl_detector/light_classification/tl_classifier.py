from styx_msgs.msg import TrafficLight

class TLClassifier(object):
    def __init__(self):
        #TODO load classifier
        tf.reset_default_graph()
        self.sess = tf.Session()
        
        saver = tf.train.import_meta_graph('model.ckpt.meta')
        saver.restore(sess,tf.train.latest_checkpoint('./'))
            
        rospy.loginfo('Model Restored')
        
        self.graph = tf.get_default_graph()
        self.prediction = graph.get_tensor_by_name("prediction")
        self.input = graph.get_tensor_by_name("input")        
        self.keep_prob = graph.get_tensor_by_name("keep_prob")

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        #TODO implement light color prediction
        pred = self.sess.run(self.prediction, feed_dict={self.input:image, self.keep_prob:1.}
        labels = [TrafficLight.GREEN,TrafficLight.UNKNOWN,TrafficLight.RED,TrafficLight.YELLOW]
        
        return labels[pred]
