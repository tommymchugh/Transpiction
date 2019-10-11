/*
 * Name: support.ts
 * Author: Tommy McHugh
 * Description: Provides tools and extensions to JS to hack efficiently
 * Date Created: 10/11/2019
 */

// Initialize runs and creates any global variables from child libs
import {MIDI} from './midi.js';
export var initSupport = ()=> {
    MIDI();
}

// Export all of the child libs
export {MIDI} from './midi.js';
export {TimeType, DateDiff} from './datediff.js';
export {LowestNote, HighestNote} from './globals.js';