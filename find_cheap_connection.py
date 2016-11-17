from bahn import BahnAPI
import datetime
import tabulate
from urllib.parse import urlencode
api = BahnAPI()
def pprint_connction(connection, traveler):
	date = datetime.datetime.strftime(connection["departure"]["time"], "%d.%m.%y")
	time = datetime.datetime.strftime(connection["departure"]["time"], "%H:%M")
	data = {"S":connection["departure"]["stop"]["name"],
	"Z":connection["arrival"]["stop"]["name"],
	"date":date,
	"time":time,
	"timesel":"depart",
	"tariffTravellerType.1":BahnAPI().traveler_types[traveler[0]],
	"tariffTravellerReductionClass.1":BahnAPI().redtnCards[traveler[1]],
	"start":"1"}
	url = "https://reiseauskunft.bahn.de/bin/query.exe/dn?" + urlencode(data)
	dauer = connection["duration"]
	umstiege = len(connection["sections"])-1
	abfahrt = connection["departure"]["time"]
	ankunft = connection["arrival"]["time"]
	return [dauer, umstiege, abfahrt, ankunft, url]
CONNECTIONS_TO_COLLECT = 6
START = "Dortmund"
END = "Leipzig"
TRAVELERS = [("adult", ""), ("adult", "25_2"), ("adult", "50_2")]
START_TIME = datetime.datetime(2016, 5, 1)
MODE = "live"
print("Downloading connections")
cons = []
for traveler in TRAVELERS:
	if MODE == "live":
		res = api.searchTrip(START, END, travelers=[traveler], start_datetime=START_TIME)
		connections = res["results"]
		while connections[-1]["arrival"]["time"] - START_TIME < datetime.timedelta(hours = 2):
			res = api.searchTrip(START, END, travelers=TRAVELERS, ctx=res["ctx_later"])
			connections+=res["results"]
		with open("connections_test.json","w") as connectionsfile:
			connectionsfile.write(str(connections))
	else:
		raise Exception("Mode invalid")
	for i,connection in enumerate(connections):
		preis = sorted(["ab "+str(x["price"]) if x["isFromPrice"] else str(x["price"]) for x in connection["fares"] ])[0]
		cons.append((preis, traveler, connection))
cons.sort(key=lambda x: x[0])
final_cons = [[x[0], x[1][1], *pprint_connction(x[2], x[1])] for x in cons]
headers = ["Preis", "Bahncard", "Dauer", "Umstiege", "Abfahrtszeit", "Ankunftszeit", "URL"]
print(tabulate.tabulate(final_cons, headers, tablefmt="psql"))
