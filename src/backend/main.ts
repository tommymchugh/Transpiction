/*
 * Name: main.ts
 * Author: Tommy McHugh
 * Description: Electron application that encompasses the MelodicalMakes web app
 * Date Created: 10/11/2019
 */

const electron = require('electron');
const { app, BrowserWindow, protocol } = electron;
const path = require('path');
const fs = require("fs");

// Setup live reload for the dist directory
// TODO: Disable when not in dev mode
require('electron-reload')(path.normalize(`${__dirname}/../../dist`));

// Define the protocol that will be added
// Give it all permissions
const protocolValue = "resource";
protocol.registerSchemesAsPrivileged([{ scheme: protocolValue, privileges: { standard: true, secure: true } }])

var defineStaticProtocol = () => {
  // Create a protocol for loading static files
  const protocolLength = protocolValue.length;

  protocol.registerStringProtocol(protocolValue, (request, callback) => {
    // Try is set so that no errors are given on live reload
    // TODO: make it not a try statement if not in dev mode
    try {
      // Remove any extraneous slashes from the end of the file
      // Set the file name to the relative path without resource protocol
      var removingEndCharacters = 0;
      if (request.url.substring(request.url.length-1, request.url.length) == "/")
        removingEndCharacters = 1;
      var fileName = request.url.substring(protocolLength+3, request.url.length-removingEndCharacters);

      // Remove any potential javascript parent files that get in the way with getting the full path
      const fileNameSplitted = fileName.split("/");
      for (var i = 0; i < fileNameSplitted.length; i++) {
        const comp = fileNameSplitted[i];
        if (comp.substring(comp.length-3, comp.length) == ".js" && i != fileNameSplitted.length-1)
          fileName = fileName.replace(`${comp}/`, "");
      }
      const filePath =  path.normalize(`${__dirname}/../app/${fileName}`);

      // Return the data as a string with JS MIME type
      // TODO: deal with more MIME types than just JS files
      var response = {data: fs.readFileSync(filePath, 'utf8')};
      if (fileName.substring(fileName.length-3, fileName.length) == ".js")
        response["mimeType"] = "text/javascript";

      callback(response);
    } catch {
      console.error("Failed to use protocol");
    }
  }, (error) => {
    if (error)
      console.error('Failed to register protocol');
  });
}

var createWindow = () => {
  // Get the screen width and height
  const screenSize = electron.screen.getPrimaryDisplay().workAreaSize;
  // Create the browser window.
  let win = new BrowserWindow({
    width: screenSize.width,
    height: screenSize.height-187,
    x: 0,
    y: 209,
    webPreferences: {
      nodeIntegration: true
    }
  });

  // and load the main html file of the app.
  win.loadFile('dist/app/static/index.html');
}

var onReady = () => {
  // Code to run when electron is finished loading
  defineStaticProtocol();
  createWindow();
}
  
app.on('ready', onReady);