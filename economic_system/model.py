# -*- coding: utf-8 -*-

"""
Module with Economic System model
"""

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from .agent_industry import IndustryAgent


def compute_gdp(model):
    """ Function to calculate GDP

    Parameters
    ----------
    model : class
        Economic system model class

    Returns
    -------
    float
        Sum of all the value in the economy (GDP)
    """

    # Agent values excluding bankrupt companies
    agent_value = [agent.value for agent in model.schedule.agents
                   if agent.type != -1]

    return sum(agent_value)


def compute_employment(model):
    """ Function to calculate work-force size

    Parameters
    ----------
    model : class
        Economic system model class

    Returns
    -------
    int
        Number of employed workers in the economy
    """

    # Agent employees excluding bankrupt companies
    agent_employment = [agent.employees for agent in model.schedule.agents
                        if agent.type != -1]

    return sum(agent_employment)


def max_size_industry(model, industry_type=0):
    """ Function to find larger company in a certain industry sector

    Parameters
    ----------
    model : class
        Economic system model class
    industry_type : int
        Label for industry agent, if -2 looks in the whole economy

    Returns
    -------
    int
        Number of employed workers in the larger company of a sector
    """

    if industry_type != -2:
        agent_employment = [agent.employees for agent in model.schedule.agents
                            if agent.type == industry_type]
    else:
        agent_employment = [agent.employees for agent in model.schedule.agents]

    return max(agent_employment)


class EconomicSystemModel(Model):
    """ A simple model of an economic system.

    All agents begin with certain revenue, each time step the agents
    execute its expenditures and sell its production. If they retain a
    healthy revenue, they can choose to hire and grow;
    otherwise they can choose to shrink;
    if too much debt is acquired the agent goes bankrupt.
    Let's see what happens to the system.
    """

    def __init__(self, width=10, height=10,
                 industry_pc=0.8, services_pc=0.6,
                 tax_industry=0.1, tax_services=0.2,
                 nsteps=60):
        """ Initialization method of economic system model class

        Parameters
        ----------
        width : int
            Grid width
        height : int
            Grid height
        industry_pc : float
            Industry percentage in the system
        services_pc : float
            Services percentage in the industry
        tax_industry : float
            Tax rate for industry sector
        tax_services : float
            Tax rate for services sector
        nsteps : int
            Number of time steps in months
        """

        # Model input attributes
        self.width = width
        self.height = height
        self.industry_pc = industry_pc
        self.services_pc = services_pc
        self.nsteps = nsteps

        # Order in which agents perform their steps,
        # random activation means no particular preference
        self.schedule = RandomActivation(self)

        # Grid initialization
        self.grid = SingleGrid(width, height, torus=True)

        # Data to be located per time step
        self.datacollector = DataCollector(
            model_reporters={"GDP": compute_gdp,
                             "Employment": compute_employment},
            agent_reporters={"Employees": "employees",
                             "Value": "value",
                             "Industry": "type"}
        )

        # Set up agents using a grid iterator that returns
        # the coordinates of a cell as well as its contents
        for cell in self.grid.coord_iter():

            # Cell coordinates
            x = cell[1]
            y = cell[2]

            # Assign industry type
            if self.random.random() < self.industry_pc:
                if self.random.random() < self.services_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                # Initialize agent
                tax_rates = [tax_industry, tax_services]
                agent = IndustryAgent((x, y), self, agent_type, tax_rates)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

        # Running set to true and collect initial conditions
        self.running = True
        self.datacollector.collect(self)

        # Computed initial conditions of the model
        self.gdp = compute_gdp(self)
        self.employment = compute_employment(self)
        self.max_size_services = max_size_industry(self, 1)
        self.max_size_industry = max_size_industry(self, 0)
        self.max_size_industries = max_size_industry(self, -2)

    def step(self):
        '''
        Method to run one time step of the model
        '''

        # Run time step
        self.schedule.step()

        # Collect data
        self.datacollector.collect(self)

        # Computed metrics
        self.gdp = compute_gdp(self)
        self.employment = compute_employment(self)
        self.max_size_services = max_size_industry(self, 1)
        self.max_size_industry = max_size_industry(self, 0)
        self.max_size_industries = max_size_industry(self, -2)

        # Halt model after maximum number of time steps
        if self.schedule.steps == self.nsteps:
            self.running = False