# based on https://www.scratchapixel.com/lessons/3d-basic-rendering/rendering-3d-scene-overview/visibility-problem

import pygame
import math

# goal: project 3 points onto screen space and rasterize into pygame

pygame.init()

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
screen_to_eye = 1

window = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
pygame.display.set_caption("Simple vertex renderer")

clock = pygame.time.Clock()
FPS = 60

PINK = '#F72585'
PURPLE = '#7209B7'
DOT_COLOR = '#FFFFFF'
DOT_RADIUS = 5

axis_of_rotation = 15  # line z = 15

cube_coordinates = [[-5, -5, 10], [-5, -5, 20], [-5, 5, 10], [-5, 5, 20],
                    [5, -5, 10], [5, -5, 20], [5, 5, 10], [5, 5, 20]]
cube_polar_coordinates = []


def project_point(point: list):
    projected_coords = [point[0] / point[2], point[1] / point[2]]  # perspective divide
    return projected_coords


def project_list(point_list):
    output_coords = point_list.copy()
    for i in range(len(point_list)):
        output_coords[i] = project_point(point_list[i])
    return output_coords


def normalize_point(projected_point):
    output_point = [0, 0]
    output_point[0] = (projected_point[0] + 1) / 2
    output_point[1] = (1 - projected_point[1]) / 2
    return output_point


def normalize_list(projected_point_list):
    normalized_point_list = projected_point_list.copy()
    for i in range(len(projected_point_list)):
        normalized_point_list[i] = normalize_point(projected_point_list[i])
    return normalized_point_list


def rasterize_point(normalized_point):
    rasterized_point = normalized_point
    # find x in raster space
    rasterized_point[0] = int(normalized_point[0] * SCREEN_WIDTH)
    if rasterized_point[0] == SCREEN_WIDTH:
        rasterized_point[0] -= 1
    # find y in raster space
    rasterized_point[1] = int(normalized_point[1] * SCREEN_HEIGHT)
    if rasterized_point[1] == SCREEN_HEIGHT:
        rasterized_point[1] -= 1
    return rasterized_point


def rasterize_list(normalized_point_list):
    rasterized_point_list = normalized_point_list.copy()
    for i in range(len(normalized_point_list)):
        rasterized_point_list[i] = rasterize_point(normalized_point_list[i])
    return rasterized_point_list


def draw_cube_edges(raster_space_coordinates, window, color, funky_mode, funk_level):
    point_combinations = raster_space_coordinates
    if funky_mode:
        point_combinations = point_combinations[0::funk_level]  # can be fun to get funky line combinations
    for i in range(len(point_combinations)):
        pygame.draw.line(window, color, point_combinations[i][0], point_combinations[i][1], 2)


def render_points(vertices, window, edges, edge_list):
    rasterized_vertices = rasterize_list(normalize_list(project_list(vertices)))
    cube_edges = [[rasterized_vertices[a], rasterized_vertices[b]] for [a, b] in edge_list]
    # print(f'raster space coords: {rasterized_vertices}')
    for i in range(len(rasterized_vertices)):
        pygame.draw.circle(window, DOT_COLOR, rasterized_vertices[i], DOT_RADIUS)
    if edges:
        draw_cube_edges(cube_edges, window, DOT_COLOR, funk_mode, funk_level)


# #tests
# # print(f'projected point: {project_point([-1, 2, 10])}')
# projection_test_point = [-1, 2, 10]
# assert project_point(projection_test_point) == [-0.1, 0.2]
#
# test_list = [[-1, 2, 10], [-1, 2, 10], [-1, 2, 10]]
# projection_test = project_list(test_list)
# assert projection_test == [[-0.1, 0.2], [-0.1, 0.2], [-0.1, 0.2]]
#
# normalize_test_point = [-0.1, 0.2]
# # print(f' normalization test: {normalize_point(normalize_test_point)}')
# assert normalize_point(normalize_test_point) == [0.45, 0.4]
#
# normalize_test_list = [[-0.1, 0.2], [-0.1, 0.2], [-0.1, 0.2]]
# normalized_output_list = normalize_list(normalize_test_list)
# # print(normalized_output_list)
# for i in range(len(normalized_output_list)):
#     assert 0 < normalized_output_list[i][0] < 1 and 0 < normalized_output_list[i][1] < 1
#
# rasterize_test_list = [[0.45, 0.4], [0.45, 0.4], [0.45, 0.4]]
# rasterized_list = rasterize_list(rasterize_test_list)
# for i in range(len(rasterize_test_list)):
#     assert 0 <= rasterized_list[i][0] < SCREEN_WIDTH and 0 <= rasterized_list[i][1] < SCREEN_HEIGHT


def find_center(point_list):
    num_points = len(point_list)
    mean_x = sum([point_list[i][0] for i in range(len(point_list))]) / num_points
    mean_y = sum([point_list[i][1] for i in range(len(point_list))]) / num_points
    mean_z = sum([point_list[i][2] for i in range(len(point_list))]) / num_points
    return [mean_x, mean_y, mean_z]


# https://www.petercollingridge.co.uk/tutorials/3d/pygame/rotation/ oct 10, 2021
def rotateX(points, center, radians):
    for i in range(len(points)):
        z = points[i][2] - center[2]
        y = points[i][1] - center[1]
        x = points[i][0]
        d = math.hypot(y, z)
        theta = math.atan2(y, z) + radians
        points[i][2] = center[2] + d * math.cos(theta)
        points[i][1] = center[1] + d * math.sin(theta)
    return points


def rotateY(points, center, radians):
    for i in range(len(points)):
        x = points[i][0] - center[0]
        z = points[i][2] - center[2]
        # y = points[i][1]
        d = math.hypot(x, z)
        theta = math.atan2(x, z) + radians
        points[i][2] = center[2] + d * math.cos(theta)
        points[i][0] = center[0] + d * math.sin(theta)
    return points


def rotateZ(points, center, radians):
    for i in range(len(points)):
        x = points[i][0] - center[0]
        y = points[i][1] - center[1]
        z = points[i][2]
        d = math.hypot(y, x)
        theta = math.atan2(y, x) + radians
        points[i][0] = center[0] + d * math.cos(theta)
        points[i][1] = center[1] + d * math.sin(theta)
    return points


# #weird
# def rotateAll(axis, points, theta):
#     rotateFunction = 'rotate' + axis
#     return rotateFunction


cube_center = find_center(cube_coordinates)

good_edges = [[0, 1], [0, 2], [0, 4], [1, 3], [1, 5], [2, 3], [2, 6], [3, 7], [4, 5], [4, 6], [5, 7], [6, 7]]
all_edges = [[i, j] for i in range(len(cube_coordinates)) for j in range(len(cube_coordinates))]
all_surface_edges = all_edges.copy()
all_surface_edges.remove([2, 5])
all_surface_edges.remove([5, 2])

all_surface_edges.remove([0, 7])
all_surface_edges.remove([7, 0])

all_surface_edges.remove([3, 4])
all_surface_edges.remove([4, 3])

all_surface_edges.remove([1, 6])
all_surface_edges.remove([6, 1])

active_edges = [good_edges, all_edges, all_surface_edges, []]
selected_edge = 0

t_x = False  # "turning around the x axis"
t_y = False
t_z = False

t_mx = False  # "turning negatively around the x axis"
t_my = False
t_mz = False

static_demo = False
funk_mode = False
funk_level = 1
autofunk = False
play = True
run = True
while run:
    clock.tick(FPS)

    if static_demo:
        cube_coordinates = rotateX(cube_coordinates, cube_center, 0.01)
        cube_coordinates = rotateY(cube_coordinates, cube_center, 0.01)
        # cube_coords = rotateZ(cube_coords, cube_center, 0.01)
    if autofunk and pygame.time.get_ticks() % FPS == 0:
        funk_level = (funk_level + 1) % len(cube_coordinates)
        if funk_level == 0:
            funk_level = 1


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                t_x = True
                t_mx = False
            if event.key == pygame.K_w:
                t_x = False
                t_mx = True
            if event.key == pygame.K_a:
                t_y = True
                t_my = False
            if event.key == pygame.K_d:
                t_y = False
                t_my = True
            if event.key == pygame.K_q:
                t_z = True
                t_mz = False
            if event.key == pygame.K_e:
                t_z = False
                t_mz = True
            if event.key == pygame.K_f:
                funk_mode = True
                funk_level = (funk_level + 1) % 12
                if funk_level == 0:
                    funk_level = 1
                    print(f'Gotta have that funk (and not divide by 0)')
            if event.key == pygame.K_p:
                autofunk = not autofunk
                funk_mode = not funk_mode
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                t_x = False
            if event.key == pygame.K_w:
                t_mx = False
            if event.key == pygame.K_a:
                t_y = False
            if event.key == pygame.K_d:
                t_my = False
            if event.key == pygame.K_q:
                t_z = False
            if event.key == pygame.K_e:
                t_mz = False
            if event.key == pygame.K_SPACE:
                static_demo = not static_demo
            if event.key == pygame.K_t:
                selected_edge = (selected_edge + 1) % len(active_edges)


    if play:
        # TODO: Add handling for t_x and t_mx type state variables. Each step should rotate the cube along some axis if turn var is true
        if t_x:
            rotateX(cube_coordinates, cube_center, 0.03)
        if t_mx:
            rotateX(cube_coordinates, cube_center, -0.03)
        if t_y:
            rotateY(cube_coordinates, cube_center, 0.03)
        if t_my:
            rotateY(cube_coordinates, cube_center, -0.03)
        if t_z:
            rotateZ(cube_coordinates, cube_center, 0.03)
        if t_mz:
            rotateZ(cube_coordinates, cube_center, -0.03)

        window.fill(PURPLE)
        render_points(cube_coordinates, window, True, active_edges[selected_edge])

    pygame.display.update()
