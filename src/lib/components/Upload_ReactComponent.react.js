// v.0.5.0. https://github.com/np-8/dash-uploader 
// 
// Credits:
// This file is based on following repositories
// v.0.0.3 from https://github.com/rmarren1/dash-resumable-upload
// v.0.0.4 from https://github.com/westonkjones/dash-resumable-upload

import React, { Component } from 'react';

import Button from './Button.react.js';
import ProgressBar from './ProgressBar.react.js'
import PropTypes from 'prop-types';
import Resumablejs from 'resumablejs';
import './progressbar.css';
import './button.css';

/**
 *  The Upload component
 */
export default class Upload_ReactComponent extends Component {

    static initialState = {
        progressBar: 0,
        messageStatus: '',
        fileList: [] ,
        isPaused: false,
        isUploading: false,
        isHovered: false,
        isCompleted: false,
        showEnabledButtons: false,
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
        this.setState(Upload_ReactComponent.initialState);
    }

    componentDidMount() {

        const ResumableField = new Resumablejs({
            target: this.props.service,
            query: { upload_id: this.props.upload_id },
            fileType: this.props.filetypes,
            maxFiles: this.props.maxFiles,
            maxFileSize: this.props.maxFileSize,
            fileTypeErrorCallback: () => {
                this.setState({
                    messageStatus: 'Invalid file type!'
                });
            },
            testMethod: 'post',
            testChunks: false,
            headers: {},
            chunkSize: this.props.chunkSize,
            simultaneousUploads: this.props.simultaneousUploads,
            forceChunkSize: false
        });

        this.props.setProps({
            isCompleted: false,
            newestUploadedFileName: '',
            numberUploaded: 0,
        });
        // Clicking the component will open upload dialog 
        ResumableField.assignBrowse(this.uploader);

        // Enable or disable drag and drop
        if (this.props.disableDragAndDrop === false && this.props.disabled === false) {
            ResumableField.assignDrop(this.dropZone);
        }

        ResumableField.on('fileAdded', (file) => {
            let currentlyUploadingFiles = [];
            ResumableField.files.forEach((value, index, array) => {
                currentlyUploadingFiles.push(value.fileName); 
            })
            this.props.setProps({
                isCompleted: false,
                fileNames: [],
                currentlyUploadingFiles: currentlyUploadingFiles,
            });
            this.setState({
                messageStatus: this.props.fileAddedMessage || ' Added file to upload queue: ' + file.fileName,
                showEnabledButtons: true,
                isCompleted: false,
                fileList: [],
            });

            if (typeof this.props.onFileAdded === 'function') {
                this.props.onFileAdded(file, this.resumable);
            } else {
                ResumableField.upload();
            }
        });

        // Uploading a file is completed
        ResumableField.on('fileSuccess', (file, fileServer) => {

            if (this.props.fileNameServer) {
                const objectServer = JSON.parse(fileServer);
                file.fileName = objectServer[this.props.fileNameServer];
            } else {
                file.fileName = fileServer;
            }
            const currentFiles = this.state.fileList;
            currentFiles.push(file);


            const fileNames = this.props.fileNames
            fileNames.push(file.fileName);
            
            if (this.props.setProps) {
                this.props.setProps({
                    fileNames: fileNames,
                    // isCompleted: true,
                    newestUploadedFileName: file.fileName,
                    numberUploaded: this.props.numberUploaded + 1,
                });
            }
            this.setState({
                fileList: currentFiles,
                // isCompleted: true,
                // showEnabledButtons: false,
                messageStatus: this.props.completedMessage + file.fileName || fileServer
            }, () => {
                if (typeof this.props.onFileSuccess === 'function') {
                    this.props.onFileSuccess(file, fileServer);
                }
            });

            // Make re-upload of a file with same filename possible.
            ResumableField.removeFile(file);
        });


        // Uploading all files is complete
        ResumableField.on('complete', () => {
            if (this.props.setProps) {
                this.props.setProps({
                    isCompleted: true,
                    currentlyUploadingFiles: [],
                });
            }
            this.setState({
                isCompleted: true,
                showEnabledButtons: false,
            });
        });



        ResumableField.on('fileProgress', (file, msg) => {


            this.setState({
                isUploading: ResumableField.isUploading()
            });

            if ((ResumableField.progress() * 100) < 100) {
                this.setState({
                    messageStatus: 'Uploading: "' + file.fileName + '"',
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
                console.log('fileError with resumable.js! (file, errorCount)', file, errorCount)
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
        this.props.setProps({
            currentlyUploadingFiles: [],
        });
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
            if (this.state.isUploading) {
                return this.props.uploadingStyle;
            } else if (this.props.disabled) {
                return this.props.disabledStyle;
            } else if (this.state.isCompleted) {
                return this.props.completeStyle;
            }
            return this.props.defaultStyle;

        }

        const getClass = () => {
            if (this.state.isUploading) {
                return this.props.uploadingClass;
            } else if (this.state.isPaused) {
                return this.props.pausedClass;
            } else if (this.props.disabled) {
                return this.props.disabledClass;
            } else if (this.state.isHovered) {
                return this.props.hoveredClass;
            } else if (this.state.isCompleted) {
                return this.props.completeClass;
            }
            return this.props.className;

        }

        const getMessage = () => {
            if (this.state.isUploading === false && this.props.disabled === true && this.props.disabledMessage) {
                return this.props.disabledMessage;
            }
            else if (this.state.messageStatus === '') {
                if (this.props.textLabel) {
                    return this.props.textLabel;
                }
                return null;
            } else {
                return this.state.messageStatus;
            }
            
        }

        return (
            <div style={getStyle()} id={this.props.id} className={getClass()} ref={node => this.dropZone = node} >
                <div id={this.props.id + '-padding'}
                    style={{
                        padding: '10px'
                    }}>
                    <label
                        style={{
                            display: this.state.isUploading ? 'block' : 'inline-block',
                            verticalAlign: 'middle', lineHeight: 'normal',
                            width: this.state.isUploading ? 'auto' : '100%',
                            paddingRight: this.state.isUploading ? '10px' : '0',
                            textAlign: 'center', wordWrap: 'break-word',
                            cursor: this.state.isUploading || this.props.disabled ? 'default' : 'pointer',
                            fontSize: this.state.isUploading ? '10px' : 'inherit',
                        }}
                        onMouseEnter={this.toggleHovered}
                        onMouseLeave={this.toggleHovered}
                    >

                        {getMessage()}
                        <input
                            ref={node => this.uploader = node}
                            type="file"
                            className='btn'
                            name={this.props.id + '-upload'}
                            accept={this.props.fileAccept || '*'}
                            disabled={this.state.isUploading || this.props.disabled}
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
     *  The name of the newest uploaded file.
     */
    newestUploadedFileName: PropTypes.string,
    
    /**
     *  The names of all the files currently uploading.
     */
    currentlyUploadingFiles: PropTypes.arrayOf(PropTypes.string),

    /**
     *  The number of uploaded files (integer)
     */
    numberUploaded: PropTypes.number,

    /**
     *  Number of simulaneous uploads.
     */
    simultaneousUploads: PropTypes.number,

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
    disabledStyle: {},
    uploadingStyle: {},
    completeStyle: {},
    textLabel: 'Click Here to Select a File',
    disabledMessage: 'The uploader is disabled.',
    completedMessage: 'Complete! ',
    fileNames: [],
    newestUploadedFileName: '',
    currentlyUploadingFiles: [],
    numberUploaded: 0,
    filetypes: undefined,
    startButton: true,
    pauseButton: true,
    cancelButton: true,
    disabled: false,
    disableDragAndDrop: false,
    id: 'default-dash-uploader-id',
    onUploadErrorCallback: undefined,
    isCompleted: false,
    upload_id: ''
};
