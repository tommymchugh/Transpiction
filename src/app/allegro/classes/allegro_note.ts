/*
 * Name: allegro_note.ts
 * Author: Tommy McHugh
 * Description: Handles conversion between MIDI input to musical notation
 * Date Created: 10/11/2019
 */

import {LowestNote} from '../libs/support/support.js';

export class AllegroNote {
    // Define the notes on keyboard
    static noteValues = {
        0: "C", 1: "C#",
        2: "D", 3: "D#",
        4: "E", 5: "F",
        6: "F#", 7: "G",
        8: "G#", 9: "A",
        10: "A#", 11: "B"
    };
    static numOfNotes = Object.keys(AllegroNote.noteValues).length;
    // The second octave is the first octave that is usable
    static octaveStart = 2;

    rawValue:number;
    dateTimeCreated:Date;
    octave:number;
    note:string;

    constructor(rawValue) {
        this.rawValue = rawValue;
        this.dateTimeCreated = new Date();

        // Convert the raw value of the note to the musical representation
        const normalizedValue = (rawValue-LowestNote);
        // Octave is the normalized note value divied by the total number of notes without a remainder
        this.octave = Math.floor(normalizedValue/AllegroNote.numOfNotes) + AllegroNote.octaveStart;
        // Note is the letter representation of normalized value modulus the total number of notes
        this.note = AllegroNote.noteValues[normalizedValue % AllegroNote.numOfNotes];
    }
}