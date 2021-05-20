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
    
    def __init__(self, height=50, width=50, dummy="", schedule_type="Simultaneous",
                 startblock=1, density=0.01, p_infect1=0.5, p_infect2=0.5,
                 p_resistant1 = 0.1, p_resistant2 = 0.1, p_death1=0.0,
                 p_death2=0.0, p_sensitive1 = 0.05, p_sensitive2 = 0.05,
                 spatial=1, onefirst=1,of_timestep=100, mutant_size = 0.5):
        '''
        Create the CA field with (height, width) cells.
        '''

        #setting an explicit seed allows you to reproduce interesting runs
        #self.random.seed(30)
        
        # Set up the grid and schedule.
        self.schedule_type = schedule_type
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.of_timestep = of_timestep
        self.height = height
        self.width = width
        self.onefirst = onefirst
        self.mutant_size = mutant_size
        
        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=False)
        self.datacollector = DataCollector(
            {"Infectious1": lambda m: self.count_infectious1(m,width*height),
             "Infectious2": lambda m: self.count_infectious2(m,width*height),
             "TotalInfectious": lambda m: self.count_infectious(m,width*height),
             "Removed1": lambda m: self.count_removed1(m,width*height),
             "Removed2": lambda m: self.count_removed2(m,width*height),
             "Dead": lambda m: self.count_dead(m,width*height),
             "PositiveCorrelation1": lambda m: self.calculate_positive_correlation1(self,m,width*height),
             "NegativeCorrelation1": lambda m: self.calculate_negative_correlation1(self,m,width*height),
             "PositiveCorrelation2": lambda m: self.calculate_positive_correlation2(self,m,width*height),
             "NegativeCorrelation2": lambda m: self.calculate_negative_correlation2(self,m,width*height)})

        # Place a cell at each location, with default SENSTIVE,
        # and some (a 2x2 block) initialized to INFECTIOUS
        
        for (contents, x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self, spatial)
            cell.state = cell.SENSITIVE
            cell.p_infect1 = p_infect1
            cell.p_infect2 = p_infect1
            cell.p_death1 = p_death1
            cell.p_death2 = p_death2
            cell.p_sensitive1 = p_sensitive1
            cell.p_sensitive2 = p_sensitive2
            cell.p_resistant1 = p_resistant2
            cell.p_resistant2 = p_resistant2
            if startblock and not onefirst:
                if ((x == 43 or x == 44) and  (y == height/2 or y == height/2+1)):
                    cell.state = cell.INFECTIOUS2
                if ((x == 6 or x == 7) and  (y == height/2 or y == height/2+1)):
                    cell.state = cell.INFECTIOUS1
            elif onefirst:
                if ((x == width/2 or x == width/2+1) and  (y == height/2 or y == height/2+1)):
                    cell.state = cell.INFECTIOUS1
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
        print(self.measure_CA[0].x, self.measure_CA[0].step_n)
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
    def count_removed1(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.REMOVED1]
        return len(list_state)/grid_size
    
    @staticmethod
    def count_removed2(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.REMOVED2]
        return len(list_state)/grid_size
    
    @staticmethod
    def count_dead(model,grid_size):
        """
        Helper method to count cells in a given state in a given model.
        """
        list_state = [a for a in model.schedule.agents if a.state == a.DEAD]
        return len(list_state)/grid_size
    
    @staticmethod
    def count_infectious(model,grid_size):
        list_state = [a for a in model.schedule.agents if a.state == a.INFECTIOUS1
                      or a.state == a.INFECTIOUS2]
        return len(list_state)/grid_size
    
    @staticmethod
    def count_sensitive(model,grid_size):
        list_state = [a for a in model.schedule.agents if a.state == a.SENSITIVE]
        return len(list_state)/grid_size

    @staticmethod
    def calculate_positive_correlation1(self,model,grid_size):
        agents = model.schedule.agents
        list_state = []
        for i in range(len(agents)):
            if agents[i].state == agents[i].INFECTIOUS1 and agents[i+1].state == agents[i+1].INFECTIOUS1:
                list_state.append(agents[i])
        return (len(list_state)/grid_size)/(self.count_infectious1(model,grid_size)**2)
        
    @staticmethod
    def calculate_negative_correlation1(self,model,grid_size):
        agents = model.schedule.agents
        list_state = []
        for i in range(len(agents)):
            if agents[i].state == agents[i].INFECTIOUS1 and agents[i+1].state == agents[i+1].SENSITIVE:
                list_state.append(agents[i])
        return (len(list_state)/grid_size)/(self.count_infectious1(model,grid_size)*self.count_sensitive(model,grid_size))
        
        
    @staticmethod
    def calculate_positive_correlation2(self,model,grid_size):
        agents = model.schedule.agents
        list_state = []
        for i in range(len(agents)):
            if agents[i].state == agents[i].INFECTIOUS2 and agents[i+1].state == agents[i+1].INFECTIOUS2:
                list_state.append(agents[i])
        if self.count_infectious2(model,grid_size) == 0:
            return 0
        else:
            return (len(list_state)/grid_size)/(self.count_infectious2(model,grid_size)**2)
        
    @staticmethod
    def calculate_negative_correlation2(self,model,grid_size):
        agents = model.schedule.agents
        list_state = []
        for i in range(len(agents)):
            if agents[i].state == agents[i].INFECTIOUS2 and agents[i+1].state == agents[i+1].SENSITIVE:
                list_state.append(agents[i])
        if self.count_infectious2(model,grid_size) == 0:
            return 0
        else:
            return (len(list_state)/grid_size)/(self.count_infectious2(model,grid_size)*self.count_sensitive(model,grid_size))
        
