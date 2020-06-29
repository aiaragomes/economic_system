# -*- coding: utf-8 -*-

"""
Module with worker agent
"""

import numpy as np
from mesa import Agent


class WorkerAgent(Agent):
    '''
    Worker agent class
    '''

    def __init__(self, pos, model, agent_state):
        """ Initialization method of worker agent class

        Parameters
        ----------
        pos : tuple
            Agent position in the grid
        model : class
            Economic system model class
        agent_state : int
            Label for employment state
        """

        # Agent attributes
        super().__init__(pos, model)
        self.pos = pos
        self.state = agent_state # employed or unemployed
        self.skill = 0 # 0 or 1 related to industry sectors
        self.worth = 1000 # worth of worker based on skills/experience
        self.salary = 600 # salary of agent
        self.income_tax = 0.3*self.salary
        self.employer = 0 # tag with employer -> industry agent id
        self.experience = 0 # months worked
        self.idle_time = 0 # months unemployed

    def step(self):
        """
        Method to run time steps
        """

        # Steps
        self.career_decision()
