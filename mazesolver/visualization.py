import pygame
from pyailib.common import datastructs

class Visualization(object):
    """description of class"""
    # Define some colors
    _aqua   = (   0, 255, 255)
    _black  = (   0,   0,   0)
    _blue   = (   0,   0, 255)
    _green  = (   0, 255,   0)
    _red    = ( 255,   0,   0)
    _teal   = (   0, 128, 128)
    _white  = ( 255, 255, 255)
    _yellow = ( 255, 255,   0)

    @property
    def animatePath(self):
        return self._animatePath

    @animatePath.setter
    def animatePath(self, value):
        self._animatePath = value

    def __init__(self, world):
        self._world = world

        self._width = self._height = 30
        self._margin = 2

        self._stepCount = 0
        self._animatePath = False

        pygame.init()
        self._size = (world.width*(self._width+self._margin), world.height*(self._height+self._margin))
        self._screen = pygame.display.set_mode(self._size)

        pygame.display.set_caption('Robot Maze')
        self._clock = pygame.time.Clock()

    def setPath(self, path):
        self._path = path

    def setResults(self, results):
        self._results = results


    def update(self):
        for y in range(self._world.height):
            for x in range(self._world.width):
                color = self._white

                if not self.animatePath and (x, y) == self._path[self._stepCount]:
                    color = self._aqua

                cell = self._world.getCell(datastructs.Point2D(x, y))
                if cell.data == 'x':
                    color = self._black
                if cell.data == 'o':
                    color = self._yellow
                if cell.data == '?':
                    color = self._green

                if self.animatePath and (x, y) == self._path[self._stepCount]:
                    color = self._aqua

                topX = x*(self._width+self._margin)+self._margin
                topY = y*(self._height+self._margin)+self._margin
                pygame.draw.rect(self._screen, 
                                color, 
                                [topX,
                                topY, 
                                self._width, self._height])

                if self._results.has_key((x, y)):
                    result = self._results[(x, y)]
                    fontObj1 = pygame.font.SysFont('arial', 10)
                    textSurfaceObj1 = fontObj1.render('f='+result['f'], True, self._black)
                    textRectObj1 = textSurfaceObj1.get_rect()
                    textRectObj1.center = (topX+15,topY+5)
                    self._screen.blit(textSurfaceObj1, textRectObj1)

                    fontObj2 = pygame.font.SysFont('arial', 10)
                    textSurfaceObj2 = fontObj2.render('g='+result['g'], True, self._black)
                    textRectObj2 = textSurfaceObj2.get_rect()
                    textRectObj2.center = (topX+15,topY+15)
                    self._screen.blit(textSurfaceObj2, textRectObj2)

                    fontObj3 = pygame.font.SysFont('arial', 10)
                    textSurfaceObj3 = fontObj3.render('h='+result['h'], True, self._black)
                    textRectObj3 = textSurfaceObj3.get_rect()
                    textRectObj3.center = (topX+15,topY+25)
                    self._screen.blit(textSurfaceObj3, textRectObj3)

        self._clock.tick(10)  # 60 frames per second

        self._stepCount = self._stepCount + 1
        if self._stepCount >= len(self._path):
            self._stepCount = 0

        pygame.display.update()
