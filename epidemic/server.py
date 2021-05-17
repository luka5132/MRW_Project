from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter


from .model import EpiDyn

COLORS = ['White', 'Red', 'Blue', 'Yellow', 'Green', 'Black']

def portrayCell(cell):
    '''
        This function is registered with the visualization server to be called
        each tick to indicate how to draw the cell in its current state.
        :param cell:  the cell in the simulation
        :return: the portrayal dictionary.
        '''
    if cell is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0, "x": cell.x, "y": cell.y}
    portrayal["Color"] = COLORS[cell.state]
    return portrayal


# Make a world that is 100x100, on a 500x500 display.
canvas_element = CanvasGrid(portrayCell, 50, 50, 500, 500)
cell_chart = ChartModule([{"Label": "Infectious1", "Color": 'Red'},
                          {"Label": "Infectious2", "Color": 'Yellow'},
                          {"Label": "Removed1", "Color": 'Blue'},
                          {"Label": "Removed2", "Color": 'Green'},
                          {"Label": "Dead", "Color": 'Black'}],
                         canvas_height=500, canvas_width=1000)

model_params = {
    "height": 50,
    "width": 50,
    "dummy": UserSettableParameter("static_text", value = "NB. Use 'Reset'-button to activate new model settings"),
    "schedule_type": UserSettableParameter("choice", "Scheduler type", value="Simultaneous", choices=list(EpiDyn.schedule_types.keys())),
    "startblock": UserSettableParameter("checkbox", "2x2 block start (or random)", value=True),
    "density": UserSettableParameter("slider", "Initial random density", 0.01, 0., 1.0, 0.01),
    "p_infect1": UserSettableParameter("slider", "Probability of Infection 1", 0.25, 0.00, 1.0, 0.01),
    "p_infect2": UserSettableParameter("slider", "Probability of Infection 2", 0.25, 0.00, 1.0, 0.01),
    "p_resistant1": UserSettableParameter("slider", "Probability of Resistance 1", 0.01, 0.00, 1.0, 0.01),
    "p_resistant2": UserSettableParameter("slider", "Probability of Resistance 2", 0.01, 0.00, 1.0, 0.01),
    "p_death1": UserSettableParameter("slider", "Probability of Death 1", 0.001, 0.00, 1.0, 0.001),
    "p_death2": UserSettableParameter("slider", "Probability of Death 2", 0.001, 0.00, 1.0, 0.001),
    "p_sensitive1": UserSettableParameter("slider", "Probability of Re-sensitiveness 1", 0.05, 0.00, 1.0, 0.01),
    "p_sensitive2": UserSettableParameter("slider", "Probability of Re-sensitiveness 2", 0.05, 0.00, 1.0, 0.01),
    "spatial": UserSettableParameter("checkbox", "Spatial", value=True),}

 
server = ModularServer(EpiDyn, [canvas_element, cell_chart], "Epidemic Dynamics",  model_params)