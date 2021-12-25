//  https://github.com/np-8/dash-uploader 
// 
// Credits:
// This file is based on following repositories
// v.0.0.3 from https://github.com/rmarren1/dash-resumable-upload
// v.0.0.4 from https://github.com/westonkjones/dash-resumable-upload

import React, { Component } from 'react';
import Flow from '@flowjs/flow.js';
import Button from './Button.react.js';
import ProgressBar from './ProgressBar.react.js'
import PropTypes from 'prop-types';
import './progressbar.css';
import './button.css';

/**
 *  The Upload component
 */
export default class Upload_ReactComponent extends Component {

    static initialState = {
        progressBar: 0,
        messageStatus: '',
        fileList: { files: [] },
        isPaused: false,
        isUploading: false,
        isHovered: false,
        isComplete: false,
        showEnabledButtons: false,
        currentFile: ''
    }

    constructor(props) {
        super(props);
        this.state = Upload_ReactComponent.initialState;
        this.toggleHovered = this.toggleHovered.bind(this)
        this.cancelUpload = this.cancelUpload.bind(this)
        this.pauseUpload = this.pauseUpload.bind(this)
        this.startUpload = this.startUpload.bind(this)
        this.createButton = this.createButton.bind(this)
        this.resumable = null;
    }

    resetBuilder() {
        this.setState(Upload_ReactComponent.initialState)
    }

    componentDidMount() {

        // Full list of options here
        // https://github.com/flowjs/flow.js#configuration 
        const flowComponent = new Flow({
            //  The API endpoint
            target: this.props.service,
            // Additional data for the requests
            query: { upload_id: this.props.upload_id },
            // Chunk size in bytes.
            chunkSize: this.props.chunkSize,
            // Number of simultaneous uploads
            simultaneousUploads: this.props.simultaneousUploads,
            // Extra headers to include in the multipart POST with data. 
            // If a function, it will be passed a FlowFile, a FlowChunk object and a isTest boolean (Default: {})
            headers: {},
            // Once a file is uploaded, allow reupload of the same file. By default, if a file
            //  is already uploaded, it will be skipped unless the file is removed from the existing 
            // Flow object. (Default: false)
            allowDuplicateUploads: true,
            // testChunks Make a GET request to the server for each chunks to see if it already exists. 
            //  If implemented on the server-side, this will allow for upload resumes even after a browser
            //  crash or even a computer restart. (Default: true) 
            testChunks: false,

            // fileType: this.props.filetypes,
            // maxFiles: this.props.maxFiles,
            // maxFileSize: this.props.maxFileSize,
            // fileTypeErrorCallback: () => {
            //     this.setState({
            //         messageStatus: 'Invalid file type!'
            //     });
            // },
            // forceChunkSize: false
        });


        flowComponent.on('fileAdded', function (file) {
            if (!this.props.filetypes.includes(file.getExtension())) {
                return false;
            };
        });


        this.props.setProps({
            isCompleted: false,
            newestUploadedFileName: '',
            uploadedFiles: 0,
        });
        // Clicking the component will open upload dialog 
        ResumableField.assignBrowse(this.uploader);

        // Enable or Disable DragAnd Drop
        if (this.props.disableDragAndDrop === false && this.props.disabled === false) {
            ResumableField.assignDrop(this.dropZone);
        }

        ResumableField.on('fileAdded', (file) => {
            this.props.setProps({
                // Currently supports uploading only one file at a time.
                isCompleted: false,
                fileNames: [],
            });
            this.setState({
                messageStatus: this.props.fileAddedMessage || ' Starting upload! of ' + file.fileName,
                showEnabledButtons: true,
                // Currently supports uploading only one file at a time.
                isComplete: false,
                fileList: { files: [] },
                currentFile: file.fileName,
            });

            if (typeof this.props.onFileAdded === 'function') {
                this.props.onFileAdded(file, this.resumable);
            } else {
                ResumableField.upload();
            }
        });

        // Uploading a file is completed
        // The "fileNames" is a list, even though currently uploading
        // only one file at a time is supported.
        // When uploading multiple files, this will be called every time a file upload completes.
        ResumableField.on('fileSuccess', (file, fileServer) => {

            if (this.props.fileNameServer) {
                const objectServer = JSON.parse(fileServer);
                file.fileName = objectServer[this.props.fileNameServer];
            } else {
                file.fileName = fileServer;
            }
            const currentFiles = this.state.fileList.files;
            currentFiles.push(file);

            const fileNames = this.props.fileNames
            fileNames.push(file.fileName);

            if (this.props.setProps) {
                this.props.setProps({
                    fileNames: fileNames,
                    newestUploadedFileName: file.fileName,
                    uploadedFiles: this.props.uploadedFiles + 1,
                });
            }
            this.setState({
                fileList: { files: currentFiles },
                showEnabledButtons: false,
                messageStatus: this.props.completedMessage + file.fileName || fileServer
            }, () => {
                if (typeof this.props.onFileSuccess === 'function') {
                    this.props.onFileSuccess(file, fileServer);
                }
            });

            // Make re-upload of a file with same filename possible.
            ResumableField.removeFile(file);
        });



        ResumableField.on('progress', () => {


            this.setState({
                isUploading: ResumableField.isUploading()
            });

            if ((ResumableField.progress() * 100) < 100) {
                this.setState({
                    messageStatus: 'Uploading "' + this.state.currentFile + '"',
                    progressBar: ResumableField.progress() * 100
                });
            } else {
                setTimeout(() => {
                    this.setState({
                        progressBar: 0
                    })
                }, 1000);
            }

        });



        ResumableField.on('fileError', (file, errorCount) => {

            if (typeof (this.props.onUploadErrorCallback) !== 'undefined') {
                this.props.onUploadErrorCallback(file, errorCount);
            } else {
                console.log('fileError with flow.js! (file, errorCount)', file, errorCount)
            }

        });

        this.resumable = ResumableField;
    }

    componentDidUpdate(prevProps) {
        const prevEnableDrop = (prevProps.disableDragAndDrop === false && prevProps.disabled === false);
        const curEnableDrop = (this.props.disableDragAndDrop === false && this.props.disabled === false);
        if (curEnableDrop !== prevEnableDrop) {
            if (curEnableDrop) {
                this.resumable.assignDrop(this.dropZone);
            } else {
                this.resumable.unAssignDrop(this.dropZone);
            }
        }
    }

    cancelUpload() {
        this.resumable.cancel();
        this.resetBuilder();
    }


    pauseUpload() {
        if (!this.state.isPaused) {
            this.resumable.pause();
            this.setState({
                isPaused: true,
                isUploading: true
            });
        } else {
            this.resumable.upload();
            this.setState({
                isPaused: false,
                isUploading: true
            });
        }
    }

    startUpload() {
        this.setState({
            isPaused: false
        });
    }

    toggleHovered() {
        this.setState({
            isHovered: !this.state.isHovered
        })
    }

    createButton(onClick, text, btnEnabledInSettings, disabled, btnClass) {
        let btn = null;
        if (this.state.showEnabledButtons && btnEnabledInSettings) {
            if (typeof btnEnabledInSettings === 'string' || typeof btnEnabledInSettings === 'boolean') {
                btn = <Button text={btnEnabledInSettings && text} btnClass={btnClass} onClick={onClick} disabled={disabled} isUploading={this.state.isUploading}></Button>
            }
            else { btn = btnEnabledInSettings }
        }
        return btn
    }

    render() {

        const fileList = null;

        let textLabel = null;
        if (this.props.textLabel) {
            textLabel = this.props.textLabel;
        }

        let startButton = this.createButton(
            this.startUpload,
            'upload',
            this.props.startButton,
            this.state.isUploading,
            "dash-uploader-btn-start"
        );

        let cancelButton = this.createButton(
            this.cancelUpload,
            'cancel',
            this.props.cancelButton,
            !this.state.isUploading,
            "dash-uploader-btn-cancel"
        );

        let pauseButton = this.createButton(
            this.pauseUpload,
            (this.state.isPaused ? 'resume' : 'pause'),
            this.props.pauseButton,
            !this.state.isUploading,
            "dash-uploader-btn-pause"
        );


        const getStyle = () => {
            if (this.state.isComplete) {
                return this.props.completeStyle;
            } else if (this.state.isUploading) {
                return this.props.uploadingStyle;
            }
            return this.props.defaultStyle;

        }

        const getClass = () => {
            if (this.props.disabledInput) {
                return this.props.disableClass;
            } else if (this.state.isHovered) {
                return this.props.hoveredClass;
            } else if (this.state.isUploading) {
                return this.props.uploadingClass;
            } else if (this.state.isComplete) {
                return this.props.completeClass;
            } else if (this.state.isPaused) {
                return this.props.completeClass;
            }
            return this.props.className

        }

        return (
            <div style={getStyle()} id={this.props.id} className={getClass()} ref={node => this.dropZone = node} >
                <div id={this.props.id + '-padding'}
                    style={{
                        padding: '10px',
                    }}>
                    <label
                        style={{
                            display: this.state.isUploading ? 'block' : 'inline-block',
                            verticalAlign: 'middle', lineHeight: 'normal',
                            width: this.state.isUploading ? 'auto' : '100%',
                            paddingRight: this.state.isUploading ? '10px' : '0',
                            textAlign: 'center', wordWrap: 'break-word',
                            cursor: this.state.isUploading ? 'default' : 'pointer',
                            fontSize: this.state.isUploading ? '10px' : 'inherit',
                        }}
                        onMouseEnter={this.toggleHovered}
                        onMouseLeave={this.toggleHovered}
                    >

                        {(this.state.messageStatus === '') ? textLabel : this.state.messageStatus}
                        <input
                            ref={node => this.uploader = node}
                            type="file"
                            className='btn'
                            name={this.props.id + '-upload'}
                            accept={this.props.fileAccept || '*'}
                            disabled={this.state.isUploading || false}
                            style={{
                                'opacity': '0',
                                'width': '0',
                                'height': '0',
                                'position': 'absolute',
                                'overflow': 'hidden',
                                'zIndex': '-1',
                            }}
                        />
                    </label>
                    <ProgressBar isUploading={this.state.isUploading} progressBar={this.state.progressBar}></ProgressBar>
                    {fileList}
                    {startButton}
                    {pauseButton}
                    {cancelButton}
                </div>
            </div >
        );
    }
}

Upload_ReactComponent.propTypes = {
    /**
     * Maximum number of files that can be uploaded in one session
     */
    maxFiles: PropTypes.number,

    /**
     * Maximum size per file in bytes.
     */
    maxFileSize: PropTypes.number,

    /**
     * Size of file chunks to send to server.
     */
    chunkSize: PropTypes.number,

    /**
     * Number of simultaneous uploads to select
     */
    simultaneousUploads: PropTypes.number,

    /**
     * The service to send the files to
     */
    service: PropTypes.string,

    /**
     * Class to add to the upload component by default
     */
    className: PropTypes.string,

    /**
     * Class to add to the upload component when it is hovered
     */
    hoveredClass: PropTypes.string,

    /**
     * Class to add to the upload component when it is disabled
     */
    disabledClass: PropTypes.string,

    /**
     * Class to add to the upload component when it is paused
     */
    pausedClass: PropTypes.string,

    /**
     * Class to add to the upload component when it is complete
     */
    completeClass: PropTypes.string,

    /**
     * Class to add to the upload component when it is uploading
     */
    uploadingClass: PropTypes.string,

    /**
     * Style attributes to add to the upload component
     */
    defaultStyle: PropTypes.object,

    /**
     * Style when upload is disabled
     */
    disabledStyle: PropTypes.object,

    /**
     * Style when upload is in progress
     */
    uploadingStyle: PropTypes.object,

    /**
     * Style when upload is completed (upload finished)
     */
    completeStyle: PropTypes.object,

    /**
     * The string to display in the upload component
     */
    textLabel: PropTypes.string,

    /**
     * Message to display when upload disabled
     */
    disabledMessage: PropTypes.string,

    /**
     * Message to display when upload completed
     */
    completedMessage: PropTypes.string,

    /**
     * The names of the files uploaded
     */
    fileNames: PropTypes.arrayOf(PropTypes.string),

    /**
     * List of allowed file types, e.g. ['jpg', 'png']
     */
    filetypes: PropTypes.arrayOf(PropTypes.string),

    /**
     * Whether or not to have a start button
     */
    startButton: PropTypes.bool,

    /**
     * Whether or not to have a pause button
     */
    pauseButton: PropTypes.bool,

    /**
     * Whether or not to have a cancel button
     */
    cancelButton: PropTypes.bool,

    /**
     * Whether or not to allow file uploading
     */
    disabled: PropTypes.bool,

    /**
     * Whether or not to allow file drag and drop
     */
    disableDragAndDrop: PropTypes.bool,

    /**
     * Dash-supplied function for updating props
     */
    setProps: PropTypes.func,

    /**
     * Callback to call on error (untested)
     */
    onUploadErrorCallback: PropTypes.func,

    /**
     * User supplied id of this component
     */
    id: PropTypes.string,

    /**
     *  The boolean flag telling if upload is completed.
     */
    isCompleted: PropTypes.bool,

    /**
     *  The ID for the upload event (for example, session ID)
     */
    upload_id: PropTypes.string,

    /**
     *  Number of uploaded files.
     */
    uploadedFiles: PropTypes.number,


    /**
     *  Name of the newest uploaded file
     */
    newestUploadedFileName: PropTypes.string,

    /**
     *  Function to call on upload error (untested)
     */
    onUploadErrorCallback: PropTypes.func,
}

Upload_ReactComponent.defaultProps = {
    maxFiles: 1,
    maxFileSize: 1024 * 1024 * 10,
    chunkSize: 1024 * 1024,
    simultaneousUploads: 1,
    service: '/API/dash-uploader',
    className: 'dash-uploader-default',
    hoveredClass: 'dash-uploader-hovered',
    completeClass: 'dash-uploader-complete',
    disabledClass: 'dash-uploader-disabled',
    pausedClass: 'dash-uploader-paused',
    uploadingClass: 'dash-uploader-uploading',
    defaultStyle: {},
    uploadingStyle: {},
    completeStyle: {},
    textLabel: 'Click Here to Select a File',
    completedMessage: 'Complete! ',
    fileNames: [],
    newestUploadedFileName: '',
    uploadedFiles: 0,
    filetypes: undefined,
    startButton: true,
    pauseButton: true,
    cancelButton: true,
    disableDragAndDrop: false,
    id: 'default-dash-uploader-id',
    onUploadErrorCallback: undefined,
    isCompleted: false,
    upload_id: ''
};
