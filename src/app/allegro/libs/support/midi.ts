/*
 * Name: midi.ts
 * Author: Tommy McHugh
 * Description: Support library functions and extensions for using MIDI web API
 * Date Created: 10/11/2019
 */

export var MIDI = () => {
    // Determine whether MIDI access is available
    // Create a boolean representation within window.navigator
    navigator["MIDIAvailable"] = (() => {
        if (navigator.requestMIDIAccess)
            return true;
        return false;
    })();
 }