# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from enum import StrEnum
import os


class VisionFormats(StrEnum):
    """
    The format of the image.
    Valid Values: png | jpeg | gif | webp
    """
    PNG = 'png'
    JPEG = 'jpeg'
    GIF = 'gif'
    WEBP = 'webp'

@dataclass
class ContentVision:
    """
    Image content for a message.

    :param image_format (VisionFormats): The format of the image.
    :param image_bytes (bytes): The bytes of the image.
    :func content_by_filename: Creates a ContentVision instance based on a given image filename.
    """

    image_format: VisionFormats
    image_bytes: bytes

    @classmethod
    def content_by_filename(cls, filename):
        """
        Creates a ContentVision instance based on a given filename.

        :param filename (str): The filename of the image.
        :returns: ContentVision: The ContentVision instance.
        """
        image_format = os.path.splitext(filename)[1][1:]
        with open(filename, 'rb') as f:
            image_bytes = f.read()
        return ContentVision(image_format, image_bytes)
    
    def _to_dict(self):
        """
        Converts the ContentVision instance to a dictionary.

        :returns: dict: The dictionary representation of the ContentVision instance.
        """
        return {
            'image': {
                'format': self.image_format,
                'source': {
                    'bytes': self.image_bytes
                }
            }
        }
