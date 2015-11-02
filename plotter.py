import pygame
from pygame.gfxdraw import aacircle
import owl
import struct
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
        self.SCREEN_HEIGHT = 600 # in pixels
        self.SCREEN_WIDTH = 600 # in pixels
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
        self.SERVER_IP = '192.168.1.230'

        # force display parameters
        self.FORCE_MAX = 5000 # in Newtons
        self.FORCE_THRESHOLD = 100 # in Newtons

    def set_variables(self):
        self.force_dict = {}
        self.force_dict['left'] = {'f_x': np.zeros(self.TIME_POINTS),
                                   'f_y': np.zeros(self.TIME_POINTS),
                                   'f_z': np.zeros(self.TIME_POINTS),
                                   'm_x': np.zeros(self.TIME_POINTS),
                                   'm_y': np.zeros(self.TIME_POINTS),
                                   'm_z': np.zeros(self.TIME_POINTS),
                                   'zero': np.zeros(self.TIME_POINTS)}
        self.force_dict['right'] = {'f_x': np.zeros(self.TIME_POINTS),
                                   'f_y': np.zeros(self.TIME_POINTS),
                                   'f_z': np.zeros(self.TIME_POINTS),
                                   'm_x': np.zeros(self.TIME_POINTS),
                                   'm_y': np.zeros(self.TIME_POINTS),
                                   'm_z': np.zeros(self.TIME_POINTS),
                                   'zero': np.zeros(self.TIME_POINTS)}
        self.force_display_dict = {}
        self.force_display_dict['left'] = {'f_x': np.zeros(self.TIME_POINTS),
                                           'f_y': np.zeros(self.TIME_POINTS),
                                           'f_z': np.zeros(self.TIME_POINTS),
                                           'm_x': np.zeros(self.TIME_POINTS),
                                           'm_y': np.zeros(self.TIME_POINTS),
                                           'm_z': np.zeros(self.TIME_POINTS),
                                           'zero': np.zeros(self.TIME_POINTS)}
        self.force_display_dict['right'] = {'f_x': np.zeros(self.TIME_POINTS),
                                           'f_y': np.zeros(self.TIME_POINTS),
                                           'f_z': np.zeros(self.TIME_POINTS),
                                           'm_x': np.zeros(self.TIME_POINTS),
                                           'm_y': np.zeros(self.TIME_POINTS),
                                           'm_z': np.zeros(self.TIME_POINTS),
                                           'zero': np.zeros(self.TIME_POINTS)}
        self.channel_dict = {}
        self.channel_dict['left'] = {'f_x': 32,
                                     'f_y': 33,
                                     'f_z': 34,
                                     'm_x': 35,
                                     'm_y': 36,
                                     'm_z': 37,
                                     'zero': 38}
        self.channel_dict['right'] = {'f_x': 39,
                                     'f_y': 40,
                                     'f_z': 41,
                                     'm_x': 42,
                                     'm_y': 43,
                                     'm_z': 44,
                                     'zero': 45}

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

        #################
        # OWL VARIABLES #
        #################

        # initialize OWL
        self.OWL = owl.Context()

        # connect to the server
        self.OWL.open(self.SERVER_IP)

        # initialize a session and enable data types
        self.OWL.initialize('event.markers=1 event.inputs=1 slave=0')

        # start streaming
        self.OWL.streaming(1)
        self.channels = []

    def get_channels(s):
        options = dict(map(lambda x: x.split('='), s.split()))
        if 'channelids' not in options:
            raise Exception('channelids entry not found!')
        return map(lambda x: int(x), filter(lambda x: len(x) > 0, options['channelids'].split(',')))

    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def update(self, inp):
        if len(self.channels) == 0:
            print('no channel information!')
        # each sample is 16-bits, so divide number of bytes by 2
        num_samples = len(inp.data) / 2
        num_points = num_samples / len(self.channels)
        samples = struct.unpack('%dh' % num_samples, inp.data)

        # self.channels[i % len(self.channels)] # this might be useful
        channel_id = 2

        self.force_dict['left']['f_z'] = np.roll(self.force_dict['left']['f_z'],
                                                 -num_points)
        self.force_dict['left']['f_z'][-num_points:] = samples[channel_id::len(self.channels)]

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

        # plot just the mean z forces on each treadmill
        self.left_force_display[1,:] = (self.PLOT_YPOS + self.PLOT_HEIGHT
                                        - self.force_display_dict['left']['f_z'][:]
                                          /self.FORCE_MAX*self.PLOT_HEIGHT)
        self.right_force_display[1,:] = (self.PLOT_YPOS + self.PLOT_HEIGHT
                                         - self.force_display_dict['right']['f_z'][:]
                                           /self.FORCE_MAX*self.PLOT_HEIGHT)

        # calculate realtime display parameters
        self.left_leftright_ratio = 0
        self.left_fwdback_ratio = 0

        self.right_leftright_ratio = 0
        self.right_fwdback_ratio = 0


    def run(self):
        while self.OWL.isOpen() and self.OWL.property('initialized'):
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()

            # poll for new data
            event = self.OWL.nextEvent()
            if not event: continue

            # parse channel data
            if len(self.channels) == 0:
                di = OWL.property('deviceinfo')
                for d in di:
                    if d.name == 'daq':
                        self.channels = self.get_channels(d.options)

            # parse new event
            if event.type_id == owl.Type.FRAME:
                pass
            if event.type_id == owl.Type.INPUT:
                for inp in event.data:
                    self.update(inp)
            elif event.type_id == owl.Type.ERROR:
                print('ERROR: %s' % event.data)
                break
            elif event.name == 'done':
                break
            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.LEFT_TREADMILL_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.RIGHT_TREADMILL_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.LEFT_PLOT_RECT)        
        pygame.draw.rect(self.screen, self.TREADMILL_COLOR, self.RIGHT_PLOT_RECT)        

        # plots the force trajectories
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
        self.OWL.done()
        self.OWL.close()
        sys.exit()

if __name__ == "__main__":
    plotter = Plotter()
    plotter.run()
