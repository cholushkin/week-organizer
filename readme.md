
# Organizer script usage

## Main usage

```
python.exe organizer.py -suggestion -start-date 27-may-2024 -output 27-may-2024.csv
```

## Other commands
- print-items
- get-random-todos
- print-completed-todos

will generate csv file which you can paste to your google spreadsheet to manage your time and efforts during the week pipeline. 


todos.csv - something that you can accomplish in one approach or in one week
todos-completed.csv - if not specified then completed tasks will disappear


# Pipeline

> Stage 1. Get tag distribution

```
Week _date_ review
day 1. #HLT #HLT #LNG #PRJ #PRJ #ART #ART #DEV #EDU #SKL
day 2. #HLT #HLT #LNG #PRJ #PRJ #ART #ART #SKL
day 3. #HLT #HLT #LNG #PRJ #PRJ #ART #ART #DEV #SKL #ENT #TODO
day 4. #HLT #LNG #PRJ #PRJ #ART #ART #DEV #SKL #TODO
day 5. #HLT #LNG #PRJ #PRJ #ART #SKL #ENT #TODO
day 6. #HLT #HLT #LNG #PRJ #ART #DEV #EDU #SKL #ENT
day 7. #HLT #LNG #PRJ #ART #ART #EDU #SKL #ENT

`r` - regenerate
`v` - verbose mode on/off

```
Stage 1 prepares week high-level task ditribution using settings from suggestion.json -> suggestions -> daily-priorities.



> Stage 2. Populate tasks
Prints day by day tasks from the user defined csv-files using parameters specified there.

```
 > day 1 review
 1. #HLT app-workout-full-body
 2. #HLT elliptical-trainer
 3. #LNG language-swedish
 4...
 5...
 
 `r` - regenerate
 `c` - continue to the next day
 `#x` - remove this task and never show again
 `#r` - regenerate task 
 `#f` - focus on task (or unfocus if task was previously focused)
 `#s` - select task from the list
```
r - will regenerate entire day suggestion 
3x - will remove task 3 (#LNG language-swedish) from the csv file (lng.csv) and move it to history file (lng-history.csv). Task 3 will be regenerated
3f - focus on `language-swedish` task. Add to focus.csv file (and remove from lng.csv). That mean next time the script generate tasks suggestion it will pick tasks from the focus.csv first. For example language-swedish task has `days = 2-3` which means #LNG slot (from stage)  from different days will be filled by this task. 

> Stage 3. 
Prints final week suggestion and save to csv.




the pipeline is the following
- update todos.csv and items.json regarding the results of the previos week (if needed)
- get generic csv from the script
- review it and arrange, add new specific items
- during the week update the list moving items to another day if needed and changing the status to done
- in the end of the week move the sheet to the done sheet and write week conclusion




## Modules review

- week_organizer_main.py - entry point. load and parse tasks csv files. Also uses 2 other modules tag_level_suggestion.py and task_level_suggestion.py
- tag_level_suggestion.py - make a week suggestion in terms of tags. Could work as a separate console program.
- task_level_suggestion.py - make a week suggestion in terms of tasks. Using as input the result received from tag_level_suggestion. Generates week_plan.csv as an output.

## Spreadsheet install
[Install spreadsheets scripts](add-script-to-sheets.md)