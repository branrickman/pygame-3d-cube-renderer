# based on https://www.scratchapixel.com/lessons/3d-basic-rendering/rendering-3d-scene-overview/visibility-problem

import pygame
import math

# goal: project 3 points onto screen space and rasterize into pygame

pygame.init()

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800
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

cube_coords = [[-5, -5, 10], [-5, -5, 20], [-5, 5, 10], [-5, 5, 20],
               [5, -5, 10], [5, -5, 20], [5, 5, 10], [5, 5, 20]]
cube_polar_coords = []
cube_center = [0, 0, 0]


def project_point(point: list):
    projected_coords = [point[0] / point[2], point[1] / point[2]]  # perspective divide
    return projected_coords


def project_list(point_list):
    output_coords = point_list.copy()
    for i in range(len(point_list)):
        print(i)
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


def draw_cube_edges(raster_space_coordinates, window, color):
    # point_combinations = [[raster_space_coordinates[i], raster_space_coordinates[j]] for i in range(len(raster_space_coordinates)) for j in range(len(raster_space_coordinates))]
    point_combinations = raster_space_coordinates
    # print(point_combinations)
    # if True:
    #     point_combinations = point_combinations[0::2]  # can be fun to get funky line combinations
    for i in range(len(point_combinations)):
        pygame.draw.line(window, color, point_combinations[i][0], point_combinations[i][1], 2)


def render_points(vertices, window, edges):
    rasterized_vertices = rasterize_list(normalize_list(project_list(vertices)))
    cube_edges = [[rasterized_vertices[a], rasterized_vertices[b]] for [a, b] in good_edges]
    # print(f'raster space coords: {rasterized_vertices}')
    for i in range(len(rasterized_vertices)):
        pygame.draw.circle(window, DOT_COLOR, rasterized_vertices[i], DOT_RADIUS)
    if edges:
        draw_cube_edges(cube_edges, window, DOT_COLOR)


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
    print(f'Mean: ({mean_x}, {mean_y}, {mean_z})')
    return [mean_x, mean_y, mean_z]


def convert_cartesian_point_to_polar2d3d(c_point,
                                         center):  # gives polar coordinate of a point. center = center of rotation
    # e.g. rotating a 3d point around the z axis
    p_point = [math.atan2(c_point[1] - center[1], c_point[0] - center[0]),
               math.hypot(c_point[1] - center[1], c_point[0] - center[0]), c_point[2]]
    return p_point


def convert_polar_point_to_cartesian2d3d(p_point, center):
    c_point = [center[0] + p_point[1] * math.cos(p_point[0]), \
               center[1] + p_point[0] * math.sin(p_point[0]), p_point[2]]
    return c_point


def rotateZ(pure_points, center, radians):
    for i in range(len(pure_points)):
        polar = convert_cartesian_point_to_polar2d3d(pure_points[i], center)
        polar[1] += radians
        cartesian = convert_polar_point_to_cartesian2d3d(polar, center)
        pure_points[i] = cartesian
    return pure_points


cube_center = find_center(cube_coords)

good_edges = [[0, 1], [0, 2], [0, 4], [1, 3], [1, 5], [2, 3], [2, 6], [3, 7], [4, 5], [4, 6], [5, 7], [6, 7]]

print(f'cube coords: {cube_coords}')
run = True
while run:
    clock.tick(FPS)

    #rotateZ(cube_coords, cube_center, 0.1)
    #print(f'cube coords: {cube_coords}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


    window.fill(PURPLE)
    render_points(cube_coords, window, edges=True)

    run += 1
    pygame.display.update()
