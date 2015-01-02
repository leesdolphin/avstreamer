import unittest as ut
from ddt import ddt, data

import avstreamer.storage.video as vid


def load_file(file_name):
    with open("tests/sample_files/" + file_name, "rb") as f:
        return f.read()



@ddt
class TestMetadataFileWriter(ut.TestCase):

    @data(
        ("sample_imgs/sample_720_x_576.jpeg", 720, 576),
        ("sample_imgs/sample_1024_x_768.jpeg", 1024, 768),
        ("sample_imgs/sample_1280_x_720.jpeg", 1280, 720),
        ("sample_imgs/sample_non-image.jpeg", vid.UNDECODABLE_IMAGE_DIMENSIONS, vid.UNDECODABLE_IMAGE_DIMENSIONS)
    )
    def test_decodes_image_dimensions(self, data_tuple):
        file, width, height = data_tuple

        image = load_file(file)
        img_w, img_h = vid.MJPEGVideoStorage.parse_frame(image)

        self.assertEqual(width, img_w)
        self.assertEqual(height, img_h)
