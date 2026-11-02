"""Original CAD world axes and translated arena layout, no geometry synthesis."""
import math

SOURCE_MODEL_SHA = 'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
COLLISION_USDC_SHA = '9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'
COLLISION_NPZ_SHA = 'f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954'
COURSE_PROFILE = 'W35_to_original_full_RM70_arena208_v1'
ROUTE_X = (5.85, 9.15)
ROUTE_Y = 6.45
ROAD_X = (6.334789943753937, 8.741212671140003)
ROAD_WORLD_Y = (5.405026944202456, 7.495880414338017)
# Explicit new lesson boundary, not a change to any physical guard. The .35m
# end extensions are the original route goal radius. Cross extent remains
# inside the original CAD rough-road world-XY footprint, not a fabricated floor.
COURSE_X = (ROUTE_X[0] - .35, ROUTE_X[1] + .35)
COURSE_Y = ROAD_WORLD_Y


def layout_origins(n):
    if type(n) is not int or not 1 <= n <= 20000:
        raise ValueError('Bounded new source layout supports 1..20000, no state slicing')
    cols = math.ceil(math.sqrt(n)); rows = math.ceil(n / cols)
    # Same original build_layout.py translation-only 34m x 20m spacings.
    return [[(i // cols - (rows - 1) / 2) * 34.,
             (i % cols - (cols - 1) / 2) * 20., 0.] for i in range(n)]


def route_for_env(env_id):
    if type(env_id) is not int or env_id < 0:
        raise ValueError('Invalid original environment ID')
    reverse = bool(env_id % 2)
    return dict(route='rough_reverse' if reverse else 'rough_forward',
                spawn_ground_xy=(ROUTE_X[int(reverse)], ROUTE_Y),
                spawn_heading=math.pi if reverse else 0.,
                target_x=ROUTE_X[int(not reverse)])


def outside_course_xy(x, y):
    return x < COURSE_X[0] or x > COURSE_X[1] or y < COURSE_Y[0] or y > COURSE_Y[1]
