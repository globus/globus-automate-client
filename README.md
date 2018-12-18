# globus-automate-client
This repository contains:
1. Documentation for the APIs for the Globus Action Interface and for the Globus Flows Service.
2. Python3 API bindings for each of these APIs and a Command Line Interface (CLI) tool for using the Flow service or any Action directly.
3. A Jupyter Notebook which provides an overview and samples of the APIs and SDK in use. This notebook provides a good starting point for familiarizing oneself with the the Automate services and interfaces and to see the SDK in action (pun intended).

In the following sections, we describe the requirements and how to set up and use each of these 3 components of this repository.

## Documentation

Documentation is located in the `docs/` directory. Both HTML and OpenAPI versions of documentation for APIs for interacting with the Flows Service and the general purpose Action interface are provided. The HTML documentation is generated from the OpenAPI specification using the `redoc-cli`. Creating the HTML documentation is as follows:

### Prerequisites

`redoc-cli` is a `Node.js` utility. Therefore, `Node.js`, the `npm` package manager and the `npx` package runner must be pre-installed.

### Generating HTML documentation

When updates to the OpenAPI specification have been made, the corresponding HTML documents can be generated simply by running `make api-docs`. This will install the `Node.js` package `redoc-cli` if necessary, and will update the HTML to match the current state of the OpenAPI specification YAML file.

## SDK and CLI

### Building

The SDK and CLI are each Python3-based, so python3 must be available on your system. Build and dependency management is performed by [`poetry`](https://poetry.eustace.io/). It is recommended that `poetry` be installed outside the project directory as described [here](https://poetry.eustace.io/docs/#installation).

With `python3` and `poetry` installed, the CLI tool can be created by running `make install`. This will create a python3-based virtual environment in the directory `.venv` and will create a runnable tool called `globus-automate` in the virtual environment's `/bin` directory.

### Running the `globus-automate` CLI tool

With the command line tool built and installed, it can be executed either by running `.venv/bin/globus-automate` or `poetry run globus-automate`. Running this way, or with the `--help` option will display the set of sub-commands which are available for interacting with the Flows service or any Action which conforms to the Action API Specification.

## Jupyter Notebook

The Jupyter Notebook file `globus-automate.ipynb` provides a "walkthrough" of the basics of both the Flows and the Actions API including live interactions with each of these services. If Jupyter is already installed on your system, it can be loaded with `jupyter notebook`. If Jupyter is not installed, the `make install` command from above will install Jupyter into the local virtual environment. Jupyter can then be run with `.venv/bin/jupyter notebook` or `poetry run jupyter notebook`. The Jupyter notebook will be launched in a new browser window/tab. The `globus-automate.ipynb` notebook can be selected from the initial list in the browser which will launch it in a new browser tab.
