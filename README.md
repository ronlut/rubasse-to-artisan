# rubasse-to-artisan
A simple script to transform the output of Rubasse coffee roaster to an Artisan compatible CSV

## Usage
```
main.py [-h] [--suffix [SUFFIX]] [--ext [EXT]] [--unit [UNIT]] file

Transform rubasse csv files to artisan csv format

positional arguments:
  file               path of file to transform (relative or absolute)

optional arguments:
  -h, --help         show this help message and exit
  --suffix [SUFFIX]  suffix to add (original_file_name{suffix}{ext})
  --ext [EXT]        extension to use (original_file_name{suffix}{ext})
  --unit [UNIT]      unit to use (C/F)
```