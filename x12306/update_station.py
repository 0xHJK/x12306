import requests
import re

DEFAULT_BASE_URL = "https://kyfw.12306.cn/otn/leftTicket"
DEFAULT_STATION_URL = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"


def update_station(path: str = "./x12306/data/stations.txt") -> None:
    # update station information
    init_url = DEFAULT_BASE_URL + "/init"
    response = requests.get(init_url)
    if response.status_code == 200:
        pattern = re.compile(r"station_version=([\d\.]+)")
        station_version = pattern.search(response.text)
        if station_version:
            print(f"Station version: {station_version.group(1)}")
            station_url = (
                DEFAULT_STATION_URL + f"?station_version={station_version.group(1)}"
            )

            response = requests.get(station_url)
            if response.status_code == 200:
                pattern = re.compile(r"var station_names ='(.*?)';")
                station_names = pattern.search(response.text)
                if station_names:
                    # utf-8 encoding
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(station_names.group(1))
                    print(f"Station information saved to {path}")
                else:
                    print("Failed to retrieve the station information.")
                    print(response.text)
            else:
                print(
                    f"Failed to retrieve the page. Status code: {response.status_code}"
                )
        else:
            print("Station version not found.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


if __name__ == "__main__":
    update_station()
