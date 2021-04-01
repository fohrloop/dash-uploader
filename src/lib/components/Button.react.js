import React, { Component } from 'react'

class Button extends Component {

    constructor(props) {
        super(props)
    }

    render() {

        return (
            <div style={{ display: 'inline-block', }}>
                <button
                    style={{
                        cursor: this.props.isUploading ? 'pointer' : 'default',
                    }}
                    disabled={this.props.disabled}
                    className={this.props.btnClass + " btn btn-sm btn-outline-secondary"}
                    onClick={this.props.onClick}>
                    {this.props.text}
                </button>
            </div >
        )
    }
}


Button.propTypes = {
    /**
     *  The text on the button 
     */
    text: PropTypes.string,
    /**
     *  The CSS class for the button
     */
    btnClass: PropTypes.string,
    /**
     *  Function to call when clicked
     */
    onClick: PropTypes.func,
    /**
     *  Is disabled, the component
     * is not shown.
     */
    disabled: PropTypes.bool,
    /**
     *  Is true, the parent component
     *  has upload in progress.
     */
    isUploading: PropTypes.bool,
}

Button.defaultProps = {
    text: '',
    btnClass: 'dash-uploader-btn',
    onClick: () => { },
    disabled: false,
    isUploading: false,

};

export default Button