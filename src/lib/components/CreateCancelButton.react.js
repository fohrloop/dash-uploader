import React,{Component} from 'react'

class CreateCancelButton extends Component
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
            className="resumable-btn-cancel btn btn-sm btn-outline-secondary"
            onClick={this.props.cancelUpload}>{this.props.pdata.cancelButton && 'cancel'}
        </button>
    </div>
    )
}
}

export default CreateCancelButton