/*
 * Name: mm.ts
 * Author: Tommy McHugh
 * Description: A canvas drawing lib that interacts through musical devices 
 * Date Created: 10/11/2019
 */

import {Allegro} from './allegro/allegro.js';

// Create an allegro instance
new Allegro((newNote, endedNote, activeNotes) => {
    // Get all active notes and print them to the screen
    /*
    var activeNoteString = "";
    for (var note of activeNotes) {
        activeNoteString += `${note.note}-${note.octave} `;
    }
    document.getElementById("note").textContent = activeNoteString;
    */
    if (endedNote != null) {
        document.getElementById("note").textContent = endedNote["length"];
    }
});