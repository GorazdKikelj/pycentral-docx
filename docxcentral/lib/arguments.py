# -*- coding: utf-8 -*-
"""
    Author: Gorazd Kikelj
    
    gorazd.kikelj@gmail.com
    
"""
import argparse
import sys
from datetime import datetime
from dateutil import parser
from logging import getLevelName


from docxcentral import (
    C_DEBUG_LEVEL,
    C_EVENT_LIST,
    C_DATA_DIR,
    C_CSV_DELIMITER,
    C_CSV_SN_COLUMN,
    C_JSON_CENTRAL,
    C_JSON_FILTER,
    C_REQUIRED_KEYS,
)

from . import (
    get_ap_list_from_csv,
    get_filter_from_json,
    get_central_from_json,
    check_path,
)

from docxcentral.logwriter import log_writer, check_debug_level


def define_arguments():
    """
    This function defines a parser and help strings for script arguments.

    Returns:
        parser (ArgumentParser): A ArgumentParser varaible that contains all
                                 input parameters passed during script execution
    """
    parser = argparse.ArgumentParser(
        description="........ \
             Log collection App for Aruba Central REST API ....."
    )
    """
    parser.add_argument(
        "--csv_input",
        required=False,
        help="CSV input file containing list of AP serial numbers \
                        to collect data from. (optional)",
    )
    parser.add_argument(
        "--csv_sn_column",
        required=False,
        help="Column # or name where device Serial number is stored. \
                        (optional, default=0)",
        default=C_CSV_SN_COLUMN,
    )
    parser.add_argument(
        "--csv_delimiter",
        required=False,
        help="Column delimiter (optional, default=',')",
        default=C_CSV_DELIMITER,
    )
    """
    parser.add_argument(
        "--json_central",
        required=False,
        help="JSON file with Aruba Central Access Token (Optional, default=central.json)",
        default=C_JSON_CENTRAL,
    )
    parser.add_argument(
        "--json_filter",
        required=False,
        help="JSON file with group select filter (optional, default=filter.json)",
        default=C_JSON_FILTER,
    )

    parser.add_argument(
        "--customer_name",
        required=False,
        help="Custmer name for the document title page (optional, default=None)",
        default=None,
    )
    parser.add_argument(
        "--document_title",
        required=False,
        help="Document title (optional, default=None)",
        default=None,
    )
    parser.add_argument(
        "--event_list",
        required=False,
        help="Summary Output of all events (optional, default=event_list.txt)",
        default=C_EVENT_LIST,
    )
    parser.add_argument(
        "--data_directory",
        required=False,
        help=f"Directory for result files (optional, default={C_DATA_DIR})",
        default=C_DATA_DIR,
    )
    parser.add_argument(
        "--debug_level",
        required=False,
        help="Set debul level to [NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL]",
        default=C_DEBUG_LEVEL,
    )
    parser.add_argument(
        "--inverse_search",
        required=False,
        help="Inverse search condition. Return only devices not in input CSV or do not have event from filter.json present",
        default=False,
        action="store_true",
    )

    return parser


def process_arguments(args):
    """
    This function processes the input arguments supplied during script
    execution and stores them as param_dict variable.

    Returns:
        param_dict: A dictionary of key value pairs required for script exec.
    """
    param_dict = {}

    # Extract customer info from input JSON File

    debug_level = args.debug_level
    if debug_level:
        check_debug_level(debug_level)

    filter_file: str = args.json_filter
    param_dict: dict = param_dict | get_filter_from_json(filename=filter_file)
    log_writer.info(f'__Using group list from Aruba Central {param_dict["group_list"]}')

    central_file = args.json_central
    param_dict["central_info"] = get_central_from_json(filename=central_file)

    if args.customer_name:
        param_dict["customer"]["customer_name"] = args.customer_name
    if args.document_title:
        param_dict["customer"]["document_title"] = args.document_title

    log_writer.info(f'__Customer name: {param_dict["customer"]["customer_name"]}')
    log_writer.info(f'__Document Title: {param_dict["customer"]["document_title"]}')

    param_dict["event_file"] = {
        "filename": args.event_list,
        "directory": args.data_directory,
    }
    check_path(path=param_dict["event_file"]["directory"])
    log_writer.info(f'__Output Event file is {param_dict.get("event_file")}')

    param_dict["condition"] = {"inverse_search": args.inverse_search}
    log_writer.info(f"__Search conditions: {param_dict.get('condition')}")

    return param_dict


def validate_input_dict(inputDict, required_keys=C_REQUIRED_KEYS):
    """
    This function checks if all the required details provided in the input JSON file.
    """
    log_writer.info("Validating Input Dict...")

    # Check if required keys are present in the input
    input_key_error = []

    group_list = inputDict.get("group_list")

    error_str = ""
    if input_key_error:
        key_str = "{}".format(str(input_key_error))
        error_str = error_str + "\nError: " + key_str

    if error_str and error_str != "":
        log_writer.error(error_str)
        sys.exit(error_str)

    return None


def init_arguments() -> dict:
    """
    Initialize all parameters from input files.

    Return:
        Dictionary:

        param_dict: {'central_info': {'base_url': '',
                                  'client_id': '',
                                  'client_secret': '',
                                  'customer_id': '',
                                  'password': '',
                                  'username': ''},
                 'site_list': ['site_name'],
                 'group_list': ['group_name'],
                 'ap_filter': {'group': 'group name',
                                  'label': 'label',
                                  'site': 'site_name',
                                  'sort': '+serial',   #  -serial, +macaddr, -macaddr, +swarm_id, -swarm_id',
                                  'status': 'AP status',
                                  'serial': 'AP serial no',
                                  'macaddr': 'AP mac address',
                                  'model': 'AP model',
                                  'cluster_id': 'Mobility controller Serial no',
                                  }}

    """
    parser = define_arguments()
    args = parser.parse_args()
    param_dict = process_arguments(args)
    validate_input_dict(inputDict=param_dict)

    return param_dict
