# Teads Extractor

## Description

Extractor for pulling data from Teads into .csv files.
The extractor downloads data based on the list of `dimensions` to query by and the list of `metrics` to return specified in `config.json`. Data can be filtered by various filters specified in `config.json`. All the filters except for the date are optional. The date (i.e. lower-bound timestamp and upper-bound timestamp in the ISO8601 format and the timezone) must be specified as in the `sample-config.json`.
It is possible to send the report to e-mail addresses specified in the `emails` list in `config.json`.

See [Teads API documentation](https://teadsapi.docs.apiary.io) for further details.

## Requirements

Teads API token

## How to use it

Create or modify `config.json` file as described in `sample-config.json`.

### Config explanation

| Parameter | Type | Description |
| --- | --- | --- |
| #auth | string | Bearer token |
| dimensions | list of strings | dimensions to query by |
| metrics | list of strings | metrics to return |
| filters | list of strings/dict | all the filters extept for date default to empty array |
| report_name | string | report name |
| email | list | list of emails |
