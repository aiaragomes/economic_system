# -*- coding: utf-8 -*-

"""
Module with industry agent
"""

import numpy as np
from mesa import Agent


class IndustryAgent(Agent):
    '''
    Industry agent class
    '''

    def __init__(self, pos, model, agent_type, tax_rates):
        """ Initialization method of industry agent class

        Parameters
        ----------
        pos : tuple
            Agent position in the grid
        model : class
            Economic system model class
        agent_type : int
            Label for industry agent
        tax_rates : list
            List with tax rates
        """

        # Agent attributes
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.opex = 1.e6
        self.capex = 0
        self.employees = 200 if self.type == 1 else 400
        self.salary = 2000 if self.type == 1 else 1000
        self.profit_rate = 1.02 if self.type == 1 else 1.01
        self.products_value = 0
        self.sells = 0
        self.stocks = 0
        self.profit = 0
        self.tax_rate = tax_rates[1] if self.type == 1 else tax_rates[0]
        self.taxes = 0
        self.profit_after_tax = 0
        self.value = self.opex + self.capex

    def run_production(self):
        """
        Method to run production
        """

        # The value of the products produced depends on the opex and
        # profit rate of the sector
        self.products_value = self.profit_rate*self.opex

        # The stocks of the company are added to the new production
        self.products_value += self.stocks

    def run_sells(self):
        """
        Method to run sells
        """

        # There are different probabilities of selling the products per sector
        if self.type == 0:
            self.sells = np.random.uniform(low=0.94*self.products_value,
                                           high=1.0*self.products_value)
        else:
            self.sells = np.random.uniform(low=0.90*self.products_value,
                                           high=1.0*self.products_value)

        # The stocks of a company is what it was not able to sell
        self.stocks += (self.products_value - self.sells)

        # The profit is what was earned by sells minus the production cost
        self.profit = self.sells - self.opex

    def pay_taxes(self):
        """
        Method to run payment of taxes
        """

        # The company pays taxes on the profit it made,
        # in the case of a loss no taxes are paid
        self.taxes = self.tax_rate*self.profit if self.profit > 0 else 0

        # The profit after taxes
        self.profit_after_tax = self.profit - self.taxes

        # This profit after tax is now available for capital expenditure
        self.capex += self.profit_after_tax

        # The company value is assumed to be opex + capex
        self.value = self.opex + self.capex

    def investment_decision(self):
        """
        Method to perform investment decision
        """

        # The decision to invest or contract depends on the capex availability,
        # positive capex gives possibility of expansion,
        # negative capex means debt, the company might decide to shrink in size
        if self.capex > 0:

            # Decision to either invest or not
            if np.random.choice([0, 1]) == 1:

                # Cost to hire new employee,
                # their salary makes 40% of the necessary capital
                investment_cost = self.salary * 100 / 40

                # The maximum number of possible new employees depends on the
                # available capex
                max_hires = int( np.floor(self.capex / investment_cost) )

                # Perform investment
                if max_hires > 0:

                    # Decide how many new employees will be hired
                    hires = np.random.randint(low=1, high=max_hires+1)

                    # Update capex
                    self.capex -= hires * investment_cost

                    # Update opex
                    self.opex += hires * investment_cost

                    # Update number of employees
                    self.employees += hires

        else:

            # Employee cost, their salary makes 40% of the total
            employee_cost = self.salary * 100 / 40

            # The maximum number of employees that might be fired depends
            # on how big the debt is
            max_fires = int( np.floor( np.abs(self.capex) / employee_cost) )

            # Decide how many employees will be fired,
            # zero means decision was made to not fire
            fires = np.random.randint(low=0, high=max_fires+1)

            # Update opex
            self.opex -= fires * employee_cost

            # Update number of employees
            self.employees -= fires

    def step(self):
        """
        Method to run time steps
        """

        # Steps
        if self.type != -1:
            self.run_production()
            self.run_sells()
            self.pay_taxes()
            self.investment_decision()

        # Check bankrupt state
        if self.capex < 0:
            if -1*self.capex/self.opex > 0.05:
                self.type = -1