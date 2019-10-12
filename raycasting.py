import pygame
import math
import random

pygame.init()

WIN_WIDTH = 1000
WIN_HEIGHT = 600
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
THE_BLUE = (130, 250, 226)
GREY = (100, 100, 100)


class Vec2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __truediv__(self, other):
        return Vec2(self.x / other, self.y / other)

    def __floordiv__(self, other):
        return Vec2(self.x // other, self.y // other)

    def __sub__(self, point):
        return Vec2(self.x - point.x, self.y - point.y)

    def __add__(self, point):
        return Vec2(self.x + point.x, self.y + point.y)

    def __mul__(self, cons):
        return Vec2(self.x * cons, self.y * cons)

    def dot(self, point):
        return self.x * point.x + self.y * point.y

    def distance(self, point):
        return math.sqrt((point.x - self.x) ** 2 + (point.y - self.y) ** 2)

    def __len__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def unit(self):
        length = len(self)
        return Vec2(self.x/length, self.y/length)

    def __str__(self):
        return str(self.x) + " ," + str(self.y)

    def slope(self, other):
        return (other.y - self.y) / (other.x - self.x + 0.00000001)

    def y_int(self, slope):
        return self.y - slope * self.x

    @staticmethod
    def poi(a1, a2, b1, b2):
        m1 = a2.slope(a1)
        m2 = b2.slope(b1)
        d1 = a1.y_int(m1)
        d2 = b1.y_int(m2)

        x = (d2 - d1) / (m1 - m2)
        y = m1 * x + d1

        return Vec2(x, y)


class Ray:
    def __init__(self, angle, length, wall_hit):
        self.a = angle
        self.length = length
        self.wall_hit = wall_hit

    def __str__(self):
        return str(self.a) + ", " + str(self.length) + ", " + str(self.wall_hit)


class Rect(Vec2):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_points(self):
        return [[self.x, self.y], [self.x, self.y + self.h], [self.x + self.w, self.y + self.h],
                [self.x + self.w, self.y]]

    def get_pos(self):
        return [self.x, self.y]

    def rect(self):
        xtra = 1  # for proportionately increasing size of rectangle
        return self.x * xtra, self.y * xtra, self.w * xtra, self.h * xtra

    def draw(self):
        pygame.draw.rect(WIN, WHITE, list(map(int, self.rect())))


class Polygon:
    def __init__(self):
        self.point_list = []
        self.tile_set = []
        self.tile_map = None

    # recursive algorithm to group all adjacent walls from tile map
    def find_adjacent_walls(self, x, y, side):
        self.tile_map.set_tile(x, y, TileMap.O)
        self.tile_set.append([x, y])

        if len(self.point_list) > 1:
            pygame.draw.lines(WIN, WHITE, False, list(map(lambda a: (a[0]*20, a[1]*20), self.point_list)))
        pygame.display.update()
        # pygame.time.delay(300)

        self.point_list.append(Polygon.get_point(x, y, side, 0))
        nx, ny = Polygon.get_next_tile(x, y, side, 1)
        if self.tile_map.get_tile(nx, ny, True) == TileMap.X:
            Polygon.find_adjacent_walls(self, nx, ny, (side+3) % 4)

        self.point_list.append(Polygon.get_point(x, y, side, 1))
        nx, ny = Polygon.get_next_tile(x, y, side, 2)
        if self.tile_map.get_tile(nx, ny, True) == TileMap.X:
            Polygon.find_adjacent_walls(self, nx, ny, side)

        self.point_list.append(Polygon.get_point(x, y, side, 2))
        nx, ny = Polygon.get_next_tile(x, y, side, 3)
        if self.tile_map.get_tile(nx, ny, True) == TileMap.X:
            Polygon.find_adjacent_walls(self, nx, ny, (side+1) % 4)

        self.point_list.append(Polygon.get_point(x, y, side, 3))

    # remove unnecessary points (duplicates and multiple point forming linear line)
    def optimize(self):
        i = 0
        for n in range(len(self.point_list)-1):
            a = self.point_list[i-1]
            b = self.point_list[i]
            c = self.point_list[i+1]
            if a[0] == b[0] and b[0] == c[0]:
                del self.point_list[i]
            elif a[1] == b[1] and b[1] == c[1]:
                del self.point_list[i]
            elif a[1] == b[1] and a[0] == b[0]:
                del self.point_list[i]
            else:
                i += 1

    # get point coordinate given a side you are coming from (0,1,2,3 clockwise staring from top)
    #   and the point you want to (0,1,2,3 clockwise from left relative to side)
    @staticmethod
    def get_point(x, y, side, direction):
        if (side + direction) % 4 == 3:
            return x, y
        elif (side + direction) % 4 == 0:
            return x + 1, y
        elif (side + direction) % 4 == 1:
            return x + 1, y + 1
        elif (side + direction) % 4 == 2:
            return x, y + 1

    # get next coordinate given a side you are coming from (0,1,2,3 clockwise staring from top)
    #   and the side you want to go to (0,1,2,3 clockwise relative to side (representing left, forward, right, back))
    @staticmethod
    def get_next_tile(x, y, side, direction):
        if (side + direction) % 4 == 3:
            return x - 1, y
        elif (side + direction) % 4 == 0:
            return x, y - 1
        elif (side + direction) % 4 == 1:
            return x + 1, y
        elif (side + direction) % 4 == 2:
            return x, y + 1


class TileMap:
    X = "wall"
    O = "none"

    def __init__(self):
        X = "wall"
        O = "none"
        self.X = "wall"
        self.O = "none"
        self.map = [[X, X, X, X, X, X, X, X],
                    [X, O, X, O, O, O, O, X],
                    [X, O, O, O, O, X, O, X],
                    [X, O, O, O, O, X, O, X],
                    [X, O, O, O, O, O, O, X],
                    [X, O, O, O, X, X, X, X],
                    [X, X, O, O, O, O, O, X],
                    [X, X, X, X, X, X, X, X]]
        self.x_len = len(self.map[0])
        self.y_len = len(self.map)
        self.tiles = []
        self.polygons = []
        self.generate_poly()

    def get_tile(self, x, y, safe=False):
        if safe:
            if y < 0 or x < 0 or y > self.y_len-1 or x > self.x_len-1:
                return -1
        return self.map[y][x]

    def set_tile(self, x, y, var):
        self.map[y][x] = var

    # convert tiles into polygons for efficient rendering and ray casting
    def generate_poly(self):
        xy = self.find_wall()
        while xy != -1:
            pol = Polygon()
            pol.tile_map = self
            pol.find_adjacent_walls(xy[0], xy[1], 0)
            pol.optimize()
            self.polygons.append(pol)
            xy = self.find_wall()

    # find next wall
    def find_wall(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.get_tile(x, y) == self.X:
                    return x, y
        return -1


class Player(Vec2):
    def __init__(self, x, y, a):
        self.x = x
        self.y = y
        self.a = a
        self.FOV = 90

    # drawing point on tile map
    def draw(self):
        xtra = 20
        pygame.draw.circle(WIN, WHITE, (int(self.x * xtra), int(self.y * xtra)), 2)

    # create rays from player to nearest walls (distance, angle)
    def get_ray_cast(self, tile_map):
        dis_list = []
        for a in range(self.FOV*3):  # 3 rays for every angle of the player's FOV
            a /= 3
            temp_dis_list = []
            for pol in tile_map.polygons:
                for l in range(len(pol.point_list)):
                    # if ray collides with line, create ray (distance from player to POI or both lines)
                    if finite_collision([self.x, self.y], [self.x + 100 * math.cos(math.radians(self.a + a)),
                                                           self.y + 100 * math.sin(math.radians(self.a + a))],
                                        pol.point_list[l], pol.point_list[l-1]):
                        temp_dis_list.append(
                            Ray(a,
                                self.distance(Vec2.poi(
                                    self, (Vec2(self.x + 100 * math.cos(math.radians(self.a + a)),
                                                       self.y + 100 * math.sin(math.radians(self.a + a)))),
                                    Vec2(pol.point_list[l][0],pol.point_list[l][1]),
                                    Vec2(pol.point_list[l-1][0],pol.point_list[l-1][1]))),
                                [pol.point_list[l], pol.point_list[l-1]]))
            if temp_dis_list:
                shortest_ray = None
                for ray in temp_dis_list:
                    if shortest_ray is None:
                        shortest_ray = ray
                    elif ray.length < shortest_ray.length:
                        shortest_ray = ray
                dis_list.append(shortest_ray)
                # if len(dis_list) > 2:
                #     if dis_list[-1].wall_hit == dis_list[-2].wall_hit and \
                #             dis_list[-2].wall_hit == dis_list[-3].wall_hit:
                #         del dis_list[-2]

            else:
                dis_list.append(Ray(a, 10, -1))
        return dis_list


# converting rays into polygons to be drawn on the screen
def render_ray_cast():
    # get rays
    ray_cast = player.get_ray_cast(tile_map)
    for ray in range(len(ray_cast)-1):
        # create polygon between current ray and next ray
        depth = ray_cast[ray].length
        depth2 = ray_cast[ray+1].length
        i = ray_cast[ray].a
        i2 = ray_cast[ray+1].a
        x = -depth * math.cos(math.radians(i+45))
        z = depth * math.sin(math.radians(i+45))
        nextx = -depth2 * math.cos(math.radians((i2)+45))
        nextz = depth2 * math.sin(math.radians((i2)+45))
        pygame.draw.polygon(WIN, darken(depth),
                            [convert(x, -2, z), convert(nextx, -2, nextz), convert(nextx, 2, nextz), convert(x, 2, z)])
    return ray_cast


# convert 3d point to 2d point
def convert(x, y, z, view_settings = (500, 300, WIN_WIDTH/2, 100), zChange=0):
    # view_settings = (screen center (x and y), zoom (x and y)
    # z_change = depth adjustment
    return int((x / (z + zChange)) * view_settings[2] + view_settings[0]), int(
        (y / (z + zChange)) * view_settings[3] + view_settings[1])


# collision between two finite lines
def finite_collision(a1, a2, b1, b2):
    signa1 = ((a1[0] - b1[0]) * (b2[1] - b1[1]) - (a1[1] - b1[1]) * (b2[0] - b1[0]))
    signa2 = ((a2[0] - b1[0]) * (b2[1] - b1[1]) - (a2[1] - b1[1]) * (b2[0] - b1[0]))
    signb1 = ((b1[0] - a1[0]) * (a2[1] - a1[1]) - (b1[1] - a1[1]) * (a2[0] - a1[0]))
    signb2 = ((b2[0] - a1[0]) * (a2[1] - a1[1]) - (b2[1] - a1[1]) * (a2[0] - a1[0]))

    return signa1 * signa2 < 0 and signb1 * signb2 < 0


# color adjustment dependant on depth
def darken(depth):
    c = int(255 - depth * 50)
    if c < 0:
        return BLACK
    return [c, c, c]


def redraw():
    WIN.fill(BLACK)

    ray_cast = render_ray_cast()

    player.draw()

    # draw tile map
    for pol in tile_map.polygons:
        pygame.draw.polygon(WIN, RED, list(map(lambda a: [a[0]*20, a[1]*20], pol.point_list)))

    # draw rays from player
    for ray in range(len(ray_cast)):
        depth = ray_cast[ray].length
        a = ray_cast[ray].a
        pygame.draw.line(WIN, YELLOW, (player.x*20, player.y*20), ((player.x + depth * math.cos(math.radians(player.a+a)))*20,
                                                                 (player.y + depth * math.sin(math.radians(player.a+a)))*20))

    pygame.display.update()


player = Player(3.5, 3.5, 90)
tile_map = TileMap()

inPlay = True
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
pygame.mouse.set_pos(300, 300)

mousepos = pygame.mouse.get_pos()

while inPlay:
    redraw()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            inPlay = False
        if event.type == pygame.MOUSEMOTION:
            player.a += (pygame.mouse.get_pos()[0] - 300) / 4
            pygame.mouse.set_pos(300, 300)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                inPlay = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        player.x -= 0.02 * math.cos(math.radians(player.a + 90 + player.FOV / 2))
        player.y -= 0.02 * math.sin(math.radians(player.a + 90 + player.FOV / 2))
    if keys[pygame.K_d]:
        player.x += 0.02 * math.cos(math.radians(player.a + 90 + player.FOV / 2))
        player.y += 0.02 * math.sin(math.radians(player.a + 90 + player.FOV / 2))
    if keys[pygame.K_w]:
        player.x += 0.02 * math.cos(math.radians(player.a + player.FOV/2))
        player.y += 0.02 * math.sin(math.radians(player.a + player.FOV/2))
    if keys[pygame.K_s]:
        player.x -= 0.02 * math.cos(math.radians(player.a + player.FOV/2))
        player.y -= 0.02 * math.sin(math.radians(player.a + player.FOV/2))

pygame.quit()
