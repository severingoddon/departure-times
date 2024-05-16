import requests
from datetime import datetime
import time

class DepartureBoard:
    def __init__(self):
        self.base_url = "https://fpbe.zvv.ch/restproxy/departureBoard"
        self.access_id = "OFPubique"
        self.station_id = "A=1@O=Zürich, Limmatplatz@X=8531626@Y=47384595@U=85@L=8591257@B=1@p=1713265918@"
        self.max_journeys = 30

    def send_request(self):
        current_datetime = datetime.now()
        params = {
            "format": "json",
            "accessId": self.access_id,
            "type": "DEP_STATION",
            "duration": "1439",
            "id": self.station_id,
            "date": current_datetime.strftime('%Y-%m-%d'),
            "time": current_datetime.strftime('%H:%M'),
            "passlist": "1",
            "maxJourneys": str(self.max_journeys),
            "baim": "1"
        }
        while True:
            try:
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    print("Fehler beim Senden der Anfrage. Statuscode:", response.status_code)
            except requests.RequestException as e:
                with open('logfile.txt', 'a') as logfile:
                    logfile.write(f"Error is: {e}\n")
            time.sleep(2)


    def filter_departures(self, json_response, loadType):
        current_datetime = datetime.now()
        filtered_departures = []
        departures = json_response.get('Departure', [])
        for departure in departures:
            if 'rtDepTime' in departure:
                departure_time_str = departure['date'] + ' ' + departure['rtDepTime']
            elif 'rtTime' in departure:
                departure_time_str = departure['date'] + ' ' + departure['rtTime']
            else:
                departure_time_str = departure['date'] + ' ' + departure['time']
            departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d %H:%M:%S')
            if 'date' not in departure:
                departure_time = departure_time.replace(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day)
            if departure_time > current_datetime:
                name_parts = departure['name'].split()
                line_number = name_parts[1] if len(name_parts) > 1 else departure['name']
                direction = departure['direction']
                if direction == "Zürich, Bahnhof Altstetten N":
                    direction = "Zürich, Bahnhof Altstetten"
                time_difference = departure_time - current_datetime
                minutes_until_departure = round(time_difference.total_seconds() / 60)
                filtered_departures.append({"line": line_number, "direction": direction, "minutes_until_departure": minutes_until_departure})
        return self.filter_departure_direction(filtered_departures, loadType)

    def filter_departure_direction(self, prefiltered_departures, loadType):
        if loadType == 'hb':
            hbDepartures = []
            for dep in prefiltered_departures:
                if 'Tiefenbrunnen' in dep['direction']:
                    hbDepartures.append(dep)
                elif 'Bahnhofplatz' in dep['direction']:
                    hbDepartures.append(dep)
                elif 'Albisgütli' in dep['direction']:
                    hbDepartures.append(dep)
            hbDepartures.sort(key=lambda x: x['minutes_until_departure'])
            hbDepartures = hbDepartures[:9]
            return hbDepartures

        elif loadType == 'bus':
            busDepartures = []
            for dep in prefiltered_departures:
                if dep['line'] == '32':
                    busDepartures.append(dep)
            busDepartures.sort(key=lambda x: x['minutes_until_departure'])
            busDepartures = busDepartures[:9]
            return busDepartures

        else:
            eschDepartures = []
            for dep in prefiltered_departures:
                if 'Werdhölzli' in dep['direction']:
                    eschDepartures.append(dep)
                elif 'Frankental' in dep['direction']:
                    eschDepartures.append(dep)
                elif 'Altstetten' in dep['direction']:
                    eschDepartures.append(dep)
            eschDepartures.sort(key=lambda x: x['minutes_until_departure'])
            eschDepartures = eschDepartures[:9]
            return eschDepartures


    def get_departures(self, loadType):
        json_response = self.send_request()
        if json_response:
            return self.filter_departures(json_response, loadType)
        else:
            return None

if __name__ == "__main__":
    departure_board = DepartureBoard()
    departures = departure_board.get_departures("hb")
    if departures:
        for departure in departures:
            print(departure)

