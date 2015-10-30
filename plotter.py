import pygame
from pygame.gfxdraw import aacircle
import sys
import numpy as np

class Plotter(object):

    def __init__(self):
        self.set_constants()
        self.set_variables()
        pygame.init()
        pygame.mouse.set_visible(not pygame.mouse.set_visible)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
                        (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def set_constants(self):
        # display parameters
        self.SCREEN_HEIGHT = 800 # in pixels
        self.SCREEN_WIDTH = 800 # in pixels
        self.FRAME_RATE = 60 # in Hz
        self.BG_COLOR = 120,120,120
        self.TREADMILL_COLOR = 180,180,180
        self.PLOT_COLOR = 30,30,30
        self.TREADMILL_WIDTH = 0.4*self.SCREEN_WIDTH
        self.TREADMILL_HEIGHT = 0.5*self.SCREEN_HEIGHT
        self.PLOT_WIDTH = self.TREADMILL_WIDTH
        self.PLOT_HEIGHT = 0.3*self.SCREEN_HEIGHT
        self.FORCE_RAD = 12

        self.YPOS_BUFFER = ((self.SCREEN_HEIGHT
                             - self.TREADMILL_HEIGHT
                             - self.PLOT_HEIGHT)/3.)
        self.TREADMILL_YPOS = self.YPOS_BUFFER
        self.PLOT_YPOS = self.TREADMILL_YPOS + self.YPOS_BUFFER + self.TREADMILL_HEIGHT

        self.XPOS_BUFFER = (self.SCREEN_WIDTH-2*self.TREADMILL_WIDTH)/3.

        self.LEFT_TREADMILL_XPOS = self.XPOS_BUFFER
        self.RIGHT_TREADMILL_XPOS = 2*self.XPOS_BUFFER + self.TREADMILL_WIDTH
        self.LEFT_PLOT_XPOS = self.XPOS_BUFFER
        self.RIGHT_PLOT_XPOS = 2*self.XPOS_BUFFER + self.PLOT_WIDTH

        self.LEFT_TREADMILL_RECT = pygame.Rect(self.LEFT_TREADMILL_XPOS,
                                   self.TREADMILL_YPOS,
                                   self.TREADMILL_WIDTH,
                                   self.TREADMILL_HEIGHT)
        self.RIGHT_TREADMILL_RECT = pygame.Rect(self.RIGHT_TREADMILL_XPOS,
                                    self.TREADMILL_YPOS,
                                    self.TREADMILL_WIDTH,
                                    self.TREADMILL_HEIGHT)
        self.LEFT_PLOT_RECT = pygame.Rect(self.LEFT_PLOT_XPOS,
                                   self.PLOT_YPOS,
                                   self.PLOT_WIDTH,
                                   self.PLOT_HEIGHT)
        self.RIGHT_PLOT_RECT = pygame.Rect(self.RIGHT_PLOT_XPOS,
                                    self.PLOT_YPOS,
                                    self.PLOT_WIDTH,
                                    self.PLOT_HEIGHT)

        # data collection parameters
        self.SAMPLE_FREQ = 1000 # in Hz
        self.TIME_HISTORY = 10 # in seconds
        self.TIME_POINTS = self.SAMPLE_FREQ*self.TIME_HISTORY
        self.DISPLAY_FREQ = 10 # in Hz
        self.DISPLAY_POINTS = self.DISPLAY_FREQ*self.TIME_HISTORY
        self.DISPLAY_RATIO = self.SAMPLE_FREQ/self.DISPLAY_FREQ # make sure evenly divisible

        # force display parameters
        self.FORCE_MAX = 100 # in Newtons
        self.FORCE_THRESHOLD = 25 # in Newtons

    def set_variables(self):
        self.force_dict = {}
        self.force_dict['left'] = {'frontleft': np.zeros(self.TIME_POINTS),
                                   'frontright': np.zeros(self.TIME_POINTS),
                                   'backleft': np.zeros(self.TIME_POINTS),
                                   'backright': np.zeros(self.TIME_POINTS)}
        self.force_dict['right'] = {'frontleft': np.zeros(self.TIME_POINTS),
                                    'frontright': np.zeros(self.TIME_POINTS),
                                    'backleft': np.zeros(self.TIME_POINTS),
                                    'backright': np.zeros(self.TIME_POINTS)}
        self.force_display_dict = {}
        self.force_display_dict['left'] = {'frontleft': np.zeros(self.DISPLAY_POINTS),
                                           'frontright': np.zeros(self.DISPLAY_POINTS),
                                           'backleft': np.zeros(self.DISPLAY_POINTS),
                                           'backright': np.zeros(self.DISPLAY_POINTS),
                                           'mean': np.zeros(self.DISPLAY_POINTS)}
        self.force_display_dict['right'] = {'frontleft': np.zeros(self.DISPLAY_POINTS),
                                            'frontright': np.zeros(self.DISPLAY_POINTS),
                                            'backleft': np.zeros(self.DISPLAY_POINTS),
                                            'backright': np.zeros(self.DISPLAY_POINTS),
                                            'mean': np.zeros(self.DISPLAY_POINTS)}
        ###########################
        # only for sample display #
        ###########################
        self.force_dict['left']['frontleft'][:] = 100*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['left']['frontright'][:] = 70-70*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['left']['backleft'][:] = 60*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['left']['backright'][:] = 30-30*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['right']['frontleft'][:] = 40*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['right']['frontright'][:] = 50*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['right']['backleft'][:] = 80-80*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        self.force_dict['right']['backright'][:] = 90*np.arange(self.TIME_POINTS)/float(self.TIME_POINTS)
        ###########################

        self.left_force_display = np.ones((2,self.DISPLAY_POINTS))
        self.right_force_display = np.ones((2,self.DISPLAY_POINTS))
        self.left_force_display[0,:] = (self.LEFT_PLOT_XPOS
                                        +np.arange(self.DISPLAY_POINTS)
                                         /float(self.DISPLAY_POINTS)
                                         *self.PLOT_WIDTH)
        self.right_force_display[0,:] = (self.RIGHT_PLOT_XPOS
                                         +np.arange(self.DISPLAY_POINTS)
                                          /float(self.DISPLAY_POINTS)
                                          *self.PLOT_WIDTH)
        self.left_leftright_ratio = 0
        self.left_fwdback_ratio = 0
        self.right_leftright_ratio = 0
        self.right_fwdback_ratio = 0

    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def update(self):
        ######################
        # only for test data #
        ######################
        for key1,val1 in self.force_dict.iteritems():
            for key2,val2 in val1.iteritems():
                self.force_dict[key1][key2] = np.roll(self.force_dict[key1][key2], -1)

        #####################
        # needs to be added #
        #####################
        # self.force_dict['left']['frontleft'][:] = force_array_left_frontleft[-self.TIME_POINTS:]
        # self.force_dict['left']['frontright'][:] = force_array_left_frontright[-self.TIME_POINTS:]
        # ...
        # self.force_dict['right']['backright'][:] = force_array_right_backright[-self.TIME_POINTS:]


        # calculate display parameters
        for key1,val1 in self.force_dict.iteritems():
            for key2,val2 in self.force_dict[key1].iteritems():
                for samples in range(self.DISPLAY_POINTS):
                    start_idx = samples*self.DISPLAY_RATIO
                    end_idx = start_idx + self.DISPLAY_RATIO
                    self.force_display_dict[key1][key2][samples] = (
                        np.mean(self.force_dict[key1][key2][start_idx:end_idx]))

        # calculate mean force
        for key,val in self.force_display_dict.iteritems():
            for sample in range(self.DISPLAY_POINTS):
                self.force_display_dict[key]['mean'][sample] = np.mean([self.force_display_dict[key]['frontleft'][sample],
                                                                self.force_display_dict[key]['frontright'][sample],
                                                                self.force_display_dict[key]['backleft'][sample],
                                                                self.force_display_dict[key]['backright'][sample]])

        self.left_force_display[1,:] = (self.PLOT_YPOS + self.PLOT_HEIGHT
                                        - self.force_display_dict['left']['mean'][:]
                                          /self.FORCE_MAX*self.PLOT_HEIGHT)
        self.right_force_display[1,:] = (self.PLOT_YPOS + self.PLOT_HEIGHT
                                         - self.force_display_dict['right']['mean'][:]
                                           /self.FORCE_MAX*self.PLOT_HEIGHT)

        # calculate realtime display parameters
        self.left_force_left = self.force_display_dict['left']['frontleft'][-1]+self.force_display_dict['left']['backleft'][-1]
        self.left_force_right = self.force_display_dict['left']['frontright'][-1]+self.force_display_dict['left']['backright'][-1] 
        self.left_force_fwd = self.force_display_dict['left']['frontleft'][-1]+self.force_display_dict['left']['frontright'][-1]
        self.left_force_back = self.force_display_dict['left']['backleft'][-1]+self.force_display_dict['left']['backright'][-1]
        self.left_leftright_ratio = self.left_force_right/(self.left_force_left+self.left_force_right+1e-12)
        self.left_fwdback_ratio = self.left_force_fwd/(self.left_force_fwd+self.left_force_back+1e-12)

        self.right_force_left = self.force_display_dict['right']['frontleft'][-1]+self.force_display_dict['right']['backleft'][-1]
        self.right_force_right = self.force_display_dict['right']['frontright'][-1]+self.force_display_dict['right']['backright'][-1]
        self.right_force_fwd = self.force_display_dict['right']['frontleft'][-1]+self.force_display_dict['right']['frontright'][-1]
        self.right_force_back = self.force_display_dict['right']['backleft'][-1]+self.force_display_dict['right']['backright'][-1]
        self.right_leftright_ratio = self.right_force_right/(self.right_force_left+self.right_force_right+1e-12)
        self.right_fwdback_ratio = self.right_force_fwd/(self.right_force_fwd+self.right_force_back+1e-12)


    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.update()
            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.LEFT_TREADMILL_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.RIGHT_TREADMILL_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.LEFT_PLOT_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.RIGHT_PLOT_RECT)        
        pygame.draw.lines(self.screen, self.PLOT_COLOR, False, 
                          self.left_force_display.transpose(), 6)
        pygame.draw.lines(self.screen, self.PLOT_COLOR, False, 
                          self.right_force_display.transpose(), 6)
        left_force_xpos = (self.LEFT_TREADMILL_XPOS
                           + self.TREADMILL_WIDTH*self.left_leftright_ratio)
        left_force_ypos = (self.TREADMILL_YPOS
                           + self.TREADMILL_HEIGHT*self.left_fwdback_ratio)
        right_force_xpos = (self.RIGHT_TREADMILL_XPOS
                           + self.TREADMILL_WIDTH*self.right_leftright_ratio)
        right_force_ypos = (self.TREADMILL_YPOS
                           + self.TREADMILL_HEIGHT*self.right_fwdback_ratio)
        if self.force_display_dict['left']['mean'][-1] > self.FORCE_THRESHOLD:
            self.draw_filled_aacircle(self.screen, self.FORCE_RAD, self.PLOT_COLOR,
                                      left_force_xpos, left_force_ypos)
        if self.force_display_dict['right']['mean'][-1] > self.FORCE_THRESHOLD:
            self.draw_filled_aacircle(self.screen, self.FORCE_RAD, self.PLOT_COLOR,
                                      right_force_xpos, right_force_ypos)

    def draw_filled_aacircle(self, screen, radius, color, xpos, ypos):
        pygame.gfxdraw.filled_circle(screen,
                                     int(xpos),
                                     int(ypos),
                                     int(radius),
                                     color)
        pygame.gfxdraw.aacircle(screen,
                                int(xpos),
                                int(ypos),
                                int(radius),
                                color)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    plotter = Plotter()
    plotter.run()
