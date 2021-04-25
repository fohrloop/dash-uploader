import React, { Component } from 'react';

class CreateStartButton extends Component
{

constructor(props){
    super(props)
}

render()
{
return(
    <div style={{display: 'inline-block'}}>
        <button
            style={{cursor: this.props.sdata.isUploading? 'pointer' : 'default',}}
            disabled={this.props.pdata.isUploading}
            className="resumable-btn-start btn btn-sm btn-outline-secondary"
            onClick={this.props.upload}>{this.props.pdata.startButton && 'upload'}
        </button>
    </div>
)
}
}

export default CreateStartButton