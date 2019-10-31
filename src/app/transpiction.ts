/*
 * Name: mm.ts
 * Author: Tommy McHugh
 * Description: A canvas drawing lib that interacts through musical devices 
 * Date Created: 10/11/2019
 */

import {Allegro} from './allegro/allegro.js';
import {ToneJs} from './allegro/libs/tone/Tone.js';

console.log(ToneJs);

// Create Synth and connect it to main speakers
const synth = new Synth();
synth.toMaster();

// Define characteristics about the music environment
const bpm = 130;
const quarterNoteCount = bpm/60
const noteCounts = {
    "quarter": quarterNoteCount,
    "whole": quarterNoteCount*4,
    "half": quarterNoteCount*2,
    "eigth": quarterNoteCount/2,
    "sixteenth": quarterNoteCount/4
}
const minNote = 48;
const maxNote = 107;
var notesPlayed = {};

var calculateNoteLength = (seconds) => {
    var closestLength = null;
    var closestLengthDiff = null;    

    const notesToCheck = [["quarter", 1.0], ["whole", 4.0], ["half", 2.0], ["eigth", 0.5], ["sixteenth", 0.25]];
    for (var i = 0; i < notesToCheck.length; i++) {
        const noteChecking = notesToCheck[i][0];
        const noteDiff = Math.abs(noteCounts[noteChecking]-seconds);
        if (closestLength == null) {
            closestLength = notesToCheck[i][1];
            closestLengthDiff = noteDiff;
        } else if (noteDiff < closestLengthDiff) {
            closestLength = notesToCheck[i][1];
            closestLengthDiff = noteDiff;
        }
    }

    return closestLength;
}

var noteSupported = (note) => {
    if (note >= minNote && note <= maxNote) {
        return true;
    }
    return false;
};

var averageLength = (lengthList) => {
    const listSum = lengthList.reduce((previous, current) => {
        return previous + calculateNoteLength(current);
    });
    return listSum/lengthList.length;
}

var interpolate = (notes) => {
    var allNotes = [];
    var totalNoteCount = 0;

    const noteKeys = Object.keys(notes);
    for (var i = 0; i < noteKeys.length; i++) {
        const noteKey = noteKeys[i];
        const note = notes[noteKey];
        totalNoteCount += note["count"];
    }

    for (i = minNote; i <= maxNote; i++) {
        const iStr = String(i);
        // Check if note was played
        if (notes[iStr] == undefined) {
            // Note was note played
            // Create empty frequency
            allNotes.push([i, 0, 0]);
        } else {
            // Note was played
            const noteInfo = notes[iStr];
            allNotes.push([i, noteInfo["count"]/totalNoteCount, averageLength(noteInfo["lengths"])])
        }
    }
    return allNotes;
}

var recording = false;
var recordingButton = document.getElementById("recording");
recordingButton.onclick = () => {
    if (recording) {
        // Stop recording
        recording = false;
        recordingButton.textContent = "Start Recording";
        // Process the input
        const noteTensor = interpolate(notesPlayed);
        const noteTensorString = JSON.stringify(noteTensor);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", `input://${noteTensorString}`, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send();
        // Clear the input
        notesPlayed = {};
    } else {
        // Start recording the input
        recording = true;
        recordingButton.textContent = "Stop Recording";
    }
}

// Create an allegro instance
new Allegro((newNote, endedNote, activeNotes) => {
    // Get all active notes and print them to the screen
    var activeNoteString = "";
    for (var note of activeNotes) {
        activeNoteString += `${note.note}-${note.octave}: ${note.rawValue}`;
    }
    document.getElementById("note").textContent = activeNoteString;

    if (newNote != undefined) {
        const newNoteValue = `${newNote.note.note}${newNote.note.octave}`;
        synth.triggerAttack([newNoteValue]);
    }

    if (endedNote != undefined) {
        const endNoteValue = `${endedNote.note.note}${endedNote.note.octave}`;
        synth.triggerRelease([endNoteValue]);
    }

    // Check if the user wants to record the notes
    if (recording) {
        // Notes are recording
        // If note is end note
        // Record the length and add to frequency count
        if (endedNote != undefined) {
            const noteValue = endedNote.note.rawValue;
            const noteValueString = parseInt(noteValue);
            // Confirm that the note value is supported
            if (noteSupported(noteValue)) {
                // Create a note played value if it does not exist
                if (notesPlayed[noteValueString] == undefined) {
                    notesPlayed[noteValueString] = {
                        "lengths": [endedNote["length"]],
                        "count": 1
                    }
                } else {
                    // Add note length and add to count for the value
                    notesPlayed[noteValueString]["lengths"].push(endedNote["length"]);
                    notesPlayed[noteValueString]["count"] += 1; 
                }  
            }
        }
    }
});