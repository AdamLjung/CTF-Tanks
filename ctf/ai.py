""" This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import defaultdict, deque

import pymunk
from pymunk import Vec2d
import gameobjects
import time
# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(1)   # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """ Compute the difference between two angles.
    """
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank, game_objects_list, tanks_list, space, currentmap):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1
        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.metalSearch = False
        self.update_grid_pos()

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """ Main decision function that gets called on every tick of the game.
        """
        self.maybe_shoot()
        next(self.move_cycle)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot.
        """

        startPos = (self.tank.body.position[0] - math.sin(self.tank.body.angle) * 0.4, self.tank.body.position[1] + math.cos(self.tank.body.angle) * 0.4)
        endPos = (self.tank.body.position[0] - math.sin(self.tank.body.angle) * 2, self.tank.body.position[1] + math.cos(self.tank.body.angle) * 2)
        ray = self.space.segment_query_first(startPos, endPos, 0, pymunk.ShapeFilter())

        if hasattr(ray, "shape"):

            if hasattr(ray.shape, "parent"):

                object = ray.shape.parent

                if isinstance(object, gameobjects.Box) and object.destructable and self.tank.cd == 0:

                    bullet = self.tank.shoot(self.space)
                    self.game_objects_list.append(bullet)
                elif isinstance(object, gameobjects.Tank) and self.tank.cd == 0:

                    bullet = self.tank.shoot(self.space)
                    self.game_objects_list.append(bullet)

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """
        while True:

            path = self.find_shortest_path(self.metalSearch)

            if len(path) < 1:

                yield
                continue
            if len(path) >= 2:

                path.popleft()

            nextCoord = path.popleft() + Vec2d(0.5, 0.5)
            yield

            tankPos = self.tank.body.position
            targetAngle = angle_between_vectors(tankPos, nextCoord)
            tankAngle = self.tank.body.angle
            while abs(periodic_difference_of_angles(targetAngle, tankAngle)) > MIN_ANGLE_DIF:
                self.tank.stop_moving()

                if -math.pi < (periodic_difference_of_angles(tankAngle, targetAngle)) < 0:

                    self.tank.turn_right()

                elif (periodic_difference_of_angles(tankAngle, targetAngle)) < -math.pi:

                    self.tank.turn_left()
                elif 0 < (periodic_difference_of_angles(tankAngle, targetAngle)) < math.pi:

                    self.tank.turn_left()
                else:
                    self.tank.turn_right()

                tankAngle = self.tank.body.angle
                tankPos = self.tank.body.position
                targetAngle = angle_between_vectors(tankPos, nextCoord)
                yield

            self.tank.stop_turning()
            distance = self.tank.body.position.get_distance(nextCoord)
            prevDist = 10000000

            while prevDist >= distance:

                self.tank.accelerate()
                prevDist = distance
                distance = self.tank.body.position.get_distance(nextCoord)
                yield

            self.update_grid_pos()

    def find_shortest_path(self, metalSearch):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """

        currentPos = self.grid_pos

        path = deque()
        shortest_path = []
        path.append((currentPos, []))
        target = self.get_target_tile()
        visited = []

        while (len(path) > 0):

            currentNode, currentPath = path.popleft()

            neighbours = self.get_tile_neighbors(currentNode, metalSearch)

            if currentNode == target:
                currentPath.append(currentNode)
                shortest_path = currentPath
                break

            for neighbour in neighbours:

                if neighbour.int_tuple not in visited:

                    path.append((neighbour, currentPath + [currentNode]))
                    visited.append(neighbour)

        if len(shortest_path) == 0:
            self.metalSearch = True
            shortest_path = self.find_shortest_path(self.metalSearch)

        return deque(shortest_path)

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """

        if self.flag is None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec, metalSearch):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """

        left = coord_vec + Vec2d(-1, 0)  # x-1
        right = coord_vec + Vec2d(1, 0)  # x+1
        up = coord_vec + Vec2d(0, -1)  # y-1
        down = coord_vec + Vec2d(0, 1)  # y+1
        neighbors = [up, down, left, right]  # Find the coordinates of the tiles' four neighbors
        noMetalBoxList = list(filter(self.filter_tile_neighbors, neighbors))

        if not metalSearch:

            return noMetalBoxList
        else:

            return list(filter(self.filter_tile_neighbors_with_metal_box, neighbors))

    def filter_tile_neighbors(self, coord):
        """ Used to filter the tile to check if it is a neighbor of the tank.
        """

        x = coord[0]
        y = coord[1]

        if (x >= 0 and self.max_x >= x) and (y >= 0 and self.max_y >= y):

            if self.currentmap.boxAt(x, y) == 0 or self.currentmap.boxAt(x, y) == 2:

                return True
        else:

            return False

    def filter_tile_neighbors_with_metal_box(self, coord):

        x = coord[0]
        y = coord[1]
        self.metalSearch = False
        if (x >= 0 and self.max_x >= x) and (y >= 0 and self.max_y >= y):

            if self.currentmap.boxAt(x, y) == 0 or self.currentmap.boxAt(x, y) == 2 or self.currentmap.boxAt(x, y) == 3:
                return True
        else:
            return False
