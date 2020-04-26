# CONTRIBUTING

Feel free to contribute. I have made some development related instructions below. This package was created using [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate) and contains some automatically generated files, too.

## How to improve this package?

Maybe you already have an idea. If not, there is also a list for development ideas in the [BACKLOG.md](BACKLOG.md).
## For developers
### Setting up development environment
- Clone this repository. Change current directory to project root.
- Install [npm and Node.js](https://nodejs.org) for building JS.
- Install the JS dependencies by running `npm install` on the project root. This will create `node_modules` directory.
- Create python virtual environment and activate it
- `pip install` this package in editable state
```
python -m pip install -e <path_to_this_folder>
```

### Running demo page
1. Run `python usage.py`
2. Visit http://127.0.0.1:8050/ in your web browser

### Package structure


**Highlights**
```
dash_uploader/
  * python source code of this package
    __init__.py
  _build/
    * Auto-generated python & JS code
    * Do not edit these by hand!
      _imports_.py
      <Component>.py <-- for each component
      dash_uploader.min.js
      dash_uploader.min.js.map
      metadata.json
      package-info.json
    
devscripts/
  * used during "npm run build"
  
src/
  demo/
    * Example JS demo. Just for testing React code
      with "npm start"
  lib/
    * React components (The JS/React source code)

package.json
  * Defines JS dependencies
  * Defines npm scripts

usage.py
  * Example file
  * Run with `python usage.py`
```
**Other**
```
assets/
  * Assets just for the demo (usage.py)
index.html
  * Needed for testing (with npm run)
inst/
  * Some kind of intermediate storage for JS files 
    (before copying to dash_uploader)
  * Automatically generated with "npm run build"
node_modules/
  * JS dependencies
  * Automatically created by "npm install"
venv/
  * python dependencies (virtual environment)
  * Created with "python -m venv venv"
```
### Developing
**What files should I edit?**<br>

- React code: The react.js files in `src/lib/components/`<br>
- Python code: The non-auto-generated files in `dash_uploader` 


### Building: React.js -> JS & Python
Run in the project root
```
npm run build
```
This will create all the auto-generated (JS, json, python) files into the `dash_uploader/_build` folder.


### Testing React components without python
- Before creating the "python/Dash" versions, it is possible to test the component(s) by
- Editing the content of `src/demo/index.js`, if you wish.
- Then, running
```
npm start
```
- Then, go to url `http://127.0.0.1:55555`. 
- The url can be changed in the package.json -> scripts -> start, by changing the `host` argument to the [`webpack-serve`](https://www.npmjs.com/package/webpack-serve).
- **Note**: There is not handler for POST requests in the demo! (the Upload component will not work without a POST handler)

## More help?
Read also the automatically generated README text at [README-COOKIECUTTER.md](README-COOKIECUTTER.md).