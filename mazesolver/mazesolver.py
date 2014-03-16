import os, sys, getopt, ast, random, pygame

projects_folder = os.path.abspath(os.path.dirname(__file__) + '/../')
if projects_folder not in sys.path:
    sys.path.append(projects_folder)

from pyailib import planner
from pyailib.core import *
from pyailib.learning import qlearning

from visualization import Visualization

import search
import learning



class Cell(environment.Cell):
    """."""
    _colorMap = {'wall': 'black',
                 'goal': 'green',
                 'floor': 'white',
                 'player': 'blue'}

    _imgMap = {}

    _tileMap = {'x': _colorMap['wall'],
                ' ': _colorMap['floor'],
                '?': _colorMap['goal'],
                '@': _colorMap['player']}

    def isOccupied(self):
        return self._data == 'x'



def usage():
    return 'Robot Maze\n\n\
Usage:\n\
    robot_maze.py astar --maze=<file> [--inpath=<file> | --outpath=<file>]\n\
    robot_maze.py qlearn --maze=<file> [--nepisode=<int> | --alpha=<float> | --gamma=<float>]\n\
    robot_maze.py -h | --help\n\
\n\
Options:\n\
    -h --help                   Show this help message\n\
    -m <file> --maze=<file>     Specify maze map from <file>\n\
    -i <file> --inpath=<file>   Load path from <file>\n\
    -o <file> --outpath=<file>  Save path to <file>\n\
    -e <int>  --nepidode=<int>  Number of episodes to run qlearning for\n\
    -a <int>  --alpha=<float>   Learning rate in [0, 1]\n\
    -g <int>  --gamma=<float>   Discount rate in [0, 1]\n'

def parseArgv(argv):
    maze = ''
    inpath = ''
    outpath = ''
    qlconfig = {"episodes": 300, "alpha": 0.5, "gamma": 0.9}

    if (len(argv) > 1):
        command = argv[0]
        argv = argv[1:]

    try:
        opts, args = getopt.getopt(argv,"hm:i:o:e:a:g:",["help","maze=","inpath=","outpath=","nepisode=","alpha=","gamma="])
    except getopt.GetoptError:
        print usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print usage()
            sys.exit(0)
        elif opt in ('-m', '--maze'):
            maze = arg
        elif opt in ('-i', '--inpath'):
            inpath = arg
        elif opt in ('-o', '--outpath'):
            outpath = arg
        elif opt in ('-e', '--nepisode'):
            qlconfig["episodes"] = arg
        elif opt in ('-a', '--alpha'):
            qlconfig["alpha"] = arg
        elif opt in ('-g', '--gamma'):
            qlconfig["gamma"] = arg
    if not maze:
        print usage()
        sys.exit(2)

    return command, maze, inpath, outpath, qlconfig

def loadPath(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    path = []
    with open(filename) as f:
        for line in f:
            path.extend(ast.literal_eval(line.strip()))
    return path

def getRandomLocation(problem):
        while True:
            loc = problem._world.randomLocation()
            state = problem.stateFromLocation(loc)
            if not problem.isTerminal(state):
                break
        return loc


def main(argv):
    cmd, mazefile, inpathfile, outpathfile, qlconfig = parseArgv(argv)

    world = environment.GridWorld(Cell, None, None, mazefile)

    if (cmd == 'astar'):
        # TOTO write a search agent to handle all this
        if not inpathfile:
            problem = search.ProblemImpl(world);
            s = planner.search.AStar(problem)
            s.search()
            path = s.getPath()
            results = s.getResults()
            if outpathfile:
                path = s.savePath(outpathfile, path)
        else:
            path = loadPath(inpathfile)
            results = {}

        vi = Visualization(world)
        vi.setPath(path)
        vi.setResults(results)
        vi.animatePath = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            vi.update()

    elif (cmd == 'qlearn'):
        problem = learning.RLProblemImpl(world)

        actions = problem.actions(13)

        policy = qlearning.EpsilonGreedyPolicy(0.05)
        ai = qlearning.QLearn(problem, policy, qlconfig["alpha"], qlconfig["gamma"])

        # place agent in random position
        npc = learning.LearnAgent('@', getRandomLocation(problem), random.randrange(4), ai)
        world.addAgent(npc)

        steps = 150

        for x in range(qlconfig["episodes"]):
            for step in range(steps):
                world.update()
                if world.isDone() == True:
                    break
            loc = getRandomLocation(problem)
            npc.setLocation(loc)

        if True:
            print "Exploit:\n"
            ai.trace = True
            policy.epsilon = 0.0
            for x in range(2):
                print "Episode= %d" % (x+1)
                for step in range(steps):
                    world.update()
                    if world.isDone() == True:
                        break;
                print "Number of steps= %d" % (step+1)
                loc = getRandomLocation(problem)
                npc.setLocation(loc)

        npc._ai.viResults()


        


if __name__ == "__main__":
       main(sys.argv[1:]);