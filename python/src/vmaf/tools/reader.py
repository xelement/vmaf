import os

import numpy as np

__copyright__ = "Copyright 2016-2020, Netflix, Inc."
__license__ = "BSD+Patent"


class YuvReader(object):

    SUPPORTED_YUV_8BIT_TYPES = ['yuv420p',
                                'yuv422p',
                                'yuv444p',
                                ]

    SUPPORTED_YUV_10BIT_LE_TYPES = ['yuv420p10le',
                                    'yuv422p10le',
                                    'yuv444p10le',
                                    ]

    # ex: for yuv420p, the width and height of U/V is 0.5x, 0.5x of Y
    UV_WIDTH_HEIGHT_MULTIPLIERS_DICT = {'yuv420p': (0.5, 0.5),
                                        'yuv422p': (0.5, 1.0),
                                        'yuv444p': (1.0, 1.0),
                                        'yuv420p10le': (0.5, 0.5),
                                        'yuv422p10le': (0.5, 1.0),
                                        'yuv444p10le': (1.0, 1.0),
                                        }

    def __init__(self, filepath, width, height, yuv_type):

        self.filepath = filepath
        self.width = width
        self.height = height
        self.yuv_type = yuv_type

        self._asserts()

        self.file = open(self.filepath, 'rb')

    def close(self):
        self.file.close()

    # make YuvReader withable, e.g.:
    # with YuvReader(...) as yuv_reader:
    #     ...
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # make YuvReader iterable, e.g.:
    # for y, u, v in yuv_reader:
    #    ...
    def __iter__(self):
        return self

    def __next__(self):
        """next() is for python2 only, in python3 all you need to define is __next__(self)"""
        return self.next()

    @property
    def num_bytes(self):
        self._assert_file_exist()
        return os.path.getsize(self.filepath)

    @property
    def num_frms(self):
        w_multiplier, h_multiplier = self._get_uv_width_height_multiplier()

        if self._is_10bitle():
            num_frms = float(self.num_bytes) / self.width / self.height / (1.0 + w_multiplier * h_multiplier * 2) / 2

        elif self._is_8bit():
            num_frms = float(self.num_bytes) / self.width / self.height / (1.0 + w_multiplier * h_multiplier * 2)

        else:
            assert False

        assert num_frms.is_integer(), 'Number of frames is not integer: {}'.format(num_frms)

        return int(num_frms)

    def _get_uv_width_height_multiplier(self):
        self._assert_yuv_type()
        return self.UV_WIDTH_HEIGHT_MULTIPLIERS_DICT[self.yuv_type]

    def _assert_yuv_type(self):
        assert (self.yuv_type in self.SUPPORTED_YUV_8BIT_TYPES
                or self.yuv_type in self.SUPPORTED_YUV_10BIT_LE_TYPES), \
            'Unsupported YUV type: {}'.format(self.yuv_type)

    def _assert_file_exist(self):
        assert os.path.exists(self.filepath), \
            "File does not exist: {}".format(self.filepath)

    def _asserts(self):

        # assert YUV type
        self._assert_yuv_type()

        # assert file exists
        self._assert_file_exist()

        # assert file size: if consists of integer number of frames
        assert isinstance(self.num_frms, int)

    def _is_8bit(self):
        return self.yuv_type in self.SUPPORTED_YUV_8BIT_TYPES

    def _is_10bitle(self):
        return self.yuv_type in self.SUPPORTED_YUV_10BIT_LE_TYPES

    def next(self, format='uint'):

        assert format == 'uint' or format == 'float'

        y_width = self.width
        y_height = self.height
        uv_w_multiplier, uv_h_multiplier = self._get_uv_width_height_multiplier()
        uv_width = int(y_width * uv_w_multiplier)
        uv_height = int(y_height * uv_h_multiplier)

        if self._is_10bitle():
            pix_type = np.uint16
            word = 2
        elif self._is_8bit():
            pix_type = np.uint8
            word = 1
        else:
            assert False

        y = np.frombuffer(self.file.read(y_width * y_height * word), pix_type)
        if y.size == 0:
            raise StopIteration
        u = np.frombuffer(self.file.read(uv_width * uv_height * word), pix_type)
        if u.size == 0:
            raise StopIteration
        v = np.frombuffer(self.file.read(uv_width * uv_height * word), pix_type)
        if v.size == 0:
            raise StopIteration

        y = y.reshape(y_height, y_width)
        u = u.reshape(uv_height, uv_width)
        v = v.reshape(uv_height, uv_width)

        if format == 'uint':
            return y, u, v

        elif format == 'float':
            if self._is_8bit():
                return y.astype(np.double) / (2.0**8 - 1.0), u.astype(np.double) / (2.0**8 - 1.0), v.astype(np.double) / (2.0**8 - 1.0)
            elif self._is_10bitle():
                return y.astype(np.double) / (2.0**10 - 1.0), u.astype(np.double) / (2.0**10 - 1.0), v.astype(np.double) / (2.0**10 - 1.0)
            else:
                assert False

        else:
            assert False
