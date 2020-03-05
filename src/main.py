"""Teads Extractor.

usage: main.py [-h] [-f CONFIG] [-o OUTPATH] [-l {INFO,WARN,ERROR,DEBUG}]

optional arguments:
  -h, --help            show this help message and exit
  -f CONFIG, --config CONFIG
                        Filename of the config JSON, default ../config.json
  -o OUTPATH, --outpath OUTPATH
                        Output dir, default ../output
  -l {INFO,WARN,ERROR,DEBUG}, --loglevel {INFO,WARN,ERROR,DEBUG}
"""
import os
import sys
import csv
import json
import requests

from logging import getLogger, basicConfig, INFO
from argparse import ArgumentParser
from datetime import datetime, timedelta
from slugify import slugify
from time import sleep

RESPONSE_BUFFER = 16*1024

def main():
    """Main function to run extraction
    """
    # Argument parser
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--config", action="store", default="../config.json",
                            help="Filename of the config JSON,\ndefault ../config.json")
    argparser.add_argument("-o", "--outpath", action="store", default="../output",
                            help="Output dir,\ndefault ../output")
    argparser.add_argument("-l", "--loglevel", action="store",
                            default="INFO", choices=["INFO", "WARN", "ERROR", "DEBUG"])

    args = argparser.parse_args()

    # Logger
    basicConfig(
        level=INFO, format="[{asctime}] {levelname}: {message}", style="{")
    logger = getLogger(__name__)
    logger.setLevel(args.loglevel)

    # Config path
    config_path = args.config

    if not os.path.exists(config_path):
        raise Exception(
            "Configuration not specified, was expected at '{}'".format(config_path))

    with open(config_path, encoding="utf-8") as conf_file:
        conf = json.load(conf_file)["parameters"]

    # Request report id
    url_request_report = "https://api.teads.tv/v1/analytics/custom"

    payload = json.dumps(conf["report_config"])

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer {}".format(conf["#auth"])
        }

    session = requests.Session()

    response = session.post(url_request_report, data=payload, headers=headers)
    if not str(response.status_code).startswith("2"):
        raise Exception("Status: {0} \nResponse: {1}".format(response.status_code, response.text))

    resp = response.json()
    if not "id" in resp:
        raise Exception(resp["msg"])

    report_request_id = resp["id"]
    logger.info("Report id: %s", report_request_id)
    

    # Request report
    url_get_report_uri = "{0}/{1}".format(url_request_report, report_request_id)
    headers = {"authorization": "Bearer {}".format(conf["#auth"])}

    while True:
        response = session.get(url_get_report_uri, data="", headers=headers)
        resp = response.json()
        if resp["status"]!="processing" and resp["status"]!="queued":
            break
        s = 10
        logger.info("Report status: %s, retry after %ds", resp["status"], s)
        sleep(s)

    if resp["status"]!="finished":
        raise Exception("Report did not finish succesfully, status: {0} \n{1}".format(resp["status"], resp["message"]))

    report_uri = resp["uri"]
    logger.info("Report status: %s \nReport uri: %s", resp["status"], report_uri)
    

    # Save csv from report uri
    output_path = args.outpath
    os.makedirs(output_path, exist_ok=True)

    output_fname = os.path.join(output_path, "{}.csv".format(slugify(conf["report_name"])))

    r = session.get(report_uri, stream=True)
    with open(output_fname, "wb") as outfile:
        for chunk in r.iter_content(chunk_size=RESPONSE_BUFFER):
            outfile.write(chunk)

if __name__ == "__main__":
    main()