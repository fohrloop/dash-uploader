# Changelog

## 0.7.0-a1 (2022-03-30)

- This pre-release is available in PyPI with `--pre` flag.
- [0.6.0 → 0.7.0 Migration Guide](https://github.com/fohrloop/dash-uploader/wiki/Migration-Guide#060--070).

### Fixed
- Calling callback each time file is uploaded in multi-file upload case (Fixes: [#5](https://github.com/fohrloop/dash-uploader/issues/5), [#20](https://github.com/fohrloop/dash-uploader/issues/20) & [#44](https://github.com/fohrloop/dash-uploader/issues/44))
- Progress bar problems when uploading multiple files (Fixes: [#84](https://github.com/fohrloop/dash-uploader/issues/84))
- Instead of returing `None`, raise `dash.exceptions.PreventUpdate`. This should reduce errors seen in the browser console. [PR 54](https://github.com/fohrloop/dash-uploader/pull/54)
- Fixed  `ImportError` which was raised when trying to import `dash_uploader` when `packaging` was not installed. [PR 54](https://github.com/fohrloop/dash-uploader/pull/54)
### Changed 
- resumable.js -> flowjs (Closes: [#21](https://github.com/fohrloop/dash-uploader/issues/21))
- ⚠️ **Backwards incompatible**: Callback syntax (@du.callback) was changed to use `status` instead of `filenames` as the callback function argument. Support for `@app.callback` syntax dropped. See the [0.6.0 -> 0.7.0 Migration Guide](https://github.com/fohrloop/dash-uploader/wiki/Migration-Guide#060--070) for details.
- ⚠️**Backwards incompatible**: Changed the CSS class of the component to be `dash-uploader-completed`,  instead of `dash-uploader-complete`, when upload is completed. 

## v.0.6.0 (2021-09-19)
### Added 
- New `chunk_size`, `disabled` and `text_disabled` parameters for `du.Upload`. [Issue 41](https://github.com/fohrloop/dash-uploader/issues/41)

### Changed 
- Added the `prevent_initial_call=True` for all `du.callback`s. For [Dash >= 1.12.0](https://community.plotly.com/t/dash-v1-12-0-release-pattern-matching-callbacks-fixes-shape-drawing-new-datatable-conditional-formatting-options-prevent-initial-call-and-more/38867).

### Fixed
- Changing the parameter `disableDragAndDrop` by callbacks does not take effects. [PR 42](https://github.com/fohrloop/dash-uploader/pull/42)

## v.0.5.0 (2021-04-25)
### Added 
- [`du.HttpRequestHandler`](./dash-uploader.md#duhttprequesthandler) which allows for custom HTTP POST and GET request handling. For example, custom validation logic is now possible! Used through `http_request_handler` parameter of [`du.configure_upload`](./dash-uploader.md#duconfigure_upload).
### Changed 
- ⚠️ **Backwards incompatible changes**: Changed the CSS classes of the component to be `dash-uploader-default`, `dash-uploader-uploading`, .. etc. instead of `resumable-default`, `resumable-uploading`. 

## v.0.4.2 (2021-02-20)
- Fixed some width related CSS issues in mobile mode. See: [#19](https://github.com/fohrloop/dash-uploader/issues/19)
  
## v.0.4.1 (2020-10-27)
### Fixed
- max_files parameter to du.Upload did not have effect (Related [issue](https://github.com/fohrloop/dash-uploader/issues/12))
  
## v.0.4.0 (2020-10-27)
### Fixed
- Now dash-uploader works with `url_base_pathname` set in `app = dash.Dash(__name__, server=server, url_base_pathname='/somebase/')` . (Related [issue](https://github.com/fohrloop/dash-uploader/issues/15))
### Other
- Javascript updates (includes security updates)

## v.0.3.1 (2020-08-04)
### Fixed
- Importing `dash-uploader` with `dash` versions `<1.11.0` was not possible. (Related [issue](https://github.com/fohrloop/dash-uploader/issues/9))
### Security
- Javascript package security updates.
  
## v.0.3.0 (2020-06-06)
### Added 
- New [`@du.callback`](dash-uploader.md#ducallback) decorator for simple callback creation.   
- Experimental `max_files` parameter for `du.Upload`.
- Support for proxies; i.e. If app is running on `http://server.com/myapp`, and dash application is configured using `requests_pathname_prefix=myapp`, this is handled automatically by the Upload component. Fixes [#3](https://github.com/fohrloop/dash-uploader/issues/3).
### Fixed
- Uploading file with same name multiple times is now possible.
## v.0.2.4 (2020-06-05)
### Added
- Possibility to determine the uploader component API endpoint using the `upload_api` argument of the `configure_upload` function. 
  
## v.0.2.0 (2020-05-25)
### Added
- Upload folder for each file defined with a upload id (`upload_id`), which may be defined by the user.
### Fixed
- Uploading file with similar name now overwrites the old file (previously, file chunks were uploaded, but never merged.)
- Removed potential cause of infinite wait
  
## v.0.1.2 (2020-05-22)
### Added
- Progressbar
### Changed
- Loosened `dash` requirements;  `dash~=0.11.0` -> `dash>=1.1.0`.
- `activeStyle` replaced with `uploadingStyle`.
  
  
## v.0.1.1 (2020-05-18)
### Fixed
- Callback will now fired even multiple files are uploaded in a row. (Related [Issue](https://github.com/fohrloop/dash-uploader/issues/1))
  
## v.0.1.0 (2020-04-06)
- Initial release based on the [dash-resume-upload](https://github.com/westonkjones/dash-uploader) (0.0.4).

### Changed
- Restarted project basing on the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate)
- Hiding "Pause" and "Cancel" buttons when not uploading
### Added
- Clean, documented python interface for `Upload`
