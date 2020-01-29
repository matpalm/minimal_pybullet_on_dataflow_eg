import pybullet_data
import pybullet as p
import numpy as np
import random
from PIL import Image
import logging
from google.cloud import storage
import io
import re

# absolutely minimal stateless example of rendering


def render(render_config):
    seed, render_output_path = render_config

    seed = int(seed)
    random.seed(seed)
    np.random.seed(seed)

    # initialise pybullet
    p.connect(p.DIRECT)

    # load checkered floor
    p.loadURDF(pybullet_data.getDataPath() + "/plane100.urdf",
               0, 0, 0,     # position
               0, 0, 0, 1)  # orientation

    # load a random object and let it drop to ground
    urdf_id = random.randint(0, 10)
    logging.info("urdf_id %d" % urdf_id)
    block_position = (0, 0, 0.1)
    block_angle = random.random() * np.pi
    block_orient = p.getQuaternionFromEuler([0, 0, block_angle])
    urdf_path = "/random_urdfs/%03d/%03d.urdf" % (urdf_id, urdf_id)
    p.loadURDF(pybullet_data.getDataPath() + urdf_path,
               *block_position, *block_orient)
    for _ in range(100):
        p.stepSimulation()

    # render a view of scene
    proj_matrix = p.computeProjectionMatrixFOV(fov=50,
                                               aspect=1.0,
                                               nearVal=0.1,
                                               farVal=100.0)
    view_matrix = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=(0, 0, 0),
        distance=1,
        yaw=10,
        pitch=-30,
        roll=0,
        upAxisIndex=2)
    rendering = p.getCameraImage(height=320,
                                 width=320,
                                 viewMatrix=view_matrix,
                                 projectionMatrix=proj_matrix,
                                 shadow=1)
    _width, _height, rgb_array, _depth, _segmentation = rendering

    # teardown pybullet environment
    p.disconnect()

    # convert RGB to PIL image (dropping alpha)
    rgb_array = rgb_array.reshape((320, 320, 4))
    rgb_array = rgb_array[:, :, :3]
    pil_img = Image.fromarray(rgb_array)

    # TODO: this switch is super clumsy, there is no doubt some
    #       standard way of doing this switch-if-path-looks-like-a-gs-thing
    if render_output_path.startswith("gs:"):
        # convert to btyes
        bytes_io = io.BytesIO()
        pil_img.save(bytes_io, format='PNG')
        img_bytes = bytes_io.getvalue()
        # split out bucket and blob_prefix to decide blob path
        m = re.match("gs://(.*?)/(.*)", render_output_path)
        if not m:
            raise Exception("invalid gs path [%s]" % render_output_path)
        bucket_name, blob_prefix = m.groups()
        blob_name = "%s/seed_%06d.png" % (blob_prefix, seed)
        # open client and store png btyes
        client = storage.Client()
        blob = client.bucket(bucket_name).blob(blob_name)
        blob.upload_from_string(img_bytes)
        render_fname = "gs://%s/%s" % (bucket_name, blob_name)
    else:
        # hackily save locally (note: assumes render_output_path is a dir)
        render_fname = "%s/seed_%06d.png" % (render_output_path, seed)
        pil_img.save(render_fname)

    # return render_info
    return {'seed': seed,
            'urdf_id': urdf_id,
            'render_fname': render_fname}
