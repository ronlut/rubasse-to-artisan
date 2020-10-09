import argparse
import csv
import os

CHARGE_ELAPSED = 1

DEFAULT_SUFFIX = "_artisan"
ARTISAN_IMPORT_SUFFIX = "_for_artisan"
RUBASSE_OUTPUT_SUFFIX = "_for_rubasse"
DEFAULT_ARTISAN_EXTENSION = ".tsv"
DEFAULT_UNIT = "C"
HEADERS = ["Time1", "Time2", "BT", "ET", "Event", "Wind", "Fire", "RoR", "Rotation", "Humidity", "Pressure"]
RUBASSE_COLUMNS = 25


class Events:
    def __init__(self, charge, tp, fc, sc, drop):
        self.charge = charge
        self.tp = tp
        self.fc = fc
        self.sc = sc
        self.drop = drop

        self.artisan_events = {
            charge: "Charge",
        }

        for elapsed, event in zip([tp, fc, sc, drop], ["TP", "FCs", "SCs", "Drop"]):
            if not elapsed or elapsed == 0:
                continue

            self.artisan_events[elapsed] = event

    def from_elapsed(self, seconds):
        return self.artisan_events.get(seconds)


def artisan_metadata(unit, events):
    return ["Date:",
            "Unit:%s" % unit,
            "CHARGE:%s" % seconds_elapsed_to_time(events.charge),
            "TP:%s" % seconds_elapsed_to_time(events.tp),
            "DRYe:",
            "FCs:%s" % seconds_elapsed_to_time(events.fc),
            "FCe:",
            "SCs:%s" % seconds_elapsed_to_time(events.sc),
            "SCe:",
            "DROP:%s" % seconds_elapsed_to_time(events.drop),
            "COOL:",
            "Time:"]


def transform_data(row, events, event=None):
    seconds_elapsed = int(row[0])
    time1 = seconds_elapsed_to_time(seconds_elapsed)
    time2 = None
    bt = float(row[1])
    et = float(row[7])
    event = event if event else events.from_elapsed(seconds_elapsed)
    wind = float(row[2])
    fire = float(row[3])
    ror = float(row[4])
    rotation = float(row[5])
    humidity = float(row[6])
    pressure = float(row[8])

    return [time1, time2, bt, et, event, wind, fire, ror, rotation, humidity, pressure]


def seconds_elapsed_to_time(seconds_elapsed):
    return '%02d:%02d' % (seconds_elapsed // 60, seconds_elapsed % 60)


def time_to_seconds_elapsed(time_str):
    minutes, seconds = [int(part) for part in time_str.split(":")]
    return minutes*60 + seconds


def process_headers(writer, headers, unit):
    tp_elapsed = int(headers[17])
    fc_elapsed = int(headers[19])
    sc_elapsed = int(headers[21])
    drop_elapsed = int(headers[23])
    events = Events(CHARGE_ELAPSED, tp_elapsed, fc_elapsed, sc_elapsed, drop_elapsed)
    writer.writerow(artisan_metadata(unit, events))
    return events


def to_artisan(in_file_path, suffix, extension, unit):
    in_file = os.path.join(os.getcwd(), in_file_path)
    dirname, basename = os.path.split(in_file)
    name, _ = os.path.splitext(basename)
    name = clean_suffixes(name)
    out_file = os.path.join(dirname, name + suffix + extension)
    with open(in_file, 'r') as rf, open(out_file, 'w') as wf:
        reader = csv.reader(rf, delimiter=',')
        writer = csv.writer(wf, delimiter='\t', lineterminator='\n')
        rubasse_headers = next(reader)
        events = process_headers(writer, rubasse_headers, unit)
        writer.writerow(HEADERS)

        previous_rubasse_row = next(reader)
        for current_rubasse_row in reader:
            writer.writerow(transform_data(previous_rubasse_row, events))
            previous_rubasse_row = current_rubasse_row

        # different handling for last row
        writer.writerow(transform_data(previous_rubasse_row, events, event="Drop"))


def to_rubasse(in_file_path, suffix, extension):
    in_file = os.path.join(os.getcwd(), in_file_path)
    dirname, basename = os.path.split(in_file)
    name, _ = os.path.splitext(basename)
    name = clean_suffixes(name)
    out_file = os.path.join(dirname, name + suffix + extension)
    with open(in_file, 'r') as rf, open(out_file, 'w') as wf:
        reader = csv.reader(rf, delimiter='\t')
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')
        writer.writerow([0]*RUBASSE_COLUMNS)
        # skip artisan headers
        next(reader)
        artisan_headers = next(reader)
        artisan_headers_indices = {header: i for i, header in enumerate(artisan_headers)}

        for artisan_row in reader:
            bt = artisan_row[artisan_headers_indices['BT']]
            time_string = artisan_row[artisan_headers_indices['Time1']]
            seconds_elapsed = time_to_seconds_elapsed(time_string)
            # writer.writerow([seconds_elapsed, bt])
            writer.writerow([seconds_elapsed, bt] + [0.0]*7)


def clean_suffixes(in_path):
    return in_path.replace(RUBASSE_OUTPUT_SUFFIX, "").replace(ARTISAN_IMPORT_SUFFIX, "")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform rubasse csv files to artisan csv format and backwards',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file', help='path of file to transform (relative or absolute)', type=str, )
    # parser.add_argument('--suffix', nargs="?", default=DEFAULT_SUFFIX,
    #                     help='suffix to add (original_file_name{suffix}{ext})',
    #                     type=str)
    parser.add_argument('--ext', nargs="?", default=DEFAULT_ARTISAN_EXTENSION,
                        help='extension to use for artisan import file (original_file_name{suffix}{ext})',
                        type=str)
    parser.add_argument('--unit', nargs="?", default=DEFAULT_UNIT, help='unit to use (C/F)',
                        type=str)
    parser.add_argument('--export', action="store_true", help='export back to rubasse')
    args = parser.parse_args()

    if args.export:
        to_rubasse(args.file, RUBASSE_OUTPUT_SUFFIX, ".csv")
    else:
        to_artisan(args.file, ARTISAN_IMPORT_SUFFIX, args.ext, args.unit)
