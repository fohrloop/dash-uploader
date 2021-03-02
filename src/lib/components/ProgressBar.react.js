import React, {Component} from 'react'

class ProgressBar extends Component
{

constructor(props)
{
    super(props)
}

render()
{
    return (
    <div className="progress"
    style={{
        display: this.props.sdata.isUploading ? 'flex' : 'none',
        textAlign: 'center',
        marginTop: '10px',
        marginBottom: '10px',

    }}>



        <div className="progress-bar progress-bar-striped progress-bar-animated"
            style={{
                width: this.props.sdata.progressBar + '%',
                height: '100%'
            }}>

            <span className="progress-value"
                style={{
                    position: 'absolute',
                    right: 0,
                    left: 0,
                }}
            >{this.props.sdata.progressBar.toFixed(2) + '%'}</span>

        </div>
    </div>
    )
}
}

export default ProgressBar