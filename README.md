# py-jugaad-aws

The Jugaad libraries are designed to be minimalist but effective in providing essential frameworks to help build multi-tenant SaaS platforms.

The python libraries in this package ease development of APIs and event driven apps for AWS serverless architecture and is primarily tested with AWS Chalice framework.

## Usage Guide

### Logging

```
from jugaad_aws import log
logger = log.STLogger.getLogger(__name__)
logger.info("useful logs...")
```
The logger instance created above is same as the logger instance available from the package `logging`

### App Configuration

```
from jugaad_aws import config
testvalue = config.getStaticConfig("testKey","DEFAULT_VALUE")
testDynValue = config.getDynamicConfig("testDynKey","DEFAULT_VALUE")
```
The config instance has two main methods:

* `getStaticConfig` - This method looks for the provided configuration key (`testKey` in the example above) in the following sequence:
    * Under the specific path within AWS Parameter Store - `/APP_CONFIG_STATIC/<App Name>/`. The app name is read from a `config.ini` file present under the app root folder.
    * Environment variable
    * A `config.ini` under the root folder of the app.
An optional `DEFAULT_VALUE` can be provided to the method to return the default if the configuration is not found in any of the mentioned locations.

* `getDynamicConfig` - This method looks for the provided configuration key (`testDynKey` in the example above) from the AWS Parameter Store - `/APP_CONFIG_DYNAMIC/<App Name>`. The app name is read from a `config.ini` file present under the app root folder.

### HTTP Client

### Middleware
