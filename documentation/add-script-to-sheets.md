1. Open your Google Sheets workbook
2. Go to Extensions > Apps Script
3. Create a new Google Apps Script project. Name it week-organizer.
4. copy content of google-spreadsheet/import-csv.gs to apps Script
5. Create a File Picker dialog. Create an HTML file named FilePicker.html in your Apps Script project and add the following code

Deploy the script as a web app:

In the Apps Script editor, click on Deploy -> New deployment.
Select Web app and configure the deployment settings.
Give all aceesses
![images/new-deployment.png](screenshot)


Run the script:

To run the script, you can call the importCSVFromFilePicker() function from the Apps Script editor, or you can add a custom menu to your Google Spreadsheet to trigger the file picker.
![images/sheet-gui.png](screenshot)


Run the script:

To run the script, you can call the importCSVFromFilePicker() function from the Apps Script editor, or you can add a custom menu to your Google Spreadsheet to trigger the file picker.
javascript
Copy code
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('CSV Importer')
    .addItem('Import CSV', 'importCSVFromFilePicker')
    .addToUi();
}