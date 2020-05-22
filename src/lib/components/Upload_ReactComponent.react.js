// v.0.1.0. https://github.com/np-8/dash-uploader 
// 
// Credits:
// This file is based on following repositories
// v.0.0.3 from https://github.com/rmarren1/dash-uploader
// v.0.0.4 from https://github.com/westonkjones/dash-uploader

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Resumablejs from 'resumablejs';
import './progressbar.css';
import './button.css';

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
        this.resumable = null;
    }

    resetBuilder() {
        this.setState(Upload_ReactComponent.initialState)
    }

    componentDidMount() {

        const ResumableField = new Resumablejs({
            target: this.props.service,
            query: {},
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
            isCompleted: false
        });
        // Clicking the component will open upload dialog 
        ResumableField.assignBrowse(this.uploader);

        // Enable or Disable DragAnd Drop
        if (this.props.disableDragAndDrop === false) {
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
                    isCompleted: true
                });
            }
            this.setState({
                fileList: { files: currentFiles },
                isComplete: true,
                showEnabledButtons: false,
                messageStatus: this.props.completedMessage + file.fileName || fileServer
            }, () => {
                if (typeof this.props.onFileSuccess === 'function') {
                    this.props.onFileSuccess(file, fileServer);
                }
            });
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
                console.log('fileError with resumable.js! (file, errorCount)', file, errorCount)
            }

        });

        this.resumable = ResumableField;
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

    render() {

        const fileList = null;

        let textLabel = null;
        if (this.props.textLabel) {
            textLabel = this.props.textLabel;
        }

        let startButton = null;
        if (this.props.startButton) {
            if (typeof this.props.startButton === 'string' || typeof this.props.startButton === 'boolean') {
                startButton = <div style={{ display: 'inline-block', }}>
                    <button
                        style={{
                            cursor: this.state.isUploading ? 'pointer' : 'default',
                        }}
                        disabled={this.state.isUploading}
                        className="resumable-btn-start btn btn-sm btn-outline-secondary"
                        onClick={this.startUpload}>{this.props.startButton && 'upload'}
                    </button>
                </div>;
            }
            else { startButton = this.props.startButton }
        }

        let cancelButton = null;
        if (this.props.cancelButton && this.state.showEnabledButtons) {
            if (typeof this.props.cancelButton === 'string' ||
                typeof this.props.cancelButton === 'boolean') {
                cancelButton = <div style={{ display: 'inline-block', }}>
                    <button
                        style={{
                            cursor: this.state.isUploading ? 'pointer' : 'default',
                        }}
                        disabled={!this.state.isUploading}
                        className="resumable-btn-cancel btn btn-sm btn-outline-secondary"
                        onClick={this.cancelUpload}>{this.props.cancelButton && 'cancel'}
                    </button>
                </div>;
            }
            else { cancelButton = this.props.cancelButton }
        }

        let pauseButton = null;
        if (this.props.pauseButton && this.state.showEnabledButtons) {
            if (typeof this.props.pauseButton === 'string'
                || typeof this.props.pauseButton === 'boolean') {
                pauseButton = <div style={{ display: 'inline-block', }}>
                    <button
                        style={{
                            cursor: this.state.isUploading ? 'pointer' : 'default',
                        }}
                        disabled={!this.state.isUploading}
                        className="resumable-btn-pause btn btn-sm btn-outline-secondary"
                        onClick={this.pauseUpload}>
                        {this.props.pauseButton
                            && (this.state.isPaused ? 'resume' : 'pause')}
                    </button>
                </div>;
            }
            else { pauseButton = this.props.pauseButton }
        }

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
                                'width': '0.1px%',
                                'height': '0.1px%',
                                'position': 'absolute',
                                'overflow': 'hidden',
                                'zIndex': '-1',
                            }}
                        />
                    </label>
                    <div className="progress"
                        style={{
                            display: this.state.isUploading ? 'flex' : 'none',
                            textAlign: 'center',
                            marginTop: '10px',
                            marginBottom: '10px',

                        }}>



                        <div className="progress-bar progress-bar-striped progress-bar-animated"
                            style={{
                                width: this.state.progressBar + '%',
                                height: '100%'
                            }}>

                            <span className="progress-value"
                                style={{
                                    position: 'absolute',
                                    right: 0,
                                    left: 0,
                                }}
                            >{this.state.progressBar.toFixed(2) + '%'}</span>

                        </div>
                    </div>
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
    isCompleted: PropTypes.bool

}

Upload_ReactComponent.defaultProps = {
    maxFiles: 1,
    maxFileSize: 1024 * 1024 * 10,
    chunkSize: 1024 * 1024,
    simultaneuosUploads: 1,
    service: '/API/resumable',
    className: 'resumable-default',
    hoveredClass: 'resumable-hovered',
    completeClass: 'resumable-complete',
    disabledClass: 'resumable-disabled',
    pausedClass: 'resumable-paused',
    uploadingClass: 'resumable-uploading',
    defaultStyle: {},
    uploadingStyle: {},
    completeStyle: {},
    textLabel: 'Click Here to Select a File',
    completedMessage: 'Complete! ',
    fileNames: [],
    filetypes: undefined,
    startButton: true,
    pauseButton: true,
    cancelButton: true,
    disableDragAndDrop: false,
    id: 'default-uploader-id',
    onUploadErrorCallback: undefined,
    isCompleted: false,
};
