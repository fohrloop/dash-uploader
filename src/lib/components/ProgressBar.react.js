import React, { Component } from 'react'

import PropTypes from 'prop-types';

/**
 *  A ProgressBar component. 
 *  Used as a part of Upload component.
 */
class ProgressBar extends Component {

    constructor(props) {
        super(props)
    }

    render() {
        return (
            <div className="progress"
                style={{
                    display: this.props.isUploading ? 'flex' : 'none',
                    textAlign: 'center',
                    marginTop: '10px',
                    marginBottom: '10px',

                }}>



                <div className="progress-bar progress-bar-striped progress-bar-animated"
                    style={{
                        width: this.props.progressBar + '%',
                        height: '100%'
                    }}>

                    <span className="dash-uploader-progress-value"
                        style={{
                            position: 'absolute',
                            right: 0,
                            left: 0,
                        }}
                    >{this.props.progressBar.toFixed(2) + '%'}</span>

                </div>
            </div >
        )
    }
}


ProgressBar.propTypes = {
    /**
     *  The progressbar value 
     */
    progressBar: PropTypes.number,
    /**
     *  The upload status (boolean)
     */
    isUploading: PropTypes.bool,
}

ProgressBar.defaultProps = {
    progressBar: 0,
    isUploading: false,
};


export default ProgressBar