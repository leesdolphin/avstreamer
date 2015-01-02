import datetime
import time


import avstreamer.storage.metadata as metadata




DEFAULT_FILE_DURATION = datetime.timedelta(minutes=10)

class MJPEGVideoStorage(object):

    FILE_NAME_FORMAT = "%Y-%m-%d/%H-%M-%S"

    def __init__(self, source_name, file_duration=DEFAULT_FILE_DURATION, hasher=0x00):
        self.source_name = source_name
        self.file_duration = file_duration
        self.hasher = hasher
        self.video_file = None
        self.start_time = None


    def write_image(self, jpeg_data, width, height, frame_rate):
        now = time.time()
        date = datetime.datetime.utcnow()

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
