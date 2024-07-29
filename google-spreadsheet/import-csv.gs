function importCSVFromFilePicker() {
  var html = HtmlService.createHtmlOutputFromFile('FilePicker').setWidth(400).setHeight(150);
  SpreadsheetApp.getUi().showModalDialog(html, 'Select a CSV file');
}

function processCSV(csvContent, fileName) {
  // Parse the CSV data
  var data = Utilities.parseCsv(csvContent);
  
  // Open the active spreadsheet
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  
  // Add a new sheet with the CSV file name
  var sheet = spreadsheet.getSheetByName(fileName);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(fileName);
  } else {
    sheet.clear();
  }
  
  // Import the CSV data into the sheet
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);

  decorateSheet(sheet, data);
  decorateTagsColumn(sheet, data);
}

function decorateSheet(sheet, data) {
  // Freeze the first row
  sheet.setFrozenRows(1);

  // Make the first row bold
  var headerRange = sheet.getRange(1, 1, 1, data[0].length);
  headerRange.setFontWeight('bold');

  // Format the Date column to "Monday, June 10, 2024"
  sheet.getRange(2, 4, sheet.getLastRow()-1).setNumberFormat("dddd, mmmm dd, yyyy");

  // Wrap text in the second column
  var secondColumn = sheet.getRange(2, 2, sheet.getLastRow()-1); // Assuming text to be wrapped is in the second column
  secondColumn.setWrap(true);

  // Add conditional formatting to Status column
  var statusColumn = sheet.getRange(2, 3, sheet.getLastRow()-1); // Assuming 'Status' is in the second column
  var rule1 = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('done')
    .setBackground('#00FF00') // Green
    .setRanges([statusColumn])
    .build();
  var rule2 = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('wip')
    .setBackground('#FFA500') // Orange
    .setRanges([statusColumn])
    .build();
  var rules = sheet.getConditionalFormatRules();
  rules.push(rule1);
  rules.push(rule2);
  sheet.setConditionalFormatRules(rules);

  // Color blocks of data with grey background and keep empty lines white
  var numRows = data.length;
  var numCols = data[0].length;  
  var colors = [];

  for (var i = 1; i < numRows; i++) {
    var rowData = data[i];
    if (rowData.every(cell => cell === '')) {
      // Empty line
      colors.push(new Array(numCols).fill('#FFFFFF')); // White
    } else {
      // Data block
      colors.push(new Array(numCols).fill('#D3D3D3')); // Grey
    }
  }

  // Apply the background colors in one go
  sheet.getRange(2, 1, numRows-1, numCols).setBackgrounds(colors);
}

function decorateTagsColumn(sheet, data) {
  // Tags column is the 5th column (E)
  var tagsColumn = sheet.getRange(2, 5, sheet.getLastRow()-1);

  var tagColors = {
    "HLT": "#ff0000",
    "LNG": "#ff9900",
    "PRJ": "#9fc5e8",
    "ART": "#9900ff",
    "DEV": "#1155cc",
    "EDU": "#6aa84f",
    "SKL": "#bf9000",
    "ENT": "#ffff00",
    "TODO": "#ffffff"
  };

  var rules = sheet.getConditionalFormatRules();

  for (var tag in tagColors) {
    var rule = SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo(tag)
      .setFontColor(tagColors[tag])
      .setRanges([tagsColumn])
      .build();
    rules.push(rule);
  }

  sheet.setConditionalFormatRules(rules);
}


function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('CSV Importer')
    .addItem('Import CSV', 'importCSVFromFilePicker')
    .addToUi();
}
