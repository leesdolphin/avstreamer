import datetime
import time
import struct


import avstreamer.storage.metadata as metadata



UNDECODABLE_IMAGE_DIMENSIONS = 0xffff
DEFAULT_FILE_DURATION = datetime.timedelta(minutes=10)

class MJPEGVideoStorage(object):

    FILE_NAME_FORMAT = "%Y-%m-%d/%H-%M-%S"

    def __init__(self, source_name, file_duration=DEFAULT_FILE_DURATION, hasher=0x00):
        self.source_name = source_name
        self.file_duration = file_duration
        self.hasher = hasher
        self.video_file = None
        self.start_time = None

    @staticmethod
    def parse_frame(jpeg_data):
        """
        Returns a tuple of width then height
        """
        # Bassed off http://wiki.tcl.tk/757

        dim_segment_headers = ["\xff" + chr(code) for code in
                                [0xc0, 0xc1, 0xc2, 0xc3]]
        # Skip 3 bytes then height then width(2 bytes each).
        # I have *assumed* they are unsigned.
        dim_struct = struct.Struct(">2x 3x H H")
        length_struct = struct.Struct(">2x H")

        pos = 2  # Skip the 2 byte mini-header
        length = len(jpeg_data)
        while pos < length:
            segment = jpeg_data[pos:pos+2]
            if segment in dim_segment_headers:
                # Found dimension headers
                height, width = dim_struct.unpack(jpeg_data[pos:pos+9])
                return width, height
            else:
                data_length, = length_struct.unpack(jpeg_data[pos:pos+4])
                pos += data_length + 2 # +2 for the segment header

        return UNDECODABLE_IMAGE_DIMENSIONS, UNDECODABLE_IMAGE_DIMENSIONS


    def write_image(self, jpeg_data, width, height, frame_rate):
        now = time.time()
        date = datetime.datetime.utcnow()

        if width < 0 or height < 0:
            width, height = self.parse_frame(jpeg_data)

        if not self.video_file:
            # TODO or file expired
            # TODO or information different.
            # TODO rotate file

            base_name = sourcename + "/" + FILE_NAME_FORMAT.format(date) + "_video"
            file = open(base_name + ".mjpeg")
            meta_file = open(base_name + ".meta")
            header = create_header(start_time, width, height, frame_rate)

            self.video_file = metadata.MetadataFileWriter(file, meta_file, header)

        self.video_file.write_frame(jpeg_data)


    def create_header(self, start_time, width, height, frame_rate):
        header = metadata.MJPEGVideoMetadataHeader()

        header.hash = self.hasher
        header.start_time = start_time
        header.source_name = self.source_name
        header.horizontal_size = width
        header.vertical_size = height
        header.frame_rate = frame_rate

        return header
