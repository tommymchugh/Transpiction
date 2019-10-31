/*
 * Name: allegro.ts
 * Author: Tommy McHugh
 * Description: A MIDI piano support library 
 * Date Created: 10/11/2019
 */

import {AllegroNote} from "./classes/allegro_note.js";
import {initSupport, TimeType, DateDiff, LowestNote, HighestNote} from "./libs/support/support.js";

export class Allegro {
    // Allegro manages the interactions between the MIDI APIs and the MIDI device
    // Define static variable types that need to be used
    static MIDIInputName = ["IAC Driver vmpk".toLowerCase(), "v25 Out".toLowerCase()];

    static errors = {
        "noBrowserSuppport": "This browser does not support MIDI APIs and will not run Allegro.",
        "noSupportLibrary": "The MelodicalMakes support library was not found.",
        "failedRequestingMIDIAPI": "Failed while requesting the MIDI Web API.",
        "noSupportedMIDIDevice": "No supported MIDI Device is found."
    };

    activeNotes:AllegroNote[] = [];
    instance:Record<string, any> = {};

    constructor(notePlayedCallback) {
        initSupport();

        // Instance provides information about the state of Allegro
        this.instance.notePlayedCallback = notePlayedCallback;

        // MIDI API uses promises to manage inputs and outputs
        // Allegro provides a wrapper around these interactions
        if (navigator["MIDIAvailable"] === true) {
            // MIDI Support available
            // Request access to the MIDI interfaces
            this.instance.browserSupported = true;
            navigator.requestMIDIAccess().then((midiAccess) => {
                // Successfully requested MIDI Access
                // Musical instruments will be included in inputs
                const inputs = midiAccess.inputs;
                // Determine whether a supported instrument is available
                var midiDevices = [];
                for (let input of inputs.values()) {
                    if (Allegro.MIDIInputName.includes(input.name.toLowerCase())) {
                        // MIDI input found and is supported
                        midiDevices.push(input);

                        // Set the message callback for the midi device
                        const classContext = this;
                        input.onmidimessage = (message) => {
                            // To override the callback with the note played callback
                            // The message is sent to midiMessageCallback and then processed
                            // Before being sent to the notePlayedCallback
                            classContext.midiMessageCallback(message, notePlayedCallback);
                        };
                    }
                }

                this.instance.instantiated = true;
                if (midiDevices === undefined) {
                    // No supported devices were found to interact with allegro
                    throw new Error(Allegro.errors.noSupportedMIDIDevice);
                } 
            }, () => {
                // Failed to request MIDI Access
                this.instance.instantiated = true;
                throw new Error(Allegro.errors.failedRequestingMIDIAPI);
            })
        } else {
            // No MIDI support found
            // Or the support library is not available
            // Rejecting the promise with the browser not supported error
            this.instance.browserSupported = false;
            this.instance.instantiated = true;
            if (navigator["MIDIAvailable"] === undefined) {
                // Support library was not loaded and did not interact with window.navigator
                throw new Error(Allegro.errors.noSupportLibrary);
            } else {
                // There is no browser support for the Web MIDI API
                throw new Error(Allegro.errors.noBrowserSuppport);
            }
        }
    }

    midiMessageCallback(message, notePlayedCallback) {
        // Define note message identifiers
        const newNoteIdentifier = 144;
        const endNoteIdentifier = 128;

        // Retrieve data from the message
        const noteIdentifier = message.data[0]
        const note = new AllegroNote(message.data[1]);
        //const noteVelocity = message.data[2] If needed

        // Cap the MIDI inputs to the lowest and highests notes required
        if (note.rawValue >= LowestNote && note.rawValue <= HighestNote) {
            var newNote, endNote;
            switch(noteIdentifier) {
                case newNoteIdentifier:
                    // Adding a new note to active notes
                    this.activeNotes.push(note);
                    newNote = {
                        "message": message,
                        "note": note
                    }
                    break;
                case endNoteIdentifier:
                    var noteLength = 0;
                    for (var i = 0; i < this.activeNotes.length; i++) {
                        const activeNote = this.activeNotes[i];
                        if (activeNote.rawValue === note.rawValue) {
                            noteLength = DateDiff(activeNote.dateTimeCreated, note.dateTimeCreated, TimeType.second);
                            this.activeNotes.splice(i, 1);
                            break;
                        }
                    }
                    endNote = {
                        "message": message,
                        "note": note,
                        "length": noteLength
                    }
                    break;
            }

            notePlayedCallback(newNote, endNote, this.activeNotes);
        }
    }
}