from datetime import datetime
import requests

class DepartureBoardNew:
    def __init__(self):
        self.url = "https://search.ch/fahrplan/api/stationboard.json"
        self.params = {
            "stop": "Limmatplatz",
            "limit": 30,
            "show_delays": 1,
            "show_subsequent_stops": 1
        }

    def send_request(self):
        response = requests.get(self.url, params=self.params)
        return response.json()

    def filter_departures(self, json_response, loadType):
        filtered_departures = []
        departures = json_response.get('connections', [])
        for departure in departures:
            delay = 0
            if 'dep_delay' in departure:
                delay = int(departure['dep_delay'].strip("+"))
            current_time = datetime.now()
            departure_time = datetime.strptime(departure['time'], "%Y-%m-%d %H:%M:%S")
            minutes_until_departure = int((departure_time - current_time).total_seconds() / 60) + delay
            line_number = departure['line']
            direction = departure['terminal']['name']
            if direction == "Zürich Altstetten, Bahnhof Nord":
                direction = "Zürich, Bahnhof Altstetten"
            next_stop = departure['subsequent_stops'][0]['name']
            filtered_departures.append(
                {"line": line_number, "direction": direction, "minutes_until_departure": minutes_until_departure,
                 "next_stop": next_stop})
        return self.filter_departure_direction(filtered_departures, loadType)

    def filter_departure_direction(self, prefiltered_departures, loadType):
        if loadType == 'hb':
            hbDepartures = []
            for dep in prefiltered_departures:
                if 'Museum' in dep['next_stop']:
                    hbDepartures.append(dep)
            hbDepartures.sort(key=lambda x: x['minutes_until_departure'])
            hbDepartures = hbDepartures[:9]
            return hbDepartures

        elif loadType == 'bus':
            busDepartures = []
            for dep in prefiltered_departures:
                if dep['line'] == '32':
                    busDepartures.append(dep)
                if dep['line'] == 'N12':
                    busDepartures.append(dep)
            busDepartures.sort(key=lambda x: x['minutes_until_departure'])
            busDepartures = busDepartures[:9]
            return busDepartures

        else:
            eschDepartures = []
            for dep in prefiltered_departures:
                if 'Quellenstrasse' in dep['next_stop']:
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
    departure_board = DepartureBoardNew()
    departures = departure_board.get_departures("esch")
    if departures:
        for departure in departures:
            print(departure)