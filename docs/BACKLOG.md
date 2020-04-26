# Backlog

This page lists some possible improvements for the package, if someone has time to implement them some day.

### More styles

It would be cool to have more different style options / themes for the component. The user should not have to know any CSS to change the style.

### Refactoring Upload_ReactComponent.react.js
The React code really would benefit on some refactoring. There is some repetitive code and the file should be cleaned.

### Adding progress bar

It would be nice to see a progress bar during the upload process.

### Simultaneous uploads

The resumable.js seems to have a option for multiple simultaneous uploads. Did not include this since have no time to test it actually works like it should. 

### Handling cases when filename exists

Should implement some logic for the situation when a file with same filename is uploaded again. Currently, if the file is larger than one chunk, the file chuncks are uploaded but the file is not replaced and no errors are shown.

### Forcing unique upload folders

Currently, multiple users can select the same upload folder and can upload files with same names simultaneously, which obviously will not work. There should be same simple logic to prevent this. Maybe random temporary folders?

### Improve testing
Testing is a waste of time. Until.. 