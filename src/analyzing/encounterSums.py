import csv

from utils import getAnalysisDataPath, getEncounterDataPath


def checkRateSum(fname_read, fname_write, versionCodes, timeDependent=False):
    with open(fname_read, 'r', newline='', encoding='utf-8') as readCSV, open(fname_write, 'w', newline='', encoding='utf-8') as writeCSV:
        reader = csv.DictReader(readCSV)
        writer = csv.writer(writeCSV)
        if not timeDependent:
            writer.writerow(['Version Code', 'Location',
                            'Sub-location', 'Method', 'Sum'])
        else:
            writer.writerow(['Version Code', 'Location', 'Sub-location',
                            'Method', 'Morning Sum', 'Day Sum', 'Night Sum'])

        # {
        #   versionCode {
        #     location {
        #       subLocation {
        #         method {
        #           pokemonName {
        #             morning: rate string
        #             day: rate string
        #             night: rate string
        #           }
        #         }
        #       }
        #     }
        #   }
        # }
        locationDict = {}
        for row in reader:
            location, subLocation, pokemon, method = row["Location"], row[
                "Sub-location"], row["Pokemon"], row["Method"]

            for versionCode in versionCodes:
                relevant = row[versionCode] == 'True'

                # If row doesn't hold true for versionCode, move on
                if not relevant:
                    continue

                # Make new entry in locationDict if necessary
                if versionCode not in locationDict.keys():
                    locationDict[versionCode] = {}
                if location not in locationDict[versionCode].keys():
                    locationDict[versionCode][location] = {}
                if subLocation not in locationDict[versionCode][location].keys():
                    locationDict[versionCode][location][subLocation] = {}
                if method not in locationDict[versionCode][location][subLocation].keys():
                    locationDict[versionCode][location][subLocation][method] = {
                    }
                if pokemon not in locationDict[versionCode][location][subLocation][method].keys():
                    locationDict[versionCode][location][subLocation][method][pokemon] = {
                        'morning': '0%',
                        'day': '0%',
                        'night': '0%',
                    }

                # If not timeDependent, only one rate
                if not timeDependent:
                    rate = row["Rate"]
                    locationDict[versionCode][location][subLocation][method][pokemon]["morning"] = rate
                    locationDict[versionCode][location][subLocation][method][pokemon]["day"] = rate
                    locationDict[versionCode][location][subLocation][method][pokemon]["night"] = rate
                else:
                    newMorningRate, newDayRate, newNightRate = row[
                        "Morning Rate"], row["Day Rate"], row["Night Rate"]
                    if newMorningRate != '0%':
                        locationDict[versionCode][location][subLocation][method][pokemon]["morning"]
                    if newDayRate != '0%':
                        locationDict[versionCode][location][subLocation][method][pokemon]["day"]
                    if newNightRate != '0%':
                        locationDict[versionCode][location][subLocation][method][pokemon]["night"]

        for versionCode, locationData in locationDict.items():
            for location, subLocationData in locationData.items():
                for subLocation, methodData in subLocationData.items():
                    for method, pokemonData in methodData.items():
                        morningSum = 0
                        daySum = 0
                        nightSum = 0
                        for pokemon, rateData in pokemonData.items():
                            # Morning
                            morningRate = rateData["morning"]
                            try:
                                morningSum += int(morningRate[:-1])
                            except ValueError:
                                None

                            # Day
                            dayRate = rateData["day"]
                            try:
                                daySum += int(dayRate[:-1])
                            except ValueError:
                                None

                            # Night
                            nightRate = rateData["night"]
                            try:
                                nightSum += int(nightRate[:-1])
                            except ValueError:
                                None
                        if not isValidSum(morningSum):
                            if timeDependent:
                                writer.writerow(
                                    [versionCode, location, subLocation, method, morningSum, daySum, nightSum])
                            else:
                                writer.writerow(
                                    [versionCode, location, subLocation, method, morningSum])
    return


def isValidSum(rate):
    return rate == 0 or rate == 100


def main():
    # Gen 1
    checkRateSum(getEncounterDataPath() + 'encounters-rby.csv',
                 getAnalysisDataPath() + 'encounter-sums-rby.csv', ['R', 'B', 'Y'])
    # Gen 2
    checkRateSum(getEncounterDataPath() + 'encounters-gsc.csv',
                 getAnalysisDataPath() + 'encounter-sums-gsc.csv', ['G', 'S', 'C'], True)
    # Gen 3
    checkRateSum(getEncounterDataPath() + 'encounters-rse.csv',
                 getAnalysisDataPath() + 'encounter-sums-rse.csv', ['R', 'S', 'E'])
    checkRateSum(getEncounterDataPath() + 'encounters-frlg.csv',
                 getAnalysisDataPath() + 'encounter-sums-frlg.csv', ['FR', 'LG'])
    # Gen 4
    checkRateSum(getEncounterDataPath() + 'encounters-dppt.csv',
                 getAnalysisDataPath() + 'encounter-sums-dppt.csv', ['D', 'P', 'Pt'], True)
    checkRateSum(getEncounterDataPath() + 'encounters-hgss.csv',
                 getAnalysisDataPath() + 'encounter-sums-hgss.csv', ['HG', 'SS'], True)


if __name__ == '__main__':
    main()
