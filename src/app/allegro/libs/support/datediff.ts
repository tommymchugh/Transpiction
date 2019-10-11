/*
 * Name: datediff.ts
 * Author: Tommy McHugh
 * Description: A support extension that calculates differences in times between dates
 * Date Created: 10/11/2019
 */

// Find the difference in time using a certain type of metric
export let TimeType = {
    "millisecond": 0,
    "second": 1,
    "minute": 2,
    "hour": 3
};
export let DateDiff = (firstDate: Date, secondDate: Date, timeType: number) => {
    // Get the original time difference in ms
    const firstDateTime = firstDate.getTime();
    const secondDateTime = secondDate.getTime();
    var diff = Math.abs(firstDateTime-secondDateTime);

    // Convert to the time type specified
    switch(timeType) {
        case TimeType.second:
            diff /= 1000;
            break;
        case TimeType.minute:
            diff /= 60000;
            break;
        case TimeType.hour:
            diff /= 3600000;
            break;
    }

    return diff;
}