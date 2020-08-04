import logging
import os
from pathlib import Path
import shutil
import time

from dash import __version__ as dashversion
import dash_html_components as html
from flask import request
from flask import abort

import dash_uploader.settings as settings

logger = logging.getLogger('dash_uploader')


def configure_upload(app, folder, use_upload_id=True, upload_api=None):
    """
    Parameters
    ---------
    app: dash.Dash
        The application instance
    folder: str
        The folder where to upload files.
        Can be relative ("uploads") or
        absolute (r"C:\tmp\my_uploads").
        If the folder does not exist, it will
        be created automatically.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different 
        session id) will use their own folder. If False, 
        all files from all sessions are uploaded into
        same folder (not recommended).
    upload_api: None or str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests. For example: "/API/dash-uploader"
    """
    settings.UPLOAD_FOLDER_ROOT = folder
    settings.app = app

    if upload_api is None:
        upload_api = settings.upload_api
    else:
        # Set the upload api since du.Upload components
        # that are created after du.configure_upload
        # need to be able to read the api endpoint.
        settings.upload_api = upload_api

    # Needed if using a proxy
    settings.requests_pathname_prefix = app.config.get(
        'requests_pathname_prefix', '/')

    decorate_server(app.server,
                    folder,
                    upload_api,
                    use_upload_id=use_upload_id)


def decorate_server(
    server,
    temp_base,
    upload_api,
    use_upload_id=True,
):
    """
    Parameters
    ----------
    server: flask.Flask
        The flask server instance
    temp_base: str
        The upload root folder
    upload_api: str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different 
        session id) will use their own folder. If False, 
        all files from all sessions are uploaded into
        same folder (not recommended).
    """

    # resumable.js uses a GET request to check if it uploaded the file already.
    # NOTE: your validation here needs to match whatever you do in the POST
    # (otherwise it will NEVER find the files)

    @server.route(upload_api, methods=['GET'])
    def resumable():

        resumableIdentifier = request.args.get('resumableIdentifier', type=str)
        resumableFilename = request.args.get('resumableFilename', type=str)
        resumableChunkNumber = request.args.get('resumableChunkNumber',
                                                type=int)

        upload_id = request.args.get('upload_id', default='', type=str)

        if not (resumableIdentifier and resumableFilename
                and resumableChunkNumber):
            # Parameters are missing or invalid
            abort(500, 'Parameter error')

        temp_root = os.path.join(temp_base,
                                 upload_id) if use_upload_id else temp_base

        # chunk folder path based on the parameters
        temp_dir = os.path.join(temp_root, resumableIdentifier)

        # chunk path based on the parameters
        chunk_file = os.path.join(
            temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))
        server.logger.debug('Getting chunk: %s', chunk_file)

        if os.path.isfile(chunk_file):
            # Let resumable.js know this chunk already exists
            return 'OK'
        else:
            # Let resumable.js know this chunk does not exists
            # and needs to be uploaded
            abort(404, 'Not found')

    # if it didn't already upload, resumable.js sends the file here
    @server.route(upload_api, methods=['POST'])
    def resumable_post():

        resumableTotalChunks = request.form.get('resumableTotalChunks',
                                                type=int)
        resumableChunkNumber = request.form.get('resumableChunkNumber',
                                                default=1,
                                                type=int)
        resumableFilename = request.form.get('resumableFilename',
                                             default='error',
                                             type=str)
        resumableIdentifier = request.form.get('resumableIdentifier',
                                               default='error',
                                               type=str)
        upload_id = request.form.get('upload_id', default='', type=str)
        temp_root = os.path.join(temp_base,
                                 upload_id) if use_upload_id else temp_base

        # get the chunk data
        chunk_data = request.files['file']

        # make our temp directory
        temp_dir = os.path.join(temp_root, resumableIdentifier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)

        # save the chunk data
        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(temp_dir, chunk_name)

        # make a lock file
        lock_file_path = os.path.join(
            temp_dir, '.lock_{:d}'.format(resumableChunkNumber))

        with open(lock_file_path, 'a'):
            os.utime(lock_file_path, None)
        chunk_data.save(chunk_file)
        os.unlink(lock_file_path)

        # check if the upload is complete
        chunk_paths = [
            os.path.join(temp_dir, get_chunk_name(resumableFilename, x))
            for x in range(1, resumableTotalChunks + 1)
        ]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:

            # Make sure all files are finished writing
            # but do not wait forever..
            tried = 0
            while any([
                    os.path.isfile(
                        os.path.join(temp_dir, '.lock_{:d}'.format(chunk)))
                    for chunk in range(1, resumableTotalChunks + 1)
            ]):
                tried += 1
                if tried >= 5:
                    logger.error('Error uploading files with temp_dir: %s.',
                                 temp_dir)
                    raise Exception('Error uploading files with temp_dir: ' +
                                    temp_dir)
                time.sleep(1)

            # Make sure some other chunk didn't trigger file reconstruction
            target_file_name = os.path.join(temp_root, resumableFilename)
            if os.path.exists(target_file_name):
                logger.info('File %s exists already. Overwriting..',
                            target_file_name)
                os.unlink(target_file_name)

            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    with open(p, 'rb') as stored_chunk_file:
                        target_file.write(stored_chunk_file.read())
            server.logger.debug('File saved to: %s', target_file_name)
            shutil.rmtree(temp_dir)

        return resumableFilename


def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number