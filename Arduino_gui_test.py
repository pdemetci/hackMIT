"""
created 02.28.2015

@author: Lindsey Vanderlyn
"""
import pygame, random, math, time
from pygame.locals import *
import time
import eztext

class Robot:
    """
        Robot object represents the actual hardware (arduino) being used
    """
    def __init__(self):
        self.motors = [1, 2, 3]
         
class Move_button(object):
    """
        When pushed generates a move object 
    """
    def __init__(self, model, robot, motors, direction, duration, rect, name=''):
        self.is_pushed = False
        self.rect = pygame.Rect(rect)
        self.robot = robot
        self.motors = motors
        self.direction = direction
        self.duration = duration
        self.model = model
        self.name = name

    def create_object(self):
        self.model.instructions.append(Move(self.robot, self.motors, self.direction, self.duration, self.rect, self.name))

        
class Move(object):
    """
        Base for robot movement
    """
    def __init__(self, robot, motors, direction=1, duration=1, rect=(10,10,40,40), name=''):
        self.motors = [robot.motors[i] for i in motors]
        self.direction = direction
        self.duration = duration
        self.rect = pygame.Rect(rect)
        self.is_dragging = True
        self.name = name
        self.txtbx = eztext.Input(str(self.duration), maxlength=45, color=(255,0,0), prompt='duration: ')
        self.text_visible = False
        
class Model:
    def __init__(self, robot):
        self.robot = robot

        #Dock/trash/run
        self.dock = pygame.Rect(120, 100, 20, 60)
        self.trash = pygame.Rect(10, 750, 40, 40)
        self.run_btn = pygame.Rect(700, 750, 80, 40)

        #Buttons
        self.fwd_btn = Move_button(self, self.robot, [0,1], direction=0, duration=1, rect=(10, 10, 60, 60), name='Straight')
        self.right_bn = Move_button(self, self.robot, [0,1], direction=1, duration=1, rect=(10, 80, 60, 60), name='R turn')
        self.left_bn = Move_button(self, self.robot, [0,1], direction=-1, duration=1, rect=(10, 150, 60, 60), name='L turn')
        self.arm_bn = Move_button(self, self.robot, [2], direction=1, duration=1, rect=(10, 220, 60, 60), name='Arm')
        self.btns = [self.fwd_btn, self.right_bn, self.left_bn, self.arm_bn]
        self.instructions = []

    def execute(self):
        self.instructions = sorted(self.instructions, key= lambda instr: instr.rect.x)
        for instr in self.instructions:
            print("direction: ", instr.direction, "motors: ", instr.motors, "duration: ", instr.duration)

class View:
    """ Draws our game in a Pygame window, the view part of our model, view, controller"""
    def __init__(self,model,screen):
        """ Initializes view when the game starts """
        self.model = model
        self.screen = screen

    def create_font(self, rect):
        """
        Changes the font size based on the size of the box we are adding the label to

        """

        size = 16
        
        return pygame.font.SysFont('Arial', size)

    def draw(self):
        """Draws updated view every 0.001 seconds, or as defined by sleep at end of main loop
        Does not do any updating on its own, takes model objects and displays        
        """
        self.screen.fill(pygame.Color(0,0,0)) #Background
        pygame.draw.rect(screen, pygame.Color(0, 0, 0), pygame.Rect(0, 800, 300, 100)) 

        for btn in self.model.btns:
            pygame.draw.rect(screen, pygame.Color(120, 120, 120), btn.rect)
            self.screen.blit(self.create_font(btn.rect).render(btn.name, True, (255,255,255)), (btn.rect.x + 2, btn.rect.y+0.25*btn.rect.height))

        for instr in self.model.instructions:
            pygame.draw.rect(screen, pygame.Color(40, 80, 120), instr.rect)
            self.screen.blit(self.create_font(instr.rect).render(instr.name, True, (255,255,255)), (instr.rect.x + 2, instr.rect.y+0.25*instr.rect.height))
            if instr.text_visible == True:
                self.screen.blit(self.create_font(instr.rect).render(instr.txtbx.prompt+instr.txtbx.value, True, (255,255,255)), (700, 100))


        pygame.draw.rect(screen, pygame.Color(40, 60, 80), model.dock) #dock
        pygame.draw.rect(screen, pygame.Color(238, 45, 45), model.trash) #trash
        pygame.draw.rect(screen, pygame.Color(255, 255, 255), (100, 0, 1, 800)) #dividing line
        pygame.draw.rect(screen, pygame.Color(109, 190, 69), model.run_btn) #run button
        self.screen.blit(self.create_font(model.run_btn).render('Run', True, (255,255,255)), (model.run_btn.x+20, model.run_btn.y+10))



        pygame.display.update() #Pygame call to update full display



class Controller:
    """ Manipulate game state based on keyboard input, the controller part of our model, view, controller"""
    def __init__(self, model):
        """ Initializes controller to deal with keyboard input """
        self.model = model
        self.mouse_held = False
        self.drag_index = 0   
        self.instructions = model.instructions
        self.btn_hold_time = 0
        self.key_held = False
            
    def handle_pygame_mouse(self, event):
        """Takes position of mouse click and passes coordinates through interactibility check and applies
        proper reactions"""
        if event.type == MOUSEBUTTONDOWN: #when key is pressed we look at position and respond
            self.mouse_held = True
        if event.type == MOUSEBUTTONUP: #when key is pressed we look at position and respond
             self.mouse_held = False

    def update(self):

        for element in self.instructions:
            #Allows only one button to be dragged at a time
            instrs_held = sum(([int(el.is_dragging) for el in self.instructions]))
            if element.rect.collidepoint((mouseX, mouseY)) and self.mouse_held and instrs_held <= 1:
                element.is_dragging = True
                self.drag_index = self.instructions.index(element)
            elif not self.mouse_held or instrs_held >= 1 :
                element.is_dragging = False

            #Allows the duration of each instruction to be edited
            if element.rect.collidepoint((mouseX, mouseY)) and not self.mouse_held:
                element.text_visible = True    
            else:
                element.text_visible = False      

            #Allows elements to be thrown out     
            if element.rect.collidepoint((model.trash.x, model.trash.y)) and not self.mouse_held:
                model.instructions.remove(element)

            #If mouse is clicked on a block, moves the block as the mouse moves
            if element.is_dragging:
                #print "is dragging", element.name
                element.rect.y = mouseY - element.rect.size[1] // 2
                element.rect.x = mouseX - element.rect.size[0] // 2

        #Only allows for one instruction to be created per button press
        for btn in self.model.btns:                                                         
            if btn.rect.collidepoint((mouseX, mouseY)) and self.mouse_held:
                self.btn_hold_time += 1
                if self.btn_hold_time <=1:    
                    btn.create_object()
            elif not self.mouse_held:
                self.btn_hold_time = 0
        if model.run_btn.collidepoint((mouseX, mouseY)) and self.mouse_held:
            self.btn_hold_time += 1
            if self.btn_hold_time <=1:    
                model.execute()
            elif not self.mouse_held:
                self.btn_hold_time = 0



if __name__ == '__main__':
    pygame.init()   #initializes our game
    size = (800, 800)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    r = Robot()
    model = Model(r)
    view = View(model,screen)
    controller = Controller(model)
    
#    music = pygame.mixer.music.load("StillAlive.mp3")   #loads our background music and plays it 
#    pygame.mixer.music.play()

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP: #when key is pressed we look at position and respond
                controller.handle_pygame_mouse(event)
        for inst in model.instructions:
            if inst.text_visible == True:
                inst.txtbx.update(events)
                inst.duration = inst.txtbx.value
        mouseX, mouseY = pygame.mouse.get_pos()
        controller.update()
        # refresh the display
        pygame.display.flip()
        view.draw()        
        clock.tick(60)