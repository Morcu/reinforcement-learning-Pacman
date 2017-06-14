# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
	self.table_file = open("qtable.txt", "r+")
	


    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgeinitnt.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------"
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Map:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()
        
    @staticmethod
    def printLineData(gameState):
	#outfile = open('LineData.txt', 'a')
	
	
	cadena = "ALegales="
	cadena += str(gameState.getLegalPacmanActions())
	cadena += ","
	cadena += "NFantasmas="
	cadena += str((gameState.getNumAgents() - 1))
	cadena += ","
	cadena += "FVivos="
	cadena += str(gameState.getLivingGhosts())
	cadena += ","
	cadena += "DFantasma="
	cadena += str(gameState.data.ghostDistances)
	cadena += ","
	cadena += "DPuntoC="
	cadena += str(gameState.getDistanceNearestFood())
	cadena += ","
	cadena += "RecompensaF=200,"
	cadena += "RecompensaP=100,"
	cadena += "PacManPos="
	cadena += str(gameState.getPacmanPosition())
	cadena += ","
	cadena += "FPos="
	cadena += str(gameState.getGhostPositions())
	cadena += ","
	cadena += "FDir="
	cadena += str([gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
	cadena += ","
	

	return cadena

    
    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
	
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
#ver cual es el fantasma que esta mas cerca, y comprobar sus coordenadas si la x del fantasma es menor que la del PC debe ir al norte, si es mayor al sur y si es igual nada
#si la y del fantasma es menor que la del PC este debera moverse al oeste, sino al este y sino nada
    
	move_random = random.randint(0, 3)
       
	
	#Asignamos el valor mas alto a la variable auxiliar para controlar que se elija la menor distancia al fantasma
	if gameState.data.layout.width < gameState.data.layout.height:
		aux = gameState.data.layout.height
	else:
		aux = gameState.data.layout.width
	
	#cogemos la distancia menor
	for i in range(0, (gameState.getNumAgents() - 1)):
		
		if gameState.data.ghostDistances[i]< aux:
			if gameState.getLivingGhosts()[i+1] == True:
				aux = gameState.data.ghostDistances[i]
				iteracion = i

	xFantasma = gameState.getGhostPositions()[iteracion][0]
	yFantasma = gameState.getGhostPositions()[iteracion][1]
	xPacman = gameState.getPacmanPosition()[0]
	yPacman = gameState.getPacmanPosition()[1]

	print 'xFantasma'+str(xFantasma) +'xPacman'+str(xPacman)+'yFantasma'+str(yFantasma)+'yPacman'+str(yPacman)

	
	 
	if(xFantasma < xPacman):
		if Directions.WEST in legal:
			move = Directions.WEST
		else:
			if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        		if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        		if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        		if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
	if(xFantasma > xPacman): 
		if Directions.EAST in legal:   
			move = Directions.EAST
		else:
			if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        		if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        		if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        		if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
	if(yFantasma > yPacman): 
		if Directions.NORTH in legal:   
			move = Directions.NORTH
		else:
			if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        		if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        		if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        		if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
	if(yFantasma < yPacman):
		if Directions.SOUTH in legal:  
			move = Directions.SOUTH	
		else:
			if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        		if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        		if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        		if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
	print "mover " + str(move)
	


        return move



class QLearningAgent_100330657_100330670(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
	self.epsilon=0.25
	self.gamma=0.8	
	self.alpha=0.2
	self.discount=0.9
	self.numTraining=0
	self.maximo = -1
	
	self.table_file = open("qtable.txt", "r+")
	
	self.maximo = (gameState.data.layout.height-4) + (gameState.data.layout.width-2)
	print "max"
	print self.maximo
	self.maximo = 30
	#self.contruirQtable(30)

	self.table_file = open("qtable.txt", "r+")
	self.q_table = self.readQtable()
	print "q_table"
	
	self.primera = True
	self.cadena = ""
	self.estado = "" 
	self.estadoSig = "" 
	self.actions = {"north":0, "south":1, "east":2, "west":3, "exit":4}
	self.iniciar = 1;

	

    def contruirQtable(self,tamMax):
	"Write qtable to disc"
	
	table = self.table_file.readlines()
        self.table_file.seek(0)
        self.table_file.truncate()
	numeroLineas = 8*tamMax 
        for line in range(numeroLineas):
            for item in range(4):
                self.table_file.write(str(0.0)+" ")
            self.table_file.write("\n")
	self.table_file.close()

    def readQtable(self):
	"Read qtable from disc"
 	
	table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table
	
 
    def writeQtable(self):
	"Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")

    def computePosition(self, gameState):
	"""
	Compute the row of the qtable for a given state.
	For instance, the state (3,1) is the row 7
	"""
	
	'''
	Buscar el fantasma mas cercano, hallar su distancia y posicion relativa
	'''

	if gameState.data.layout.width < gameState.data.layout.height:
		aux = gameState.data.layout.height
	else:
		aux = gameState.data.layout.width
	#cogemos la distancia menor

	for i in range(0, (gameState.getNumAgents() - 1)):
		
		if self.distancer.getDistance(gameState.getGhostPositions()[i],gameState.getPacmanPosition())< self.maximo:
			if gameState.getLivingGhosts()[i+1] == True:
				aux = self.distancer.getDistance(gameState.getGhostPositions()[i],gameState.getPacmanPosition())
				iteracion = i

	xFantasma = gameState.getGhostPositions()[iteracion][0]
	yFantasma = gameState.getGhostPositions()[iteracion][1]
	xPacman = gameState.getPacmanPosition()[0]
	yPacman = gameState.getPacmanPosition()[1]
	
	'''Posicion relativa:
		Arriba = 0
		Abajo = 1
		Derecha = 2
		Izqueirda = 3
		Arriba-Derecha = 4
		Arriba-Izquierda = 5
		Abajo-Derecha = 6
		Abajo-Izquierda = 7
	'''
	posicion = -1

	#Arriba
	if(yFantasma > yPacman):
		#Arriba-Derecha
		if(xFantasma > xPacman):
			posicion = 4
		#Arriba-izquierda
		if(xFantasma < xPacman):
			posicion = 5
		#Arriba
		if(xFantasma == xPacman):
			posicion = 0		

	#Abajo
	if(yFantasma < yPacman):
		#Abajo-Derecha
		if(xFantasma > xPacman):
			posicion = 6
		#Abajo-izquierda
		if(xFantasma < xPacman):
			posicion = 7
		#Abajo
		if(xFantasma == xPacman):
			posicion = 1

	if(yFantasma == yPacman):
		#Abajo-Derecha
		if(xFantasma > xPacman):
			posicion = 2

		#Abajo-izquierda	
		if(xFantasma < xPacman):
			posicion = 3

	# Distancia + (Posicion Relativa * maximo)
	'''print "Dist: ", gameState.data.ghostDistances[iteracion]
	print "pos: ", posicion
	print "max: ", self.maximo
	'''
	'''
	print "Living Gosht", gameState.getLivingGhosts()
	print "Distancia " ,self.distancer.getDistance(gameState.getGhostPositions()[iteracion],gameState.getPacmanPosition())
	print "iteracion", iteracion
	print "posicion", posicion 
	print "maximo", self.maximo


	print "EL NUMERO MAGICO"
	print self.distancer.getDistance(gameState.getGhostPositions()[iteracion],gameState.getPacmanPosition()) + posicion * self.maximo
	'''  
     
	return 	self.distancer.getDistance(gameState.getGhostPositions()[iteracion],gameState.getPacmanPosition()) + posicion * self.maximo


    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)

	action_column = -1
	if(action == Directions.NORTH):
	       action_column = 0

	if(action == Directions.SOUTH):
	       action_column = 1

	if(action == Directions.EAST):
	       action_column = 2

	if(action == Directions.WEST):
	       action_column = 3


        return self.q_table[position][action_column]


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
     	legalActions = self.getLegalActions(state)
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = self.getLegalActions(state)
	if("Stop" in legalActions):
		legalActions.remove("Stop")       

        if len(legalActions)==0:
          return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
	
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def getLegalActions(self, gameState):
	return gameState.getLegalPacmanActions()


    def getAccion(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """

        # Pick Action
        legalActions = self.getLegalActions(state)
	action = None
	if("Stop" in legalActions):
		legalActions.remove("Stop")       

        if len(legalActions) == 0:
             return action

        flip = util.flipCoin(self.epsilon)

        if flip:
		return random.choice(legalActions)
        return self.getPolicy(state)


    def chooseAction(self, gameState):
	#print gamestate
	self.countActions = self.countActions + 1
	print "TICK"
	print self.countActions/2
	print "Score: ", gameState.getScore()

	if(self.primera):
			self.estado = gameState
			
			action = self.getAccion(gameState)		
			
			if action == "North":
				self.cadena += "0"
			if action == "South":
				self.cadena += "1"
			if action == "East":
				self.cadena += "2"
			if action == "West":
				self.cadena += "3"
			self.primera = False
		

	else:
			
			self.estadoSig = gameState
	
			#Update
			self.update(self.estado, self.cadena,self.estadoSig)
			
			self.estado = self.estadoSig
			
			self.cadena = ""
			action = self.getAccion(gameState)
		
	    		if action == "North":
				self.cadena += "0"

			if action == "South":
				self.cadena += "1"

			if action == "East":
				self.cadena += "2"

			if action == "West":
				self.cadena += "3"
	

	return action


    def update(self, state, action, nextState):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

	  Good Terminal state -> reward 1
	  Bad Terminal state -> reward -1
	  Otherwise -> reward 0

	  Q-Learning update:

	  if terminal_state:
		Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
	  else:
	  	Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))
		
        """
        "*** YOUR CODE HERE ***"
	fantasmasEstado = 0
	fantasmasEstadoSig = 0
	
	#Numero de fantasmas en el estado
	for i in range(0, (state.getNumAgents() - 1)):
		if state.getLivingGhosts()[i+1] == True:
			fantasmasEstado += 1
	
	#Numero de fantasmas en el estado sig
	for i in range(0, (nextState.getNumAgents() - 1)):
		if nextState.getLivingGhosts()[i+1] == True:
			fantasmasEstadoSig += 1
	numF = 0
	#Numero de fantasmas en el estado sig
	for i in range(0, (nextState.getNumAgents() - 1)):
		if nextState.getLivingGhosts()[i+1] == True:
			numF += 1
		

	if(fantasmasEstado > fantasmasEstadoSig):
		reward = 100
	else:
		reward = 0


        legalActions = self.getLegalActions(nextState)

	action_column = int(action)
        if len(legalActions)==0:
		
        	self.q_table[self.computePosition(state)][action_column] = (1-self.alpha) * self.getQValue(state,action) + self.alpha * (reward + 0)
		self.writeQtable()
	        self.table_file.close()		
	else:
		
		self.q_table[self.computePosition(state)][action_column] = (1-self.alpha) * self.getQValue(state,action) + self.alpha * (reward + self.discount*self.computeValueFromQValues(nextState))


    def getPolicy(self, state):
	"Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state)

    def getValue(self, state):
	"Return the highest q value for a given state"
        return self.computeValueFromQValues(state)

    def __del__(self):
	"Destructor. Invokation at the end of each episode"

    
