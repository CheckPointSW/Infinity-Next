#!/usr/bin/env python3

import os
import argparse
import requests
import io
import sys
import hashlib

from datetime import datetime
from distutils import util


KILOBYTE                    = 1024
MEGABYTE                    = KILOBYTE * KILOBYTE
CHUNK_SIZE                  = MEGABYTE * 2  # Customizeable chunk size
DEFAULT_CREDS_FILENAME      = ".iotcreds"
DEFAULT_IOT_META_FILENAME   = ".iotmeta"
TIME_FORMAT                 = "%H:%M:%S"
VERBOSITY                   = 0
CLOUDINFRA_URL              = "https://cloudinfra-gw.portal.checkpoint.com"
IOT_SCANNER_URL             = f"{CLOUDINFRA_URL}/app/iotfirmware/v2"


class APIClient:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file

    def get_creds(self):
        client_id = os.getenv("SCANNER_CLIENT_ID", None)
        access_key = os.getenv("SCANNER_ACCESS_KEY", None)
        if client_id and access_key:
            return client_id, access_key

        print(f"Failed to detect credentials from environment variables, checking for credentials in file {self.credentials_file}...")

        configs = {"clientId" : None,
                   "accessKey" : None}

        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "rt") as fd:
                content = fd.read().splitlines()
                for configline in content:
                    try:
                        key, value = configline.split("=")
                        if key not in configs.keys():
                            print(f"Error: Configuration file {self.credentials_file} contains unknown configuration: '{key}'. Expected one of: {configs.keys()}")
                            return None, None
                        else:
                            configs[key] = value
                    except Exception as e:
                        print(f"Error: Configuration file {self.credentials_file} malformed or empty, cannot retrieve credentials.\nLine: {configline}\nException details: {e}")
                        return None, None
                return configs["clientId"], configs["accessKey"]
        else:
            print(f"Error: Configuration file {self.credentials_file} not found, cannot retrieve credentials.")
            return None, None

    def chunk_generator(self, filename, chunk=CHUNK_SIZE):
        with open(f"{filename}", "rb") as file_obj:
            while True:
                data = file_obj.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    def authenticate(self, client_id = None, access_key = None):
        if client_id is None or access_key is None:
            client_id, access_key = self.get_creds()
            if client_id is None or access_key is None:
                return False

        try:
            response = requests.post(f"{CLOUDINFRA_URL}/auth/external",
                                     headers={"Content-Type" : "application/json"},
                                     json={"accessKey" : access_key, "clientId" : client_id})
            success = response.json()["success"]
            if success is False:
                message = response.json()["message"]
                print(f"Error authenticating to Check Point portal. Error details: '{message}'")
                self.authorization = None
                return False
            self.authorization = response.json()["data"]["token"]
            return True
        except Exception as e:
            self.authorization = None
            print(f"Error authenticating to Check Point portal: {e}")
            print("Response content: %s" % (response.json()))
            return False

    def send_chunk(self, filename, file_chunk, file_hash, total_chunks, chunk_index, deviceType = "", vendor = "", deviceModel = "", version = "", tags = "", disclaimer = False, deleteFwAfterScan = False, **kwargs):
        url = f"{IOT_SCANNER_URL}/upload"
        headers = {"Authorization" : f"Bearer {self.authorization}"}

        payload = {
            "deviceType" : deviceType,
            "vendor" : vendor,
            "deviceModel" : deviceModel,
            "version" : version,
            "tags" : tags,
            "disclaimer" : disclaimer,
            "deleteFwAfterScan" : deleteFwAfterScan,
            "fileHash": file_hash,
            "totalChunks": total_chunks,
            "chunkIndex": chunk_index
        }

        wrapped_chunk = (filename, io.BytesIO(file_chunk).read())
        files = {"file": wrapped_chunk}
        response = requests.post(url, headers=headers, files=files, data=payload)
        try:
            parsed_response = response.json()
            if response.status_code == 200:
                return parsed_response

            if parsed_response.get("success", None) is None:
                return parsed_response
            else:
                print("Failed to send file chunk")
                if parsed_response["message"] == "Authentication required":
                    print("Missing authentication. Trying to re-auth and resend...")
                    if self.authenticate() is True:
                        headers = {"Authorization" : f"Bearer {self.authorization}"}
                        wrapped_chunk = (filename, io.BytesIO(file_chunk))
                        files = {"file": wrapped_chunk}
                        response = requests.post(url, headers=headers, files=files, data=payload)
                        parsed_response = response.json()
                        return parsed_response
                    else:
                        print("Error: Failed to authenticate and retrieve an access token; cannot send file chunk.")
                        return None
        except Exception as e:
            print(f"Encountered exception while sending chunk. Exception details: <{e}>")
            return None

        return parsed_response

    def scan_file(self, filename, metadata):
        now1 = datetime.now()
        initialization = now1.strftime(TIME_FORMAT)

        if not os.path.isfile(metadata):
            choice = input(f"Metadata file {metadata} not found. Would you like to create one now manually? [y/N] ")
            if choice.lower() == "y":
                success, metadata = create_metadata_file(metadata)
                if not success:
                    return
            else:
                print("Aborting upload.")
                return

        try:
            meta_dictionary = {
                "deviceType"        : "",
                "vendor"            : "",
                "deviceModel"       : "",
                "version"           : "",
                "tags"              : [],
                "disclaimer"        : True,
                "deleteFwAfterScan" : False
            }
            with open(metadata, "rt") as fd:
                data = fd.read().splitlines()

            for metaparam in data:
                metaparam = metaparam.split("=")
                if len(metaparam) != 2:
                    print(f"Invalid line in metadata file: {metaparam}")
                    print("Expected key=value (no spaces)")
                    return
                metaparam_name = metaparam[0]
                metaparam_value = metaparam[1]
                if metaparam_name in meta_dictionary.keys():
                    meta_dictionary[metaparam_name] = metaparam_value

            if meta_dictionary["version"] == "":
                print("Error: 'version' field empty or not found in metadata file.")
                return

            if meta_dictionary["deviceType"] == "":
                print("Error: 'deviceType' field empty or not found in metadata file.")
                return

            if not isinstance(meta_dictionary["deleteFwAfterScan"], bool):
                meta_dictionary["deleteFwAfterScan"] = bool(util.strtobool(meta_dictionary["deleteFwAfterScan"]))

            tags = meta_dictionary["tags"]
            if tags != []:
                tags = tags.split(",")
                meta_dictionary["tags"] = tags
        except Exception as e:
            print(f"Error reading metadata file '{metadata}': {e}")
            print("Aborting upload.")
            return

        print(f"Request initiated at {initialization}")
        file_hash = hashlib.sha256()
        try:
            with open(filename, "rb") as uploaded_file:
                data = uploaded_file.read(2 * MEGABYTE)
                while data:
                    file_hash.update(data)
                    data = uploaded_file.read(2 * MEGABYTE)
        except Exception as e:
            print(f"Failed to read target file '{filename}': {e}")
            return

        filesize = os.stat(filename).st_size
        total_chunks = filesize // CHUNK_SIZE
        if filesize % CHUNK_SIZE != 0:
            total_chunks += 1

        chunk_index = 0
        self.authenticate()
        for file_chunk in self.chunk_generator(filename):
            chunk_index += 1
            response = self.send_chunk(filename,
                                       file_chunk,
                                       file_hash.hexdigest(),
                                       str(total_chunks),
                                       str(chunk_index),
                                       **meta_dictionary)
            if response is not None:
                if response.get("chunkStatus", False) is True:
                    if VERBOSITY >= 1:
                        print(f"Chunk {chunk_index}/{total_chunks} sent.")
                else:
                    error_message = response.get("message", response)
                    print(f"Chunk {chunk_index}/{total_chunks} issue: {error_message}")
                if response.get("scanId", "") != "":
                    print("Scan initiated. Save the scan ID for later:")
                    print(response["scanId"])
        now2 = datetime.now()
        completion = now2.strftime(TIME_FORMAT)
        print(f"Request completed at {completion}")

        timedelta = now2 - now1
        print(f"Total request time: {timedelta}")

    def retrieve_report(self, scan_id, format, output_filepath = None):
        if output_filepath is None:
            output_filepath = f"{scan_id}.{format}"

        url = f"{IOT_SCANNER_URL}/reports?scanId={scan_id}&reportType={format}"
        if self.authenticate() is False:
            print("Failed to authenticate, aborting report retrieval.")
            return

        try:
            response = requests.get(url, headers = {"Authorization" : f"Bearer {self.authorization}"})

            # The next block requires some explanation:
            # There are 2-3 cases here:
            # Assuming we got a 200 OK, this is a valid response from our server and so we'll only get an exception if we try to convert a non-json response to json.
            # 1. We only get 200 OK + a non-json response in the case where the analysis was completed and the response
            #    is the raw data of the report file itself. In this case, we need to ignore the exception and save the response content.
            # 2. We only get 200 OK + a json response in the case where the analysis did not complete: it's in progress or errored out.
            #    In this case, we parse the scan status and print it out.
            # 3. If we didn't get a 200 OK, the response may be json (in case it's an error reported by the backend) or non-json in case
            #    of an unknown unknown. In this case, we'd like to show the error and fail.
            try:
                if response.status_code == 200:  # Case #2: The server is telling us "I got your request, but the scan isn't ready yet".
                    scan_status = response.json()["scanStatus"]
                    print(f"Scan status: {scan_status}")
                    return
                else:  # Case #3: There was an error, we need to show it and fail.
                    try:
                        parsed_response = response.json()
                        print(f"Bad response from server: {parsed_response}")
                    except Exception as e:
                        print(f"Unexpected response from server: {response.content}")

                    return
            except Exception as e:  # Case #1: We got the report file. We're in an exception because we tried to read a raw data file as if it were a json response. Save the report.
                with open(output_filepath, "wb") as fd:
                    fd.write(response.content)
                print(f"Report saved as {output_filepath}")

        except Exception as e:
            print(f"Failed to retrieve report from server for scanId {scan_id}. Error: {e}")
            return


def create_metadata_file(filename):
    new_filename = input(f"Enter filename to hold the metadata or leave blank for default ({filename}) ")
    if new_filename == "":
        new_filename = filename

    version = input("*Mandatory* Input firmware version (for example, 1.0-rc1): ")
    if version == "":
        return False, ""
    device_type = input("*Mandatory* Input device type (for example, Medical, Security, Smart home, IP Camera, etc): ")
    if device_type == "":
        return False, ""
    vendor = input("Input vendor or leave blank for no vendor: ")
    device_model = input("Input device model or leave blank for no model: ")
    tags = input("Input comma-separated tags or leave blank for no tags (for example: custom_tag1,custom_tag2,custom_tag3): ")
    deleteFwAfterScan = input("Delete firmware after scan? [y/N] ")
    if deleteFwAfterScan == "":
        deleteFwAfterScan = "False"
    disclaimer = input('Do you confirm that you own the firmware or have permission from the owner to run the scan? Type "yes": ')
    if disclaimer == "yes":
        disclaimer = "True"
    else:
        disclaimer = "False"

    with open(new_filename, "wt") as fd:
        fd.write(f"deviceType={device_type}\n")
        fd.write(f"vendor={vendor}\n")
        fd.write(f"version={version}\n")
        fd.write(f"deviceModel={device_model}\n")
        fd.write(f"tags={tags}\n")
        fd.write(f"deleteFwAfterScan={deleteFwAfterScan}\n")
        fd.write(f"disclaimer={disclaimer}\n")

    return True, new_filename


def create_credentials_file(filename):
    new_filename = input(f"Enter filename to hold the credentials or leave blank for default ({filename}) ")
    if new_filename == "":
        new_filename = filename
    client_id = input("Input client ID: ")
    access_key = input("Input access key: ")

    if client_id == "" or access_key == "":
        print("Cannot skip mandatory fields. Failed to create credentials file. Aborting.")
        return False, ""

    try:
        with open(new_filename, "wt") as fd:
            fd.write(client_id)
            fd.write("\r\n")
            fd.write(access_key)
            return True, new_filename
    except Exception as e:
        print(f"Error trying to save credentials file: {e}")
        print("Failed to create credentials file. Aborting.")
        return False, ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Utility to peform firmware scans utilizing Check Point's cloud-based IoT Firmware Scanner")

    subparsers = parser.add_subparsers(help="Possible commands", dest="subcommand")

    # Available sub-commands are "upload" and "get"
    upload_parser   = subparsers.add_parser("upload", help = "Upload a file to be scanned")
    get_parser      = subparsers.add_parser("get", help = "Get a report for a previously scanned file")

    # "upload" sub-command parser
    upload_parser.add_argument("file", help = "File to be scanned")
    upload_parser.add_argument("--metadata", "-m", help = "File containing metadata for the firmware: vendor name, device model, etc.", default=DEFAULT_IOT_META_FILENAME)

    # "get" sub-command parser
    get_parser.add_argument("scan_id", help = "The scan ID of a file previously sent for scanning")
    get_parser.add_argument("--format", "-f", help = "File format of report", choices=["pdf", "json"], default="pdf")
    get_parser.add_argument("--output", "-o", help = "Output file name", default=None)

    # General arguments
    parser.add_argument("--credentials-file", "-c", help = "Name of file to take credentials from", default=DEFAULT_CREDS_FILENAME)
    parser.add_argument("--verbose", "-v", help = "Verbose", default=0, action="count")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(-1)

    VERBOSITY = args.verbose
    client = APIClient(args.credentials_file)
    client_id, access_key = client.get_creds()
    if client_id is None or access_key is None:
        print(f"Malformed credentials or no credentials file found (expected \"{client.credentials_file}\")")
        choice = input("Would you like to create it now? [Y/n] ").lower()
        if choice == "" or choice == "y":
            success, credentials_file = create_credentials_file(client.credentials_file)
            if success is False:
                sys.exit(-1)
            else:
                client = APIClient(credentials_file)
        else:
            print("Cannot proceed without credentials file. Aborting.")
            sys.exit(-1)

    # Currently, we support "upload" and "get" modes:
    # This is "upload"
    if args.subcommand == "upload":
        print(f"Sending file {args.file} to be scanned...")
        client.scan_file(args.file, args.metadata)
    # This is "get"
    elif args.subcommand == "get":
        print(f"Retrieving report for ID {args.scan_id}")
        client.retrieve_report(args.scan_id, args.format, args.output)
    else:
        parser.print_usage()
        sys.exit(-1)
