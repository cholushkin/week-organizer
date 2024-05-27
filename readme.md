
# Organizer script usage

## Main usage

```
python.exe organizer.py -suggestion -start-date 27-may-2024 -output 27-may-2024.csv
```

## Other commands
- print-items
- get-random-todos

will generate csv file which you can paste to your google spreadsheet to manage your time and efforts during the week pipeline. 


# Pipeline

the pipeline is the following
- update todos.csv and items.json regarding the results of the previos week (if needed)
- get generic csv from the script
- review it and arrange, add new specific items
- during the week update the list moving items to another day if needed and changing the status to done
- in the end of the week move the sheet to the done sheet and write week conclusion