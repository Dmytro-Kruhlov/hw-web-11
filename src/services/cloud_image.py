import hashlib

import cloudinary
import cloudinary.uploader
from src.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    @staticmethod
    def generate_name_avatar(email: str):
        """
        The generate_name_avatar function takes an email address as input and returns a string that is the name of the avatar image.
        The function uses SHA256 to hash the email address, then truncates it to 12 characters.
        It then prepends &quot;hw13/&quot; to this string and returns it.

        :param email: str: Pass the email address of the user into
        :return: A string that is the name of a file
        :doc-author: Trelent
        """
        name = hashlib.sha256(email.encode("utf-8")).hexdigest()[:12]
        return f"hw13/{name}"

    @staticmethod
    def upload(file, public_id):
        """
        The upload function takes a file and public_id as arguments.
        It then uploads the file to Cloudinary using the public_id provided.
        The function returns a dictionary containing information about the uploaded image.

        :param file: Upload a file to the cloudinary account
        :param public_id: Set the public id of the image
        :return: A dictionary with the following keys:
        :doc-author: Trelent
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_url_for_avatar(public_id, r):
        """
        The get_url_for_avatar function takes in a public_id and an r (request) object.
        It then uses the cloudinary library to build a URL for the avatar image, using
        the public_id as well as some other parameters. The version parameter is used to
        ensure that we are getting the most recent version of our image.

        :param public_id: Identify the image in cloudinary
        :param r: Get the version of the image
        :return: A url for the avatar image
        :doc-author: Trelent
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
                width=250, height=250, crop="fill", version=r.get("version")
            )
        return src_url
