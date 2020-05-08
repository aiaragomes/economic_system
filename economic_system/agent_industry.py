# -*- coding: utf-8 -*-

"""
Module with industry agent
"""

import numpy as np
from mesa import Agent


def ic_opex():
    """ Function to assign initial opex drawing from a normal distribution

    Returns
    -------
    opex : float
        Initial opex
    """

    # Draw opex from normal distribution
    opex = np.random.normal(1.e6, 0.2e6)

    # Fix possible minimum
    opex = opex if opex >= 1.e3 else 1.e3

    return opex


def ic_capex(opex):
    """ Function to assign initial capex drawing from a uniform distribution
    a percentage of the opex

    Parameters
    ----------
    opex : float
        Initial opex

    Returns
    -------
    capex : float
        Initial capex
    """

    # Draw capex from uniform distribution
    capex = np.random.uniform(-0.01, 0.05) * opex

    return capex


def ic_salary(type):
    """ Function to assign workers average salary

    Parameters
    ----------
    type : int
        Company type

    Returns
    -------
    salary : float
        Average workers salary
    """

    # Draw average salary from normal distribution
    salary = np.random.normal(2000, 200) if type == 1 \
        else np.random.normal(1000, 200)

    # Fix minimum wage
    salary = salary if salary >= 600 else 600

    return salary


def ic_employees(type, opex, salary):
    """ Function to assign initial number of employees

    Parameters
    ----------
    type : int
        Company type
    opex : float
        Company initial opex
    salary : float
        Average workers salary in the company

    Returns
    -------
    employees : int
        Initial number of employees
    """

    # Draw fraction of opex for salaries from uniform distribution
    opex_fc = np.random.uniform(0.4, 0.7) if type == 1 \
        else np.random.normal(0.2, 0.5)

    # Get initial number of employees, rounding down
    employees = int( np.floor( opex_fc * opex / salary ) )

    # Fix minimum number of employees to one, the minimum indicates
    # one-person business
    employees = employees if employees >= 1 else 1

    return employees


def ic_profit_rate(type):
    """ Function to assign company's profit rate

    Parameters
    ----------
    type : int
        Company type

    Returns
    -------
    profit_rate : float
        Company's profit rate
    """

    # Draw profit rate from normal distribution
    profit_rate = np.random.normal(1.05, 0.01) if type == 1 \
        else np.random.normal(1.03, 0.01)

    # Fix minimum profit rate
    profit_rate = profit_rate if profit_rate >= 1.001 else 1.001

    return profit_rate


def ic_stocks(type, products_value):
    """ Function to assign company's initial stocks

    Parameters
    ----------
    type : int
        Company type
    products_value : float
        Initial value in products

    Returns
    -------
    stocks : float
        Company's initial stocks
    """

    # Draw stocks fraction of products from uniform distribution
    stocks_fc = np.random.uniform(0.0, 0.1) if type == 1 \
        else np.random.uniform(0.0, 0.06)

    # Company's initial stocks
    stocks = stocks_fc * products_value

    return stocks


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
        self.opex = ic_opex()
        self.capex = ic_capex(self.opex)
        self.salary = ic_salary(self.type)
        self.employees = ic_employees(self.type, self.opex, self.salary)
        self.profit_rate = ic_profit_rate(self.type)
        self.products_value = self.profit_rate*self.opex
        self.sells = 0.0
        self.stocks = ic_stocks(self.type, self.products_value)
        self.profit = 0.0
        self.tax_rate = tax_rates[self.type]
        self.taxes = 0.0
        self.profit_after_tax = 0.0
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
            self.sells = np.random.uniform(0.94*self.products_value,
                                           1.0*self.products_value)
        else:
            self.sells = np.random.uniform(0.90*self.products_value,
                                           1.0*self.products_value)

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

                # Cost to hire new employee
                investment_cost = self.opex / self.employees

                # The maximum number of possible new employees depends on the
                # available capex
                max_hires = int( np.floor(self.capex / investment_cost) )

                # Perform investment
                if max_hires > 0:

                    # Decide how many new employees will be hired
                    hires = np.random.randint(1, max_hires+1)

                    # Update capex
                    self.capex -= hires * investment_cost

                    # Update opex
                    self.opex += hires * investment_cost

                    # Update number of employees
                    self.employees += hires

        else:

            # Employee cost
            employee_cost = self.opex / self.employees

            # The maximum number of employees that might be fired depends
            # on how big the debt is
            max_fires = int( np.floor( np.abs(self.capex) / employee_cost) )

            # Decide how many employees will be fired,
            # zero means decision was made to not fire
            fires = np.random.randint(0, max_fires+1)

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