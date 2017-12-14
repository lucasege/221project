import util, random, math, sys
import numpy as np
from collections import defaultdict
import tensorflow as tf

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines thes discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, simulator, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = np.zeros(5) #defaultdict(float)
        self.numIters = 1
        self.sim = simulator
        # These lines establish the feed-forward part of the network used to choose actions
        self.inputs1 = tf.placeholder(shape=[1,6],dtype=tf.float32)
        self.W = tf.Variable(tf.random_uniform([6,3],0,0.01))
        self.Qout = tf.matmul(self.inputs1, self.W)
        self.predict = tf.argmax(self.Qout,1)

        # Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        self.nextQ = tf.placeholder(shape=[1,3],dtype=tf.float32)
        loss = tf.reduce_sum(tf.square(self.nextQ - self.Qout))
        trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
        self.updateModel = trainer.minimize(loss)
        init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(init)
        self.allQ = None


    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        return np.dot(self.weights, self.featureExtractor(self.sim, state))

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        # stateArray = []
        # for key in state:
        #     stateArray.append(float(state[key]))
        a, self.allQ = self.sess.run([self.predict, self.Qout], feed_dict={self.inputs1:state})
        if random.random() < self.explorationProb:
            return random.choice(self.actions)
        else:
            return a

        # self.numIters += 1
        # if random.random() < self.explorationProb:
        #     return random.choice(self.actions)
        # else:
        #     return max((self.getQ(state, action), action) for action in self.actions)[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        #Obtain the Q' values by feeding the new state through our network
        Q1 = self.sess.run(self.Qout,feed_dict={self.inputs1:newState})
        #Obtain maxQ' and set our target value for chosen action.
        maxQ1 = np.max(Q1)
        targetQ = self.allQ
        targetQ[0,action] = reward + self.getStepSize()*maxQ1
        # targetQ[0,a[0]] = reward + y*maxQ1
        #Train our network using target and predicted Q values
        _,W1 = self.sess.run([self.updateModel, self.W], feed_dict={self.inputs1:state, self.nextQ:targetQ})
        #_,W1 = sess.run([updateModel,W],feed_dict={inputs1:np.identity(16)[s:s+1],nextQ:targetQ})



        # if newState == None: return
        # vhat = max([self.getQ(newState, a) for a in self.actions])
        # Qopt = self.getQ(state, action)
        # # sumWeights = float(np.sum(self.weights))+1
        # features = self.featureExtractor(self.sim, state)
        # self.weights = self.weights - self.getStepSize()*features*(Qopt-(reward + self.discount*vhat))
        # # for k,v in self.featureExtractor(self.sim, state):
        # #     self.weights[k] = self.weights.get(k,0) - self.getStepSize()*v*(self.weights[k]+1)/sumWeights*(Qopt-(reward + self.discount*vhat))

    def printWeights(self):
        print(self.weights)
