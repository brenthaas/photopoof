# Required libraries
- GIMP
-

## Setting up printing

### lpoptions
- View available options via `lpoptions -p 'HiTi-P525L' -l`
- Set the default to a split 4x6
    - `lpoptions -p 'HiTi-P525L' -o media='P6x4_split'`

### Print Commands

- Because `lp` commands and `pyCups` have consistently produced strange color misalignment issues, but gimp prints images just fine, we use gimp to print images
    - Copy the `quick-print` gimp script (in `quick-print.scm`) to `~/.config/GIMP/2.10/scripts`
    - add `gimpprint` script to your `PATH`


## Diagnostic help to try to get lp printing

- From within Python
```
>>> import cups
>>> conn = cups.Connection()
>>> import pprint
>>> pp = pprint.PrettyPrinter(indent=4)
>>> pp.pprint(conn.getPrinterAttributes('HiTi-P525L'))
```

- In the terminal run `lpoptions -p 'HiTi-P525L' -l`
  - Media options for splitting images `PageSize/Media Size: *P6x4 P5x7 P6x8 P6x4_split P6x8_split P5x7_2up P6x8_2up`
