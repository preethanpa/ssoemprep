import logging
from base64 import b64decode

from dateutil import parser
from requests import Session
from xlsxwriter.utility import xl_col_to_name

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO
import json
import uuid
import sys
import logging

from trir.query_runner import *
from trir.utils import json_dumps, json_loads



logger = logging.getLogger(__name__)

try:
    from fonduer.parser.models import Document, Sentence, Table
    from fonduer.parser.preprocessors import HTMLDocPreprocessor
    from fonduer.parser import Parser
    from pprint import pprint

    from fonduer import Meta, init_logging

    from fonduer.candidates import CandidateExtractor
    from fonduer.candidates import MentionNgrams
    from fonduer.candidates import MentionExtractor 

    from fonduer.candidates.models import Mention
    from fonduer.candidates.models import mention_subclass
    from fonduer.candidates.models import candidate_subclass

    from fonduer.candidates.matchers import RegexMatchSpan, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union

    from fonduer.features import Featurizer    
    
    enabled = True
except ImportError:
    enabled = False

def _load_key(filename):
    with open(filename, "rb") as f:
        return json_loads(f.read())


def _get_columns_and_column_names(row):
    column_names = []
    columns = []
    duplicate_counter = 1

    return columns, column_names


def _value_eval_list(row_values, col_types):
    value_list = []
    raw_values = zip(col_types, row_values)
    for typ, rval in raw_values:
        try:
            value_list.append(val)
        except (ValueError, OverflowError):
            value_list.append(rval)
    return value_list


HEADER_INDEX = 0


class PageNotFoundError(Exception):
    def __init__(self, worksheet_num, worksheet_count):
        message = "Worksheet number {} not found. Spreadsheet has {} worksheets. Note that the worksheet count is zero based.".format(
            worksheet_num, worksheet_count
        )
        super(WorksheetNotFoundError, self).__init__(message)


def parse_query(query):
    values = query.split("|")
    key = values[0]  # key of the spreadsheet
    worksheet_num = (
        0 if len(values) != 2 else int(values[1])
    )  # if spreadsheet contains more than one worksheet - this is the number of it

    return key, worksheet_num


def parse_worksheet(worksheet):
    if not worksheet:
        return {"columns": [], "rows": []}

    columns, column_names = _get_columns_and_column_names(worksheet[HEADER_INDEX])

    if len(worksheet) > 1:
        for j, value in enumerate(worksheet[HEADER_INDEX + 1]):
            columns[j]["type"] = guess_type(value)

    column_types = [c["type"] for c in columns]
    rows = [
        dict(zip(column_names, _value_eval_list(row, column_types)))
        for row in worksheet[HEADER_INDEX + 1:]
    ]
    data = {"columns": columns, "rows": rows}

    return data


def parse_pdf(pdf_file_name, worksheet_num):
    if worksheet_num >= worksheet_count:
        raise WorksheetNotFoundError(worksheet_num, worksheet_count)

    worksheet = worksheets[worksheet_num].get_all_values()

    return parse_worksheet(worksheet)


def is_url_key(key):
    return key.startswith("https://")


def parse_api_error(error):
    error_data = error.response.json()

    if "error" in error_data and "message" in error_data["error"]:
        message = error_data["error"]["message"]
    else:
        message = str(error)

    return message


class TimeoutSession(Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 300)
        return super(TimeoutSession, self).request(*args, **kwargs)


class PortableDocumentFormatFile(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(PortableDocumentFormatFile, self).__init__(configuration)
        self.syntax = "custom"
        self.userapikey = configuration.userapikey

    @classmethod
    def name(cls):
        return "Portable Document Format File"

    @classmethod
    def type(cls):
        return "pdf_files"

    @classmethod
    def enabled(cls):
        return enabled

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {"pdfFile": {"type": "string", "title": "PDF Files"}},
            "required": ["pdfFile"],
        }

    def _get_pdf_service(self):
        scope = ["/home/dsie/Developer/sandbox/3ray/data/excel/"+self.userapikey+"/"]

        key = json_loads(b64decode(self.configuration["jsonKeyFile"]))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key, scope)

        timeout_session = Session()
        timeout_session.requests_session = TimeoutSession()
        spreadsheetservice = gspread.Client(auth=creds, session=timeout_session)
        spreadsheetservice.login()
        return spreadsheetservice

    def test_connection(self):
        service = self._get_spreadsheet_service()
        test_spreadsheet = "/home/dsie/Developer/sandbox/3ray/data/excel/tryaspose.xls"
        try:
            # Open an excel file
            workbook = Workbook("/home/dsie/Developer/sandbox/3ray/data/excel/tryaspose.xls")

            # Set scroll bars
            workbook.getSettings().setHScrollBarVisible(False)
            workbook.getSettings().setVScrollBarVisible(False)
        except APIError as e:
            message = parse_api_error(e)
            raise Exception(message)

    def run_query(self, query, user):
        logger.debug("Spreadsheet is about to execute query: %s", query)
        key, worksheet_num = parse_query(query)

        try:
            # Open an excel file
            workbook = Workbook("/home/dsie/Developer/sandbox/3ray/data/excel/tryaspose.xls")

            # Set scroll bars
            workbook.getSettings().setHScrollBarVisible(False)
            workbook.getSettings().setVScrollBarVisible(False)

            data = parse_spreadsheet(spreadsheet, worksheet_num)

            return json_dumps(data), None
        except gspread.SpreadsheetNotFound:
            return (
                None,
                "Spreadsheet ({}) not found. Make sure you used correct id.".format(
                    key
                ),
            )
        except APIError as e:
            return None, parse_api_error(e)





register(PortableDocumentFormatFile)
