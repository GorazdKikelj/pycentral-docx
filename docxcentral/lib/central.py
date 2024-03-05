# -*- coding: utf-8 -*-
"""
    Author: Gorazd Kikelj
    
    gorazd.kikelj@gmail.com
    
"""
from time import sleep
from pycentral.base import ArubaCentralBase
from pycentral.configuration import Groups
from pycentral.monitoring import Sites
from icecream import ic
from docxcentral.logwriter import log_writer
import base64
import json

"""
pycentral general functions

"""


def get_central_data(central, apipath: str, apiparams: dict = {"offset": 0}) -> dict:
    """
    Retrive prepared data from Aruba Central Instance

    Return : dictionary

        Retrived data is returned as dictionary

    Parameters:

    apipath: str
        REST API URL for returnig data

    apiparams: dict
        Parameters required for data filtering


    """
    apiPath = apipath
    apiMethod = "GET"
    apiParams = apiparams
    base_resp = central.command(
        apiMethod=apiMethod, apiPath=apiPath, apiParams=apiParams
    )
    if base_resp["code"] >= 400:
        if base_resp["code"] == 404:
            log_writer.error(
                f"Retrying GET request for {apiPath} status code {base_resp['code']} Not found"
            )
            return base_resp.get("msg")

        log_writer.warning(
            f"Retrying GET request for {apiPath} status code {base_resp['code']} {base_resp['msg'].get('detail')}"
        )
        sleep(2)
        base_resp = central.command(
            apiMethod=apiMethod, apiPath=apiPath, apiParams=apiParams
        )
        log_writer.warning(
            f"Retried GET request for {apiPath} status code {base_resp['code']} {base_resp['msg'].get('detail')}"
        )

    return base_resp.get("msg")


def post_central_data(central, apipath: str, apidata: dict = {}) -> dict:
    """
    Submit data collection request to Aruba Central Instance

    Return: dictionary

        Return call result as dictionary

    Parameters:

    apipath: str
        REST API URL path for called function

    apidata: dict
        JSON debug commands

        {
            "device_type": "IAP",
            "commands": [
                            {
                                "command_id": 115,
                                "arguments": [
                                                {
                                                    "name": "",
                                                    "value": ""
                                                }
                                            ]
                            }
                        ]
        }

    """
    apiPath = apipath
    apiMethod = "POST"
    apiData = apidata
    base_resp = central.command(apiMethod=apiMethod, apiPath=apiPath, apiData=apiData)
    if base_resp["code"] >= 400:
        log_writer.warning(
            f"Retrying POST request for {apiPath} status code {base_resp['code']}"
        )
        sleep(2)
        base_resp = central.command(
            apiMethod=apiMethod, apiPath=apiPath, apiData=apiData
        )
        log_writer.warning(
            f"Retried POST request for {apiPath} status code {base_resp['code']}"
        )

    return base_resp["msg"]


def connect_to_central(central_info: dict) -> None:
    """
    Establish connection with Aruba Central instance

    Return: None

    Parameters:

    central_info : dict
        {
            "base_url": "< Central Instance API gateway URL >",
            "customer_id": "< Aruba Central Customer ID >",
            "client_id": "< API Token Client ID >",
            "client_secret": "< API Token Client Secret >",
            "username": "< GreenLake Username >",
            "password": "< GreenLake Password >"
        }
    or
        {
            "base_url": "< Central Instance API gateway URL >,
            "token": {
                        "access_token": "< Aruba Central REST API Access Token >",
                        "refresh_token": "< Aruba Central REST API Refresh Token >",
                     }
        }
    """
    token_store = {"type": "local", "path": "token"}
    central = ArubaCentralBase(
        central_info=central_info,
        token_store=token_store,
        ssl_verify=True,
    )
    return central


def get_per_ap_settings(central, serial_no) -> dict:
    """
    Return status data for specific AP
    """
    apipath = f"/configuration/v1/ap_settings_cli/{serial_no}"
    return get_central_data(central=central, apipath=apipath)


#    ap_data = get_central_data(central=central, apipath=apipath)
#
#    if isinstance(ap_data, dict):
#        return ap_data.get("aps")
#    return None


def get_per_ap_config(central, serial_no) -> dict:
    """
    Return current AP configuration
    """
    return get_central_data(
        central=central,
        apipath=f"/configuration/v1/devices/{serial_no}/configuration",
        apiparams={"limit": 0},
    )


"""
pycentral VisualRF

visualrf_api = "/visualrf_api/v1/"

"""
visualrf_api = "/visualrf_api/v1/"


def get_campus_id(central) -> dict:
    return get_central_data(
        central=central, apipath=f"{visualrf_api}campus", apiparams={"offset": 0}
    )


def get_buildings(central, campus_id) -> dict:
    return get_central_data(
        central=central,
        apipath=f"{visualrf_api}campus/{campus_id}",
        apiparams={"offset": 0},
    )


def get_floors(central, building_id) -> dict:
    return get_central_data(
        central=central,
        apipath=f"{visualrf_api}building/{building_id}",
        apiparams={"offset": 0, "units": "METERS"},
    )


def get_floor_data(central, floor_id) -> dict:
    return get_central_data(
        central=central,
        apipath=f"{visualrf_api}floor/{floor_id}/access_point_location",
        apiparams={"offset": 0, "units": "METERS"},
    )


def get_floor_image(central, floor_id) -> any:
    return base64.b64decode(
        get_central_data(
            central=central,
            apipath=f"{visualrf_api}floor/{floor_id}/image",
            apiparams={"offset": 0},
        ),
        validate=True,
    )


def save_floorplan_ap_location(central, ap_id):
    api_path = f"/visualrf/location.png?id={ap_id}"
    base_resp = central.command(
        apiMethod="GET", apiPath=api_path, apiParams={"offset": 0}
    )

    ic(api_path, base_resp)
    try:
        with open(f"images/ap['ap_name'].jpg", "wb") as f:
            f.write(base64.b64decode(base_resp))
    except TypeError:
        pass

    return None


def save_floorplans(central, central_info) -> dict:
    campuses = get_campus_id(central=central)
    floor_dict = {}
    buildings = get_buildings(
        central=central, campus_id=campuses["campus"][0]["campus_id"]
    )
    param_info = central_info
    param_info["base_url"] = "https://app-eucentral3.central.arubanetworks.com"
    ic(param_info)
    ap_location_pictures = connect_to_central(central_info=param_info)
    ic(ap_location_pictures)
    for building in buildings["buildings"]:
        floors = get_floors(central=central, building_id=building["building_id"])
        for floor in floors["floors"]:
            floor_dict[floor["floor_name"]] = {
                "floor_id": floor["floor_id"],
                "ap": {},
            }
            img = get_floor_image(central=central, floor_id=floor["floor_id"])
            with open(
                f"images/{building['building_name']}_floor_{floor['floor_level']}.png",
                "wb",
            ) as f:
                f.write(img)

            floor_data = get_floor_data(central=central, floor_id=floor["floor_id"])
            for ap in floor_data["access_points"]:
                floor_dict[floor["floor_name"]]["ap"].update(
                    {ap["ap_name"]: ap["ap_id"]}
                )
                save_floorplan_ap_location(
                    central=ap_location_pictures, ap_id=ap["ap_id"]
                )

    return floor_dict


def get_rf_groups(central, group_name) -> list:
    apipath = f"/configuration/v1/dot11a_radio_profiles/{group_name}"
    return get_central_data(central=central, apipath=apipath)


def get_central_groups(central) -> list:
    g = Groups()
    group_list = g.get_groups(central)["msg"]

    return group_list.get("data")


def get_wlan_list(central, group_name) -> dict:
    apipath = f"/configuration/full_wlan/{group_name}"
    data = get_central_data(central=central, apipath=apipath)
    if type(data) is dict:
        return data.get("description")
    return json.loads(data)


def get_sites(central) -> list:
    s = Sites()
    site_list = s.get_sites(central)["msg"]
    return site_list.get("sites")


"""

Originalne funkcije iz create_docx.py

(g) 5.3.2024

def get_central_data(central, apipath, apiparams={"offset": 0}):
    apiPath = apipath
    apiMethod = "GET"
    apiParams = apiparams or " "
    base_resp = central.command(
        apiMethod=apiMethod, apiPath=apiPath, apiParams=apiParams
    )
    return base_resp["msg"]


def get_campus_id(central) -> dict:
    return get_central_data(
        central=central, apipath=visualrf_api + "campus", apiparams={"offset": 0}
    )


def get_buildings(central, campus_id) -> dict:
    return get_central_data(
        central=central,
        apipath=visualrf_api + f"campus/{campus_id}",
        apiparams={"offset": 0},
    )


def get_floors(central, building_id) -> dict:
    return get_central_data(
        central=central,
        apipath=visualrf_api + f"building/{building_id}",
        apiparams={"offset": 0, "units": "METERS"},
    )


def get_floor_data(central, floor_id) -> dict:
    return get_central_data(
        central=central,
        apipath=visualrf_api + f"floor/{floor_id}/access_point_location",
        apiparams={"offset": 0, "units": "METERS"},
    )


def save_floorplans(central) -> dict:
    campuses = get_campus_id(central=central)
    floor_dict = {}
    buildings = get_buildings(
        central=central, campus_id=campuses["campus"][0]["campus_id"]
    )
    for building in buildings["buildings"]:
        floors = get_floors(central=central, building_id=building["building_id"])
        for floor in floors["floors"]:
            floor_dict[floor["floor_name"]] = {
                "floor_id": floor["floor_id"],
                "ap": {},
            }
            img = base64.b64decode(
                get_central_data(
                    central=central,
                    apipath=f"/visualrf_api/v1/floor/{floor['floor_id']}/image",
                    apiparams={"offset": 0},
                ),
                validate=True,
            )
            with open(
                f"images/{building['building_name']}_floor_{floor['floor_level']}.png",
                "wb",
            ) as f:
                f.write(img)

            floor_data = get_floor_data(central=central, floor_id=floor["floor_id"])
            for ap in floor_data["access_points"]:
                floor_dict[floor["floor_name"]]["ap"].update(
                    {ap["ap_name"]: ap["ap_id"]}
                )
    return floor_dict


def get_rf_groups(central, group_name) -> list:
    apipath = f"/configuration/v1/dot11a_radio_profiles/{group_name}"
    return get_central_data(central=central, apipath=apipath)


def get_central_groups(central) -> list:
    g = Groups()
    group_list = g.get_groups(central)["msg"]

    return group_list.get("data")


def get_wlan_list(central, group_name) -> dict:
    apipath = f"/configuration/full_wlan/{group_name}"
    data = get_central_data(central=central, apipath=apipath)
    if type(data) is dict:
        return data.get("description")
    return json.loads(data)


def get_sites(central) -> list:
    s = Sites()
    site_list = s.get_sites(central)["msg"]
    return site_list.get("sites")


def get_per_ap_settings(central, serial_no) -> list:
    #    apimethod = "GET"
    apipath = f"/configuration/v1/ap_settings_cli/{serial_no}"
    return get_central_data(central=central, apipath=apipath)

"""
