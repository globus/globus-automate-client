Globus SDK and CLI for Automate
===============================

This is an experimental, and unsupported interface for working with Globus Automate tools, notably the Globus Flows service and any service implementing the Action Provider interface.

As this is experimental, no support is implied or provided for any sort of use of this package. It is published for ease of distribution among those planning to use it for its intended, experimental, purpose.

Basic Usage
-----------

Install with ``pip install globus-automate-client``

This will install an executable script ``globus-automate``. Run the script without arguments to get a summary of the sub-commands and their usage.

Use of the script to invoke any services requires authentication. Upon first interaction with any Action Provider or the Flows Service, you will be prompted to proceed through an Authentication process using Globus Auth to consent for use by the CLI with the service it is interacting with. This typically only needs to be done once, the first time a service is invoked. Subsequently, the cached authentication information will be used. Authentication information is cached in the file ``$HOME/.globus_token_cache``. It is recommended that this file be protected, and deleted when experimentation with the services is complete.
