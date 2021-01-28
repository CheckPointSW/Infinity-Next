# IoT Firmware Scanner Utility

A small Python-based tool to help scan firmware files and view reports using the Check Point IoT Firmware Scanner.

## First time installation

### Interpreter

To use the scanner utility, you must have Python 3 and the pip packages listed in the requirements.txt file.

### An API key

If you don't have one yet, create a Check Point portal account here: https://portal.checkpoint.com/create-account. Once your account is set up, log in to it and go to the Global Settings page (button on the bottom left). Click on API Keys -> New and under "Service" select "IoT Firmware Scanning". Expiration as you wish. *Make sure to save the credentials you're shown as they will not be shown again once you close the popup*.
Set the environment variables SCANNER_CLIENT_ID and SCANNER_ACCESS_KEY to the values of your client id and secret key, respectively.

Alternatively, although not recommended, you can place them in a file (by default, ".iotcreds") next to the scanner tool like so:

```
clientId=<client id>
accessKey=<secret key>
```

For example:
```
clientId=9433aa0ea3a8c93a
accessKey=a8c93ad03ea0ea34343ad5
```

This method is not recommended because it means your credentials will be stored unencrypted on disk.


### Metadata

Create a file (by default, ".iotmeta") containing the following structure for any metadata you'd like placed with the scan. This metadata will later appear in the report itself, or help you query previous scans for insights in the future.
```
deviceType=Vacuum
vendor=Example vendor
deviceModel=T-1000
version=1.1-rc1
tags=custom_tag1,custom_tag2
deleteFwAfterScan=False
disclaimer=False
```

The only mandatory fields are *version*, *deviceType*, and *disclaimer*, but each of the fields is useful for visibility and for query slicing.
*NOTE* Due to legal reasons, disclaimer defaults to False and must explicitly be set to True for the scan to proceed. This API is a wrapper for the web UI and the disclaimer corresponds to the checkbox confirming you own the firmware or have permission from the owner to scan it.


## Usage

The tool has two primary functions: uploading a firmware to be scanned, and getting a report for a scanned firmware.
To initiate a scan:
```
$ ./scanner upload <firmware filename>
```

This will automatically authenticate using your API token and upload the firmware file to the scanner service. The final output (if successful) will include a scanId which is used to retrieve your report later on.

To retrieve a report:
```
$ ./scanner get <scan id>
```

Scans take a while to finish. Depending on the size of your firmware, this could take a couple of minutes or up to 2 hours before the analysis is complete. Once the scan is finished, this will retrieve and save the PDF report. You can optionally retrieve other report formats by using the --format switch.

Enjoy :)
For questions or comments contact iot-device-security@checkpoint.com
