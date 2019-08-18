import sys
import glob
import os
import time
import random
import numpy as np
import cv2

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

actor_list = []
IMG_WIDTH = 640
IMG_HEIGHT = 480


def process_image(image):
    """
    Affiche l'image issue du capteur
    :param image: image du capteur
    :return: valeurs normalisées
    """
    i = np.array(image.raw_data)
    print(i.shape)
    i2 = i.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0


try:
    # Préparation de Carla
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # Préparation de la voiture
    bp = blueprint_library.filter("model3")[0]
    print(bp)

    # Ajout de la voiture
    spawn_point = random.choice(world.get_map().get_spawn_points())
    vehicle = world.spawn_actor(bp, spawn_point)
    # vehicle.set_autopilot(True)
    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
    actor_list.append(vehicle)

    # Ajout de la caméra
    cam_bp = blueprint_library.find("sensor.camera.rgb")
    cam_bp.set_attribute("image_size_x", f"{IMG_WIDTH}")
    cam_bp.set_attribute("image_size_y", f"{IMG_HEIGHT}")
    cam_bp.set_attribute("fov", "100")
    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))
    sensor = world.spawn_actor(cam_bp, spawn_point, attach_to=vehicle)
    actor_list.append(sensor)

    # Récupération des informations du capteur
    sensor.listen(lambda data: process_image(data))

    time.sleep(20)  # Pour empêcher la destruction immédiate du vehicule

finally:
    for actor in actor_list:
        actor.destroy()
    print('All actors have been destroyed.')
