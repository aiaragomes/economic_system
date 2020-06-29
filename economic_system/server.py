# -*- coding: utf-8 -*-

"""
Economic System visualization dashboard
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import TextElement
from mesa.visualization.UserParam import UserSettableParameter
from .model import EconomicSystemModel


class GDPElement(TextElement):
    '''
    Display a text with current GDP
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "GDP: " + str(round(model.gdp/1.e9, 2)) + " billions"


class WorkForceElement(TextElement):
    '''
    Display a text with current work force size
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Work force: " + str(model.work_force)


def economic_system_draw(agent):
    '''
    Portrayal method for canvas
    '''

    if agent is None:
        return

    # Shape to visualize agent
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0}

    # Draw agent with colour depending on sector and size on company size
    if agent.type == 0:
        portrayal["r"] = agent.employees/agent.model.max_size_industry
        portrayal["text"] = 'I'
        portrayal["Color"] = ["#FF0000", "#FF9999"]
        portrayal["stroke_color"] = "#00FF00"
    elif agent.type == 1:
        portrayal["r"] = agent.employees/agent.model.max_size_services
        portrayal["text"] = 'S'
        portrayal["Color"] = ["#0000FF", "#9999FF"]
        portrayal["stroke_color"] = "#000000"
    else:
        portrayal["r"] = 0.5
        portrayal["text"] = 'B'
        portrayal["Color"] = ["#FFFFFF", "#FFFFFF"]
        portrayal["stroke_color"] = "#000000"

    return portrayal


# Dashboard outputs
gdp_element = GDPElement()
work_force_element = WorkForceElement()
canvas_element = CanvasGrid(economic_system_draw, 20, 10, 800, 400)
employment_chart = ChartModule([
    {"Label": "Employment", "Color": "#0000FF"}],
    data_collector_name='datacollector'
)

# Model parameters
model_params = {
    "n_workers": UserSettableParameter("slider", "# workers in millions",
                                       0.1, 0.1, 5.0, 0.1),
    "unemployment": UserSettableParameter("slider", "Unemplyment rate",
                                          0.05, 0.0, 0.3, 0.01),
    "services_pc": UserSettableParameter("slider", "Fraction services",
                                         0.6, 0.00, 0.95, 0.05),
    "avg_opex": UserSettableParameter("slider", "Average opex in millions",
                                      1.0, 0.1, 5.0, 0.1),
    "bankrupt": UserSettableParameter("slider", "Bankrupt index in % of opex",
                                      5.0, 1.0, 50.0, 1.0),
    "salary_industry": UserSettableParameter("slider", "Avg salary industry",
                                             1000, 600, 3000, 100),
    "salary_services": UserSettableParameter("slider", "Avg salary services",
                                             2000, 600, 5000, 100),
    "profit_industry": UserSettableParameter("slider", "Avg profit industry",
                                             1.01, 1.005, 1.10, 0.005),
    "profit_services": UserSettableParameter("slider", "Avg profit services",
                                             1.02, 1.005, 1.20, 0.005),
    "tax_industry": UserSettableParameter("slider", "Tax rate industry",
                                          0.1, 0.01, 0.8, 0.01),
    "tax_services": UserSettableParameter("slider", "Tax rate services",
                                          0.2, 0.01, 0.8, 0.01),
    "nsteps": UserSettableParameter("slider", "Months",
                                    24, 12, 360, 12)
}

# Server
server = ModularServer(EconomicSystemModel,
                       [canvas_element, gdp_element, work_force_element,
                        employment_chart],
                       "Economic system model", model_params)
server.port = 8521