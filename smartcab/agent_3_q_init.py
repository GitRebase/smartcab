import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.state = {}
        self.learning_rate = 0.6
        self.discount_rate = 0.6
        self.exploration_rate = 0.05
        self.q_value_dic = {}

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        # deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = self.assemble_state(inputs)
        # print "LearningAgent.update(): next_point = {}, light = {}, oncoming = {}, left = {}".format(state['next_point'], state['light'], state['oncoming'], state['left'])  # [debug]

        # TODO: Select action according to your policy
        action = self.acquire_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.update_q_dic(self.state, action, reward)

        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

    def acquire_action(self, state):
        if random.random() < self.exploration_rate:
            return random.choice(Environment.valid_actions)
        optimal_action = Environment.valid_actions[0]
        q_value_max = 0
        for action in Environment.valid_actions:
            q_value = self.get_q_value(state, action)
            if q_value_max < q_value:
                optimal_action = action
                q_value_max = q_value
            elif q_value_max == q_value:
                optimal_action = random.choice([optimal_action, action])
        return optimal_action

    def max_q_value_among_actions(self, state):
        max_q = None
        for action in Environment.valid_actions:
            tmp = self.get_q_value(state, action)
            if (max_q is None) or (tmp > max_q):
                max_q = tmp
        return max_q

    def get_q_value(self, state, action):
        key = self.build_format_key(state, action)
        if key in self.q_value_dic:
            return self.q_value_dic[key]
        return 0

    def update_q_dic(self, state, action, reward):
        inputs = self.env.sense(self)
        self.next_waypoint = self.planner.next_waypoint()
        next_state = self.assemble_state(inputs)
        experienced_utilities = reward + (self.discount_rate * self.max_q_value_among_actions(next_state))
        cur_q_value = self.get_q_value(state, action)
        new_q_value = (1 - self.learning_rate) * cur_q_value + (self.learning_rate * experienced_utilities)

        self.q_value_dic[self.build_format_key(state, action)] = new_q_value

    def build_format_key(self, state, action):
        return str(state['next_point']) + ';' + \
               str(state['light']) + ';' + \
               str(state['oncoming']) + ';' + \
               str(state['left']) + ';' + \
               str(action)

    def assemble_state(self, inputs):
        return {'next_point': self.next_waypoint,
                'light': inputs['light'],
                'oncoming': inputs['oncoming'],
                'left': inputs['left']}

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=1, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    trials = 10
    sim.run(n_trials=trials)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
    print '******************************************'
    print '{} trials done, statistics:'.format(trials)
    print '******************************************'
    print 'Successful trials: {}'.format(e.suc)
    print '******************************************'
    print 'Failed trials: {}'.format(e.fail)
    print '******************************************'


if __name__ == '__main__':
    run()
