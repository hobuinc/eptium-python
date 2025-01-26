
# Eptium for Jupyter

A jupyter widget to display COPC and COGS data from Eptium.

## Installation

You can install using `pip`:

```bash
pip install eptium
```

## Usage

The following is an example on how to render data within the jupyter notebook environment

```python
import eptium

w = eptium.Eptium()
w.render("https://s3.amazonaws.com/hobu-lidar/autzen-classified.copc.laz")
w
```

The example above shows a remote URL to a COPC file.  Inside jupyter, this extension can also render local files relative to the notebook.  

```python
import eptium

w = eptium.Eptium()
w.render("./path/to/file.copc.laz")
w
```

The `render` method supports other optional arguments to customize the view.  Run `help(w.render)` to see the possible options.

Note: the local file functionality is not present in google colab.

## Development Installation

Create a dev environment:

```bash
conda create -n eptium-dev -c conda-forge nodejs python jupyterlab
conda activate eptium-dev
```

Install the python. This will also build the TS package.

```bash
pip install -e ".[test, examples]"
```

When developing your extensions, you need to manually enable your extensions with the
notebook / lab frontend. For lab, this is done by the command:

```bash
jupyter labextension develop --overwrite .
jlpm run build
```

For classic notebook, you need to run:

```bash
jupyter nbextension install --sys-prefix --symlink --overwrite --py eptium
jupyter nbextension enable --sys-prefix --py eptium
```

Note that the `--symlink` flag doesn't work on Windows, so you will here have to run
the `install` command every time that you rebuild your extension. For certain installations
you might also need another flag instead of `--sys-prefix`, but we won't cover the meaning
of those flags here.

### How to see your changes

#### Typescript

If you use JupyterLab to develop then you can watch the source directory and run JupyterLab at the same time in different
terminals to watch for changes in the extension's source and automatically rebuild the widget.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm run watch
# Run JupyterLab in another terminal
jupyter lab
```

After a change wait for the build to finish and then refresh your browser and the changes should take effect.

#### Python

If you make a change to the python code then you will need to restart the notebook kernel to have it take effect.

## Updating the version

To update the version, install tbump and use it to bump the version.
By default it will also create a tag.

```bash
pip install tbump
tbump <new-version>
```
