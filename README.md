
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
```

The example above shows a remote URL to a COPC file.  Inside jupyter, this extension can also render local files relative to the notebook.  

```python
import eptium

w = eptium.Eptium()
w.render("./path/to/file.copc.laz")
```

The `render` method supports other optional arguments to customize the view.  Run `help(w.render)` to see the possible options.

Note: the local file functionality is not present in google colab.
