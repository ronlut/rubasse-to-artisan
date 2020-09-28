import argparse
import csv
import os

CHARGE_ELAPSED = 0

DEFAULT_SUFFIX = "_artisan"
DEFAULT_EXTENSION = ".tsv"
DEFAULT_UNIT = "C"
HEADERS = ["Time1", "Time2", "BT", "ET", "Event", "Wind", "Fire", "RoR", "RPM", "Hum", "Pressure"]


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
    rpm = float(row[5])
    hum = float(row[6])
    pressure = float(row[8])

    return [time1, time2, bt, et, event, wind, fire, ror, rpm, hum, pressure]


def seconds_elapsed_to_time(seconds_elapsed):
    return '%02d:%02d' % (seconds_elapsed // 60, seconds_elapsed % 60)


def process_headers(writer, headers, unit):
    tp_elapsed = int(headers[17])
    fc_elapsed = int(headers[19])
    sc_elapsed = int(headers[21])
    drop_elapsed = int(headers[23])
    events = Events(CHARGE_ELAPSED, tp_elapsed, fc_elapsed, sc_elapsed, drop_elapsed)
    writer.writerow(artisan_metadata(unit, events))
    return events


def main(in_file_path, suffix, extension, unit):
    in_file = os.path.join(os.getcwd(), in_file_path)
    dirname, basename = os.path.split(in_file)
    name, _ = os.path.splitext(basename)
    out_file = os.path.join(dirname, name + suffix + extension)
    with open(in_file, 'r') as rf, open(out_file, 'w') as wf:
        reader = csv.reader(rf, delimiter=',')
        writer = csv.writer(wf, delimiter='\t', lineterminator='\n')
        rubasse_headers = next(reader)
        events = process_headers(writer, rubasse_headers, unit)
        writer.writerow(HEADERS)

        previous_row = next(reader)
        for current_row in reader:
            writer.writerow(transform_data(previous_row, events))
            previous_row = current_row

        # different handling for last row
        writer.writerow(transform_data(previous_row, events, event="Drop"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform rubasse csv files to artisan csv format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='path of file to transform (relative or absolute)', type=str)
    parser.add_argument('--suffix', nargs="?", default=DEFAULT_SUFFIX,
                        help='suffix to add (original_file_name{suffix}{ext})',
                        type=str)
    parser.add_argument('--ext', nargs="?", default=DEFAULT_EXTENSION,
                        help='extension to use (original_file_name{suffix}{ext})',
                        type=str)
    parser.add_argument('--unit', nargs="?", default=DEFAULT_UNIT, help='unit to use (C/F)',
                        type=str)
    args = parser.parse_args()

    main(args.file, args.suffix, args.ext, args.unit)
