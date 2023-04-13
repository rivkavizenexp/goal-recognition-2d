# Goal Recognition 2d

Experiments of goal recognition in 2d over Amazon's Mechanical Turk

## Installation  

Described in [SETUP](SETUP.md) file

## Mturk commands

the file [main.py](main.py) is an command-line tool that manages the expirament

mturk commands starts with:
```[bash]
python3 main.py mturk [-p]
```
the -p flag specifies production, if specified the command will work on production account

### to create hits use the command:
 ```[bash]
 python3 main.py mturk [-p] create -t <title> [-d <svg_dir>] [-n <number of slides>] [-l <lifetime in seconds>] [-c <number of hits>]
 ```
if -c not specified, the program will create the minimum required number of hits to cover all slides(70 hits)


### to review Assignments use the command:
```[bash]
 python3 main.py mturk [-p] review [--auto]
```
if the auto flag specified, the program will automatically accept or reject assignments, otherwise the program will ask the user what to do 

### to create a csv file with the results use the command:
```[bash]
 python3 main.py report [--output_path OUTPUT_PATH] [--anchors_file ANCHORS_FILE] [--preview]
```
it will create a csv file with the results of the experiment, 
- if the preview flag specified, the program will create a preview for each slide
- you can provide a path to the anchors file, the file should be excel file with the following columns: 

    | Group| Slide| x| y| Radius 
    | --- | --- | --- | --- | ---
    | ... | ... | ... | ... | ...
- if the output_path not specified, the program will create a file in the current directory with the name: results.csv