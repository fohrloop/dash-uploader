import React,{Component} from 'react'

class CreatePauseButton extends Component
{
    constructor(props)
    {
        super(props)
        {
        }
    }

render()
{

    return(

    <div style={{ display: 'inline-block', }}>
        <button
            style={{
                cursor: this.props.sdata.isUploading ? 'pointer' : 'default',
            }}
            disabled={!this.props.sdata.isUploading}
            className="resumable-btn-pause btn btn-sm btn-outline-secondary"
            onClick={this.props.pauseUpload}>
            {this.props.pdata.pauseButton
                && (this.props.sdata.isPaused ? 'resume' : 'pause')}
        </button>
    </div>
    )
}
}

export default CreatePauseButton