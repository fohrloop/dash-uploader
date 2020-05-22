# Changelog

### v.0.1.2 (2020-05-22)
- Added progressbar
- Loosened `dash` requirements;  `dash~=0.11.0` -> `dash>=1.1.0`.
  
  
### v.0.1.1 (2020-05-18)
- Bugfix: Callback will now fired even multiple files are uploaded in a row. (Related [Issue](https://github.com/np-8/dash-uploader/issues/1))
  
### v.0.1.0 (2020-04-06)
- Initial release based on the [dash-resume-upload](https://github.com/westonkjones/dash-uploader) (0.0.4).
- Restarted project basing on the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate)
- Added clean, documented python interface for `Upload`
- Hiding "Pause" and "Cancel" buttons when not uploading