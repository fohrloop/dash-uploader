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
import './uploader.css';


/**
 * Convert bytes to Megabytes
 * 
 * @param {number} size_bytes - The bytes
 * @return {number} size_mb - Bytes converted to megabytes
 */
function bytest_to_mb(size_bytes) {
    // Mb = 1024*1024 bytes
    return size_bytes / 1048576;
}


/**
 *  The Upload component
 */
export default class Upload_ReactComponent extends Component {

    static initialState = {
        progressBar: 0,
        messageStatus: '',
        uploadedFiles: [],
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
        this.flow = null
        // use 'true' to enable debug console log
        // (for development only!)
        this.debug = false
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
        });


        // Clicking the "this.uploader" component will open the browse files/folders dialog
        flowComponent.assignBrowse(this.uploader);

        // Enable or Disable DragAnd Drop
        if (this.props.disableDragAndDrop === false && this.props.disabled === false) {
            flowComponent.assignDrop(this.dropZone);
        }

        // fileAdded and filesAdded events are both triggered whenever
        // any (one or multiple) files are to be added (through dialog or drag&drop)
        // to the upload component's upload queue.
        // 
        // fileAdded must return true for files that should be uploaded
        // - Use this to check the extension
        // - Use this to check if the file size is in acceptable limits
        // - Use this to check if the file already exists on the server
        // 
        // Not in use, as files are checked on onFilesSubmitted already
        // flowComponent.on('fileAdded', this.checkFileIsOkayToBeUploaded);

        // filesAdded must also return true for file(s) that should be uploaded
        // - Use this to check if there are too many files or the 
        //   overall upload size is too large.
        // Not in use, as files are checked on onFilesSubmitted already
        // flowComponent.on('filesAdded', this.checkFilesAreOkayToBeUploaded);


        // Check files
        // individual files: size, filetype
        // sum of all files: size, number of files
        flowComponent.on('filesSubmitted', this.onFilesSubmitted)

        // Uploading a file is completed
        // The "uploadedFileNames" is a list, even though currently uploading
        // only one file at a time is supported.
        // When uploading multiple files, this will be called every time a file upload completes.
        flowComponent.on('fileSuccess', this.fileSuccess);


        flowComponent.on('progress', this.onProgress);
        flowComponent.on('complete', this.onComplete);
        flowComponent.on('fileError', this.fileError);

        this.flow = flowComponent;
    }

    componentDidUpdate(prevProps) {
        const prevEnableDrop = (prevProps.disableDragAndDrop === false && prevProps.disabled === false);
        const curEnableDrop = (this.props.disableDragAndDrop === false && this.props.disabled === false);
        if (curEnableDrop !== prevEnableDrop) {
            if (curEnableDrop) {
                this.flow.assignDrop(this.dropZone);
            } else {
                this.flow.unAssignDrop(this.dropZone);
            }
        }
    }

    checkFileExtensionIsOk = (file) => {
        var extension = file.name.split('.').pop()
        if (this.props.filetypes === undefined) {
            // All filetypes are accepted
            return true;
        }
        return this.props.filetypes.includes(extension)
    }

    checkFilesAreOkayToBeUploaded = (filearray) => {
        if (this.debug) {
            console.log('checkFilesAreOkayToBeUploaded')
        }
        if ((this.maxFiles !== undefined) && (filearray.length > this.maxFiles)) {
            alert('Too many files selected! Maximum number of files is: ', this.maxFiles.toString() + '!')
            return false
        }
        if (this.props.maxTotalSize !== undefined) {
            var sumOfSizes = 0;
            this.flow.files.forEach(function (file) {
                sumOfSizes += file.size
            }, this);
            if (sumOfSizes > this.props.maxTotalSize) {
                alert('Total file size too large (' + bytest_to_mb(sumOfSizes).toFixed(1) + ' Mb) ! Maximum total filesize is: ' + bytest_to_mb(this.props.maxTotalSize).toFixed(1) + ' Mb')
                return false
            }
        }
        return true
    }

    onProgress = () => {

        let parenthesisTxt = (bytest_to_mb(this.flow.sizeUploaded())).toFixed(2)
            + ' Mb'
        let filenameTxt = ''

        if (this.props.totalFilesCount > 1) {
            parenthesisTxt += ', File ' + (this.props.uploadedFileNames.length + 1).toString()
                + '/' + this.props.totalFilesCount.toString()
        } else {
            filenameTxt = this.flow.files[0].name + ' '
        }
        this.setState({
            messageStatus: 'Uploading ' + filenameTxt + '(' + parenthesisTxt + ')',
            progressBar: this.flow.progress() * 100
        });


    };

    onComplete = () => {

        if (this.debug) {
            console.log('onComplete')
        }
        // Make re-upload of a file with same filename possible.
        this.state.uploadedFiles.forEach(function (file) {
            this.flow.removeFile(file);
        }, this);

        this.setState({ isUploading: false, showEnabledButtons: false })
        setTimeout(() => {
            this.setState({ progressBar: 0 })
        }, 600);


    };

    removeAllFilesFromFlow = () => {
        while (this.flow.files.length > 0) {
            this.flow.removeFile(this.flow.files[0]);
        }
    }

    fileSuccess = (file, message, chunk) => {
        // file: FlowFile instance
        // message: string
        // chunk: FlowChunk instance
        if (this.debug) {
            console.log('fileSuccess:', file, message, chunk)
        }

        file.fileName = message;
        const uploadedFiles = this.state.uploadedFiles;
        uploadedFiles.push(file);

        const uploadedFileNames = this.props.uploadedFileNames
        uploadedFileNames.push(file.fileName);

        if (this.props.setProps) {
            this.props.setProps({
                dashAppCallbackBump: this.props.dashAppCallbackBump + 1,
                uploadedFileNames: uploadedFileNames,
                uploadedFilesSize: bytest_to_mb(this.flow.sizeUploaded()),
                totalFilesSize: bytest_to_mb(this.flow.getSize()),
            });
        }
        this.setState({
            uploadedFiles: uploadedFiles,
            messageStatus: this.props.completedMessage + file.fileName || fileServer
        }, () => {
            if (typeof this.props.onFileSuccess === 'function') {
                this.props.onFileSuccess(file, fileServer);
            }
        });

    };


    fileError = (file, errorCount) => {
        if (this.debug) {
            console.log('fileError', file, errorCount)
        }
        if (this.debug) {
            console.log('fileError with flow.js! (file, errorCount)', file, errorCount)
        }
        if (typeof (this.props.onUploadErrorCallback) !== 'undefined') {
            this.props.onUploadErrorCallback(file, errorCount);
        } else {
            alert('Unexpected error while uploading ' + file.relativePath + '!\nPlease reupload the file.')
        }

    };

    removeUnsupportedFileTypesFromQueue = () => {
        var n_bad_file_extension = 0
        // Remove files that do not have correct file extension.
        const removeTheseFiles = []
        this.flow.files.forEach(function (file) {
            if (this.debug) {
                console.log('Checking filetype for file', file)
            }
            if (!this.checkFileExtensionIsOk(file)) {
                if (this.debug) {
                    console.log('Removing file as filetype is not supported', file)
                }
                removeTheseFiles.push(file)
                n_bad_file_extension += 1
            }
        }, this);

        removeTheseFiles.forEach(function (file) {
            this.flow.removeFile(file);
        }, this);


        if (n_bad_file_extension == 1) {
            alert('1 file could not be uploaded, as the file extension is not supported! Allowed filetypes are: [' + this.props.filetypes.join(', ') + ']')
        } else if (n_bad_file_extension > 1) {
            alert(n_bad_file_extension.toString() + ' files could not be uploaded, as the file extension is not supported! Allowed filetypes are: [' + this.props.filetypes.join(', ') + ']')
        }
    }

    removeTooLargeFilesFromQueue = () => {
        var n_too_large_files = 0
        // Remove files that do not have correct file extension.
        const removeTheseFiles = []
        this.flow.files.forEach(function (file) {
            if (file.size > this.props.maxFileSize) {
                if (this.debug) {
                    console.log('Removing file as it is too large', file)
                }
                removeTheseFiles.push(file)
                n_too_large_files += 1
            }
        }, this);

        removeTheseFiles.forEach(function (file) {
            this.flow.removeFile(file);
        }, this);

        if (n_too_large_files == 1) {
            alert('1 file could not be uploaded, as the file is too large! Maximum allowed file size is ' + bytest_to_mb(this.props.maxFileSize).toFixed(1) + 'Mb')
        } else if (n_too_large_files > 1) {
            alert(n_too_large_files.toString() + ' files could not be uploaded, as the file is too large! Maximum allowed file size is ' + bytest_to_mb(this.props.maxFileSize).toFixed(1) + 'Mb')
        }
    }

    onFilesSubmitted = (files) => {
        if (this.debug) {
            console.log('onFilesSubmitted', files.length, files)
        }

        this.removeUnsupportedFileTypesFromQueue()
        this.removeTooLargeFilesFromQueue()
        const isok = this.checkFilesAreOkayToBeUploaded(this.flow.files)
        if (!isok) {
            this.removeAllFilesFromFlow()
            return
        }

        this.props.setProps({
            dashAppCallbackBump: 0,
            uploadedFileNames: [],
            totalFilesCount: this.flow.files.length,
            uploadedFilesSize: 0,
            totalFilesSize: 0,
        })
        this.setState({ showEnabledButtons: true })
        this.flow.upload()
        this.setState({ isUploading: true })

    }

    cancelUpload() {
        this.flow.cancel();
        this.resetBuilder();
        this.setState({ isUploading: false })
    }

    pauseUpload() {
        if (!this.state.isPaused) {
            this.flow.pause();
            this.setState({ isPaused: true });
        } else {
            this.flow.resume();
            this.setState({ isPaused: false });
        }
    }

    startUpload() {
        this.setState({ isPaused: false, isUploading: true, showEnabledButtons: true });
    }

    toggleHovered() {
        this.setState({
            isHovered: !this.state.isHovered
        })
    }

    createButton(onClick, text, btnEnabledInSettings, disabled, btnClass) {
        if (this.state.showEnabledButtons && btnEnabledInSettings) {
            return <Button text={btnEnabledInSettings && text} btnClass={btnClass} onClick={onClick} disabled={disabled} isUploading={this.state.isUploading}></Button>
        } else {
            return null;
        }
    }

    getLabel = () => {

        let textLabel = this.props.textLabel ? this.props.textLabel : null

        return <label
            style={{
                display: this.state.isUploading ? 'block' : 'inline-block',
                verticalAlign: 'middle',
                lineHeight: 'normal',
                width: this.state.isUploading ? 'auto' : '100%',
                paddingRight: this.state.isUploading ? '10px' : '0',
                textAlign: 'center',
                wordWrap: 'break-word',
                cursor: this.state.isUploading ? 'default' : 'pointer',
                fontSize: this.state.isUploading ? '10px' : 'inherit',
            }}
            onMouseEnter={this.toggleHovered}
            onMouseLeave={this.toggleHovered}
            className="dash-uploader-label"
        >
            {(this.state.messageStatus === '') ? textLabel : this.state.messageStatus}
            <input
                ref={node => this.uploader = node}
                type="file"
                className='btn'
                name={this.props.id + '-upload'}
                accept={this.props.filetypes || '*'}
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
    }

    render() {

        let startButton = this.createButton(
            this.startUpload,
            'upload',
            this.props.startButton,
            this.state.isUploading,
            "dash-uploader-btn-start btn-outline-secondary "
        );

        let cancelButton = this.createButton(
            this.cancelUpload,
            'cancel',
            this.props.cancelButton,
            !this.state.isUploading,
            "dash-uploader-btn-cancel btn-outline-secondary "
        );

        let pauseButton = this.createButton(
            this.pauseUpload,
            (this.state.isPaused ? 'resume' : 'pause'),
            this.props.pauseButton,
            !this.state.isUploading,
            "dash-uploader-btn-pause btn-outline-primary "
        );


        const getStyle = () => {
            if (this.state.isUploading) {
                return this.props.uploadingStyle;
            } else if (this.props.disabled) {
                return this.props.disabledStyle;
            } else if (this.state.isComplete) {
                return this.props.completeStyle;
            }
            return this.props.defaultStyle;

        }

        const getClass = () => {
            let classList = [this.props.className];
            const classes = {
                isUploading: this.props.uploadingClass,
                isPaused: this.props.pausedClass,
                isHovered: this.props.hoveredClass,
                isComplete: this.props.completeClass,
            }

            Object.entries(classes).forEach(([stateProperty, className]) => {
                this.state[stateProperty] && classList.push(className);
            });

            this.props.disabled && classList.push(this.props.disabledClass);

            return classList.join(" ");

        }


        return (
            <div style={getStyle()} id={this.props.id} className={getClass()} ref={node => this.dropZone = node} >
                <div id={this.props.id + '-padding'}
                    style={{
                        padding: '10px',
                    }}>
                    {this.getLabel()}
                    <ProgressBar isUploading={this.state.isUploading} progressBar={this.state.progressBar}></ProgressBar>
                    <div className='dash-uploader-button-container'>
                        {cancelButton}
                        {pauseButton}
                        {startButton}
                    </div>
                </div>
            </div >
        );
    }
}

Upload_ReactComponent.propTypes = {
    /**
     * Dash-supplied function for updating props
     * This is something special to Dash, and is needed
     * If values are needed to be passed to the python dash backend.
     */
    setProps: PropTypes.func,


    /**
     * Maximum number of files that can be uploaded in one session
     */
    maxFiles: PropTypes.number,

    /**
     * Maximum size per file in bytes.
     */
    maxFileSize: PropTypes.number,

    /**
     * Maximum total size in bytes.
     */
    maxTotalSize: PropTypes.number,

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
    completedClass: PropTypes.string,

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
    uploadedFileNames: PropTypes.arrayOf(PropTypes.string),

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
     * Callback to call on error (untested)
     */
    onUploadErrorCallback: PropTypes.func,

    /**
     * User supplied id of this component
     */
    id: PropTypes.string,

    /**
     *  A prop that is monitored by the dash app
     *  Wheneven the value of this prop is changed,
     *  all the props are sent to the dash application.
     * 
     *  This is used in the dash callbacks.
     */
    dashAppCallbackBump: PropTypes.number,

    /**
     *  The ID for the upload event (for example, session ID)
     */
    upload_id: PropTypes.string,


    /**
     *  Total number of files to be uploaded.
     */
    totalFilesCount: PropTypes.number,

    /**
     *  Size of uploaded files (Mb). Mb = 1024*1024 bytes.
     */
    uploadedFilesSize: PropTypes.number,

    /**
     *   Total size of uploaded files to be uploaded (Mb). 
     *   Mb = 1024*1024 bytes.
     */
    totalFilesSize: PropTypes.number,
}

Upload_ReactComponent.defaultProps = {
    maxFiles: 1,
    maxFileSize: 1024 * 1024 * 10,
    chunkSize: 1024 * 1024,
    simultaneousUploads: 1,
    service: '/API/dash-uploader',
    className: 'dash-uploader-default',
    hoveredClass: 'dash-uploader-hovered',
    completedClass: 'dash-uploader-completed',
    disabledClass: 'dash-uploader-disabled',
    pausedClass: 'dash-uploader-paused',
    uploadingClass: 'dash-uploader-uploading',
    defaultStyle: {},
    uploadingStyle: {},
    completeStyle: {},
    textLabel: 'Click Here to Select a File',
    completedMessage: 'Complete! ',
    uploadedFileNames: [],
    filetypes: undefined,
    startButton: true,
    pauseButton: true,
    cancelButton: true,
    disableDragAndDrop: false,
    id: 'default-dash-uploader-id',
    onUploadErrorCallback: undefined,
    dashAppCallbackBump: 0,
    upload_id: ''
};

