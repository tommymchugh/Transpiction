#! /bin/bash
gulp build
(osascript vmpk/start_script.scpt && npm start) &
gulp liveReload
