from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import SimultaneousActivation, RandomActivation
from mesa.space import Grid

from .cell import Cell


class EpiDyn(Model):
    '''
    Represents the 2-dimensional model for epidemic dynamics
    '''
    
    schedule_types = {"Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}
    
    def __init__(self, height=50, width=50, dummy="", schedule_type="Simultaneous",startblock=1, density=0.01, p_infect1=0.25, p_infect2=0.5, p_death=0.0, p_death2=0.0, p_sensitive = 0.05, spatial=1):
        '''
        Create the CA field with (height, width) cells.
        '''

        #setting an explicit seed allows you to reproduce interesting runs
        #self.random.seed(30)
        
        # Set up the grid and schedule.
        self.schedule_type = schedule_type
        self.schedule = self.schedule_types[self.schedule_type](self)
        
        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=False)
        self.datacollector = DataCollector(
            {"Infectious1": lambda m: self.count_infectious1(m,width*height),
             "Infectious2": lambda m: self.count_infectious2(m,width*height),
             "Removed": lambda m: self.count_removed(m,width*height)})

        # Place a cell at each location, with default SENSTIVE,
        # and some (a 2x2 block) initialized to INFECTIOUS
        
        for (contents, x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self, spatial)
            cell.state = cell.SENSITIVE
            cell.p_infect1 = p_infect1
            cell.p_infect2 = p_infect1
            cell.p_death = p_death
            cell.p_death2 = p_death2
            cell.p_sensitive = p_sensitive
            if startblock:
                if ((x == 43 or x == 44) and  (y == height/2 or y == height/2+1)):
                    cell.state = cell.INFECTIOUS1
                if ((x == 6 or x == 7) and  (y == height/2 or y == height/2+1)):
                    cell.state = cell.INFECTIOUS2
            elif self.random.random() < density:
                    cell.state = cell.INFECTIOUS1
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

        self.measure_CA = []
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        '''
        Have the scheduler advance each cell by one step
        '''
        self.measure_CA = [a for a in self.schedule.agents]
        self.schedule.step()
               # collect data
        self.datacollector.collect(self)

    @staticmethod
    def count_infectious1(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.INFECTIOUS1]
        return len(list_state)/grid_size
    
    @staticmethod
    def count_infectious2(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.INFECTIOUS2]
        return len(list_state)/grid_size

    @staticmethod
    def count_removed(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.REMOVED]
        return len(list_state)/grid_size


