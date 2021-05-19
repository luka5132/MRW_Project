from mesa import Agent
import numpy as np
import random as rd


class Cell(Agent):
    '''Represents a single individual in the simulation.'''

    SENSITIVE = 0
    INFECTIOUS1 = 1
    INFECTIOUS2 = 3
    REMOVED1 = 2
    REMOVED2 = 4
    DEAD = 5

    def __init__(self, pos, model, spatial, init_state=SENSITIVE):
        '''
        Create a cell, in the given state, at the given x, y position.
        '''
        super().__init__(pos, model)
        self.x, self.y = pos
        self.spatial = spatial
        self.state = init_state
        self.step_n = 1
        self.switched = 0
        self._nextState = None

    @property
    def isInfectious1(self):
        return self.state == self.INFECTIOUS1
    
    @property
    def isInfectious2(self):
        return self.state == self.INFECTIOUS2

    @property
    def isSensitive(self):
        return self.state == self.SENSITIVE
    
    @property
    def isRemoved1(self):
        return self.state == self.REMOVED1
    
    @property
    def isRemoved2(self):
        return self.state == self.REMOVED2
    
    @property
    def isDead(self):
        return self.state == self.DEAD

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y), True)

    def step(self):
        '''
        Compute if the cell will be INFECTIOUS or REMOVED at the next tick.
        With simultaneous updating, he state is not changed here,
        but is just computed and stored in self._nextState,
        because the current state may still be necessary for our neighbors
        to calculate their next state.
        '''

        # Get the neighbors and apply the rules on whether to be INFECTIOUS or SENSITIVE
        # at the next tick.
        
        self.step_n += 1
        
        if self.spatial:
            self.neighbourhood = self.model.grid.iter_neighborhood(self.pos, moore=True, radius=2)
            self.neighbourhood = self.model.grid.get_cell_list_contents(self.neighbourhood)
            self.rd_neighbour = rd.choice(self.neighbourhood)

        # In the non-spatial setting, th he next function is using random cells instead
        # neigboring cells;  in this way "mean field" is simulated

        else:
            self.neighbourhood = rd.sample(self.model.measure_CA, 1)
            self.rd_neighbour = rd.choice(self.neighbourhood)

        # Assuming default nextState is unchanged
        self._nextState = self.state

        # Check if state will be changed
        if self.isInfectious1:
            if np.random.random() < self.p_resistant1:
                self._nextState = self.REMOVED1
            if np.random.random() < self.p_death1:
                self._nextState = self.DEAD
        if self.isInfectious2:
            if np.random.random() < self.p_resistant2:
                self._nextState = self.REMOVED2
            if np.random.random() < self.p_death2:
                self._nextState = self.DEAD
        if self.isDead:
            self._nextState = self.DEAD
        if self.isSensitive:
            if self.rd_neighbour.state == self.rd_neighbour.INFECTIOUS1:
                if np.random.random() < self.p_infect1:
                    self._nextState = self.INFECTIOUS1
            if self.rd_neighbour.state == self.rd_neighbour.INFECTIOUS2:
                if np.random.random() < self.p_infect2:
                    self._nextState = self.INFECTIOUS2
        if self.isRemoved1:
            if self.rd_neighbour.state == self.rd_neighbour.INFECTIOUS2:
                if np.random.random() < self.p_infect2:
                    self._nextState = self.INFECTIOUS2
            if rd.random() < self.p_sensitive1:
                self._nextState = self.SENSITIVE
        if self.isRemoved2:
            if self.rd_neighbour.state == self.rd_neighbour.INFECTIOUS1:
                if np.random.random() < self.p_infect1:
                    self._nextState = self.INFECTIOUS1
            if rd.random() < self.p_sensitive2:
                self._nextState = self.SENSITIVE
        if self.model.onefirst: 
            if not self.switched and self.step_n > self.model.of_timestep:
                if self.x >= self.model.width * (1 -self.model.mutant_size):
                    if self.isInfectious1:
                        self._nextState = self.INFECTIOUS2
        if self.model.schedule_type == "Random":
            self.advance()


        
    def advance(self):
        '''
        Simultaneously set the state to the new computed state -- computed in step().
        '''
        self.state = self._nextState

