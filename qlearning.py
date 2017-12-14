import util, random, math, sys
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
        self.weights = defaultdict(float)
        self.numIters = 1
        self.sim = simulator
        #These lines establish the feed-forward part of the network used to choose actions
        self.inputs1 = tf.placeholder(shape=[1,6],dtype=tf.float32)
        self.W = tf.Variable(tf.random_uniform([6,3],0,0.01))
        self.Qout = tf.matmul(self.inputs1, self.W)
        self.predict = tf.argmax(self.Qout,1)

        #Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        nextQ = tf.placeholder(shape=[1,3],dtype=tf.float32)
        loss = tf.reduce_sum(tf.square(nextQ - self.Qout))
        trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
        updateModel = trainer.minimize(loss)
        init = tf.initialize_all_variables()
        self.sess = tf.Session()
        self.sess.run(init)


    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(self.sim, state):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):


        a, allQ = self.sess.run([self.predict, self.Qout], feed_dict={self.inputs1:state})
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
        # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
        if newState == None: return
        vhat = max([self.getQ(newState, a) for a in self.actions])
        Qopt = self.getQ(state, action)
        sumWeights = float(sum(self.weights.values()))+1
        for k,v in self.featureExtractor(self.sim, state):
            self.weights[k] = self.weights.get(k,0) - self.getStepSize()*v*(self.weights[k]+1)/sumWeights*(Qopt-(reward + self.discount*vhat))


        # if newState != None:
        #     eta = self.getStepSize()
        #     vOpt = max((self.getQ(newState, action), action) for action in self.actions(newState))[0]
        #     rightHand = (reward + self.discount * vOpt)
        #     leftHand = self.getQ(state, action)
        #     feature = self.featureExtractor(state)
        #     for f, v in self.featureExtractor(state):
        #         mult = eta * (leftHand - rightHand)
        #         sub = mult * v
        #         self.weights[f] -= sub
        # else:
        #     return None

    def printWeights(self):
        print(self.weights)
