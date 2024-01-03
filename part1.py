# Group#: G14
# Student Names: James Zhang & Mitul Pandey

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self, queue, game):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self, queue, gui):
        self.queue = queue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self, queue):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = queue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55), (445, 55), (435, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.1     #speed of snake updates (sec)
        while self.gameNotOver:
            #complete the method implementation below
            time.sleep(SPEED)
            self.move()
            gameQueue.put({"move" : self.snakeCoordinates})

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        #complete the method implementation below

        eaten_something = False #Flag for snake growing if prey eaten
        prey = list(map(int,(gui.canvas.coords(gui.preyIcon)))) #Create local variable for the prey coordinates
                                                                #Mapped to int to avoid unexpected behaviour from comparing floats to ints

        '''
        move() arranged in this order as we first check if the last move ate a prey
        then we calculate new move, depending on whether prey was eaten or not
        then we see if new move triggers a game over
        then we update the snakes coordinates
        '''

        #Check if prey eaten:
        '''
        The following logic is for checking if the prey and snake head intersect. It works as follows:
         - For travelling vertically, the bottom or top edge (depending on travelling up or down) must be within 
         the vertical edges of the snake. Either the left or right edge of the prey must be within the horizontal
         edges of the snake.
         - For travelling horizontally, the left or right edge (depending on travelling up or down) must be within
         the horizontal edges of the snake. Either the top or bottom edge of the prey must be within the vertical
         edges of the snake.

         - We broke it up into each separate direction. Talking with the professor he said this was okay. 
         Additionally, this way we don't get unexpected behaviour when the snake approaches from the left but 
         eats the prey because it passes the requirements from the snake approaching from the right
         - Sometimes the snake won't eat the prey when most of the prey is visually enveloped in the snake head. 
         Or sometimes the prey will be eaten when it is visually outside the snake. We assume this is due to the
         limitations of tkinter's canvas as the debug output:
         print(f"Prey eaten! Snake head at {self.snakeCoordinates[-1]}, prey at {prey}")
         shows that the prey and snake head coordinates meet the requirements laid out in this if statement, but
         visually the prey appears outside the snake.
         - >= is used instead of > because sometimes the prey visually appeared in the snake but wasn't eaten because
         it's coordinates were right on the border of the snake head.
         - MOVE_LENGTH is used to calculate the x bounds as this should represent the x width of the snake head.
        '''
        if(
            #Snake travelling Down
            (self.direction == "Down" and
            self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[1] >= self.snakeCoordinates[-1][1] and
            (self.snakeCoordinates[-1][0] <= prey[0] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH or
            self.snakeCoordinates[-1][0] <= prey[2] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH)) or

            #Snake travelling Right
            (self.direction == "Right" and
            (self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[1] >= self.snakeCoordinates[-1][1] or
            self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[3] >= self.snakeCoordinates[-1][1]) and
            self.snakeCoordinates[-1][0] <= prey[0] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH) or

            #Snake travelling Up
            (self.direction == "Up" and 
            self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[3] >= self.snakeCoordinates[-1][1] and
            (self.snakeCoordinates[-1][0] <= prey[0] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH or
            self.snakeCoordinates[-1][0] <= prey[2] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH)) or

            #Snake travelling Left
            (self.direction == "Left" and
            (self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[1] >= self.snakeCoordinates[-1][1] or
            self.snakeCoordinates[-1][1] + SNAKE_ICON_WIDTH >= prey[3] >= self.snakeCoordinates[-1][1]) and
            self.snakeCoordinates[-1][0] <= prey[2] <= self.snakeCoordinates[-1][0] + MOVE_LENGTH)
        ):
        #Increment and update the score
            self.score += 1
            gameQueue.put({"score" : self.score})
            eaten_something = True 
        #Create new prey
            self.createNewPrey()

        #Move snake:
        newCoordinates = self.snakeCoordinates
        if not eaten_something: newCoordinates.pop(0)   #Keep the tail where it currently is if the snake grows
        newCoordinates.append(self.calculateNewCoordinates())   #Append the new head to snake coordinates

        #Check if game over:
        self.isGameOver(newCoordinates[-1])

        #Update coordinates:
        self.snakeCoordinates = newCoordinates

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]

        #Else statement isn't used because we don't need to act on a non valid key press
        if (self.direction == "Left"):
            return (lastX - MOVE_LENGTH, lastY)
        elif (self.direction == "Right"):
            return (lastX + MOVE_LENGTH, lastY)
        elif (self.direction == "Up"):
            return (lastX, lastY - MOVE_LENGTH)
        elif (self.direction == "Down"):
            return (lastX, lastY + MOVE_LENGTH)

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        #complete the method implementation below

        #Update gameNotOver and add "game_over" task:
        def callGameOver() -> None:
            self.gameNotOver = False
            gameQueue.put("game_over")

        #Check if snake has passed any wall:
        '''
         This checks if the next move places the snake outside the window bounds
         This allows the snake to move "along" the walls
        '''
        if (x < 0 or y < 0 or x > WINDOW_WIDTH or y > WINDOW_HEIGHT):
            callGameOver()

        #Check if snake has bit itself:
        elif snakeCoordinates in self.snakeCoordinates[:-1]:
            callGameOver()

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). 
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        #complete the method implementation below

        #Fetch an x,y within the window bounds
        x = random.randint(0 + THRESHOLD, WINDOW_WIDTH - THRESHOLD)
        y = random.randint(0 + THRESHOLD, WINDOW_HEIGHT - THRESHOLD)
        gameQueue.put({"prey" : (x - 5, y - 5, x + 5, y + 5)})

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    MOVE_LENGTH = 10    #Added to make move length variable
    
    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game(gameQueue)        #instantiate the game object

    gui = Gui(gameQueue, game)    #instantiate the game user interface
    
    QueueHandler(gameQueue, gui)  #instantiate our queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()