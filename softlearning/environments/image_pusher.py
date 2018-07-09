import os.path as osp

import numpy as np
from skimage.transform import resize

from rllab.core.serializable import Serializable
from rllab.misc import logger
from rllab.misc.overrides import overrides
from rllab.mujoco_py import MjViewer

from softlearning.misc.utils import PROJECT_PATH
from .pusher import PusherEnv


class ImagePusherEnv(PusherEnv):
    def __init__(self, image_size, *args, **kwargs):
        Serializable.quick_init(self, locals())
        self.image_size = image_size
        PusherEnv.__init__(self, *args, **kwargs)

    @overrides
    def get_current_obs(self):
        # image = self.render(mode='rgb_array',)
        data, width, height = self.get_viewer().get_image()
        image = np.fromstring(
            data, dtype='uint8'
        ).reshape(height, width, 3)[::-1,:,:]
        # resized_image = resize(image, size=(32, 32, 3))
        resized_image = resize(
            image,
            output_shape=self.image_size,
            preserve_range=True,
            anti_aliasing=True)

        # show_image = False
        # if show_image:
        #     from PIL import Image
        #     Image.fromarray(image.astype('uint8')).show()
        #     # .save(
        #     #     '/Users/kristian/code/softqlearning-private/tmp/{}_real.png'.format(self.i)
        #     # )
        #     Image.fromarray(resized_image.astype('uint8')).show()
        #     # .save(
        #     #     '/Users/kristian/code/softqlearning-private/tmp/{}_resized.png'.format(self.i)
        #     # )
        #     # setattr(self, 'i', getattr(self, 'i', 0) + 1)
        #     from pdb import set_trace; from pprint import pprint; set_trace()

        return np.concatenate([
            resized_image.reshape(-1),
            self.model.data.qpos.flat[self.JOINT_INDS],
            self.model.data.qvel.flat[self.JOINT_INDS],
        ]).reshape(-1)

    def get_viewer(self):
        if self.viewer is None:
            self.viewer = MjViewer(visible=False)
            self.viewer.start()
            self.viewer.set_model(self.model)
        return self.viewer

    def viewer_setup(self):
        viewer = self.get_viewer()
        viewer.cam.trackbodyid = 0
        viewer.cam.distance = 4.0
        cam_dist = 3.5
        cam_pos = np.array([0, 0, 0, cam_dist, -90, 0])
        viewer.cam.lookat[:3] = cam_pos[:3]
        viewer.cam.distance = cam_pos[3]
        viewer.cam.elevation = cam_pos[4]
        viewer.cam.azimuth = cam_pos[5]
        viewer.cam.trackbodyid = -1
