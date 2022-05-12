import csv

from scraping import makeEncounterCSV
from utils import getDataPath, openLink, parseName


def main():
    dataPath = getDataPath()
    fname_dppt = dataPath + 'encounters-dppt.csv'
    fname_hgss = dataPath + 'encounters-hgss.csv'
    fname_none = dataPath + 'none-gen4.csv'

    with open(fname_dppt, 'w', newline='', encoding='utf-8') as csvFile_rse, open(fname_hgss, 'w', newline='', encoding='utf-8') as csvFile_frlg, open(fname_none, 'w', newline='', encoding='utf-8') as csvFile_none:
        writer_dppt = csv.writer(csvFile_rse)
        writer_dppt.writerow(['Location', 'Sub-location', 'Pokemon', 'D', 'P',
                             'Pt', 'Method', 'Levels', 'Morning Rate', 'Day Rate', 'Night Rate'])
        writer_hgss = csv.writer(csvFile_frlg)
        writer_hgss.writerow(
            ['Location', 'Pokemon', 'HG', 'SS', 'Method', 'Levels', 'Morning Rate', 'Day Rate', 'Night Rate'])
        writer_none = csv.writer(csvFile_none)
        writer_none.writerow(['Version Group Code', 'Location', 'Reason'])

        # Navigate to link
        bs = openLink(
            'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_IV)', 0, 10)

        # Section where desired table is
        findSection = bs.find('h1', id=f'firstHeading')

        # Desired table (nested within an outer table)
        findTable = findSection.findNext('table')
        makeEncounterCSV(
            findTable, {'DPPt': writer_dppt, 'HGSS': writer_hgss, 'None': writer_none}, 'IV')


if __name__ == '__main__':
    main()
