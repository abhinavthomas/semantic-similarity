#!/usr/bin/python
# Semantic similarity implementation.

# Provides a fast api,for semantic similarity search using Spotify Annoy and Universal Sentence Encoder.

# Copyright (c) Abhinav Thomas.

# semantic-similarity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# semantic similarity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with semantic-similarity.  If not, see <https://www.gnu.org/licenses/>.

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient


def __download_from_azure(azure_connect_str: str, container_name: str, blob_name: str, local_file_name: str):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            azure_connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name)
        with open(local_file_name, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        logger.info('File {} downloaded to {}.'.format(
            'azure-storage://{}/{}'.format(container_name, blob_name), local_file_name))

        logger.info('File size: {} GB'.format(
            round(os.path.getsize(local_file_name) / float(1024 ** 3), 2)))
    except Exception as e:
        logger.error('Failed to download {} to {}.'.format(
            'azure-storage://{}/{}'.format(container_name, blob_name), local_file_name))
        raise e


def __upload_to_azure(azure_connect_str: str, container_name: str, blob_name: str, local_file_name: str):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            azure_connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name)

        logger.info(
            "\nUploading to Azure Storage as blob:\n\t" + local_file_name)
        try:
            # delete if already exists
            blob_client.delete_blob()
        except ResourceNotFoundError:
            # ignore if not present
            pass
        finally:
            # Upload the created file
            with open(local_file_name, "rb") as data:
                blob_client.upload_blob(data)
            logger.info('File {} uploaded to {}.'.format(
                local_file_name, 'azure-storage://{}/{}'.format(container_name, blob_name)))

            logger.info('File size: {} GB'.format(
                round(os.path.getsize(local_file_name) / float(1024 ** 3), 2)))
    except Exception as e:
        logger.error('Failed to upload {} to {}.'.format(
            local_file_name, 'azure-storage://{}/{}'.format(container_name, blob_name)))
        raise e


def download_artefacts(blob_name: str, local_file: str):
    """
    Paramets:
    blob_name: Blob file name in cloud 
    local_file: Local file pth for index
    """
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER')
    __download_from_azure(connect_str, container_name, blob_name, local_file)


def upload_artefacts(blob_name: str, local_file: str):
    """
    Paramets:
    blob_name: Blob file name in cloud 
    local_file: Local file pth for index
    """
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER')
    __upload_to_azure(connect_str, container_name, blob_name, local_file)
