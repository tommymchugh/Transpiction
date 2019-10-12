#! /bin/bash
npx gulp build
(osascript vmpk/start_script.scpt && npm start) &
npx gulp liveReload
