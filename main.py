import argparse
import csv

from pathlib2 import Path

DEFAULT_SUFFIX = "_artisan"
DEFAULT_EXTENSION = ".tsv"
DEFAULT_UNIT = "C"
HEADERS = ["Time1", "Time2", "BT", "ET", "Event"]


def metadata(unit):
    return ["Date:", "Unit:%s" % unit, "CHARGE:", "TP:", "DRYe:", "FCs:", "FCe:", "SCs:", "SCe:", "DROP:", "COOL:",
            "Time:"]


def transform_data(row):
    seconds_elapsed = int(row[0])
    time1 = '%02d:%02d' % (seconds_elapsed//60, seconds_elapsed%60)
    time2 = None
    bt = et = float(row[1])
    event = None

    return [time1, time2, bt, et, event]


def main(in_file_path, suffix, extension, unit):
    in_file = Path.cwd().joinpath(in_file_path)
    out_file = in_file.with_name(in_file.stem + suffix + extension)
    with in_file.open('r') as rf, out_file.open('w') as wf:
        reader = csv.reader(rf, delimiter=',')
        writer = csv.writer(wf, delimiter='\t', lineterminator='\n')
        _ = next(reader)  # useless headers
        writer.writerow(metadata(unit))
        writer.writerow(HEADERS)
        for row in reader:
            writer.writerow(transform_data(row))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform rubasse csv files to artisan csv format')
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