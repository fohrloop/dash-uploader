# Changelog

### v.0.2.4 (2020-06-05)
- Added possibility to determine the uploader component API endpoint using the `upload_api` argument of the `configure_upload` function. 
  
### v.0.2.0 (2020-05-25)
- Upload folder for each file defined with a upload id (`upload_id`), which may be defined by the user.
- Bugfix: Uploading file with similar name now overwrites the old file (previously, file chunks were uploaded, but never merged.)
- Removed potential cause of infinite wait
  
### v.0.1.2 (2020-05-22)
- Added progressbar
- Loosened `dash` requirements;  `dash~=0.11.0` -> `dash>=1.1.0`.
- `activeStyle` replaced with `uploadingStyle`.
  
  
### v.0.1.1 (2020-05-18)
- Bugfix: Callback will now fired even multiple files are uploaded in a row. (Related [Issue](https://github.com/np-8/dash-uploader/issues/1))
  
### v.0.1.0 (2020-04-06)
- Initial release based on the [dash-resume-upload](https://github.com/westonkjones/dash-uploader) (0.0.4).
- Restarted project basing on the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate)
- Added clean, documented python interface for `Upload`
- Hiding "Pause" and "Cancel" buttons when not uploading