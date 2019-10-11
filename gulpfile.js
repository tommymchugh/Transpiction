/*
 * Name: gulpfile.js
 * Author: Tommy McHugh
 * Description: Automation tool for running MelodicalMakes
 * Date Created: 10/11/2019
 */

const gulp = require('gulp');
const {series, parallel} = gulp;
const del = require('del');
const ts = require('gulp-typescript');
const watch = require("gulp-watch");
const exec = require('child_process').exec;
const tslint = require("gulp-tslint");

function clean(cb) {
    // Deletes all files in the dist folder
    del([
        'dist/**/*'
    ]).then(() => {
        cb();
    });
}

function lint(cb) {
    // Linter for all typescript files

    gulp.src("src/**/*.ts")
        .pipe(tslint({
            formatter: "verbose"
        }))
        .pipe(tslint.report())
        .on('end', () => {
            cb();
        })
}

function compileTypeScriptFrontend(cb) {
    // Compiles the typescript files in the app folder

    const tsProjectFrontend = ts.createProject("tsconfig_frontend.json");
    const tsResultFrontend = gulp.src("src/app/**/*.ts").pipe(tsProjectFrontend());
    tsResultFrontend.js.pipe(gulp.dest('dist/app')).on('end', () => {
        cb();
    });
}

function compileTypeScriptBackend(cb) {
    // Compiles the typescript files in the backend folder

    const tsProject = ts.createProject("tsconfig_backend.json");
    const tsResult = gulp.src("src/backend/**/*.ts").pipe(tsProject());
    tsResult.js.pipe(gulp.dest('dist/backend')).on('end', () => {
        cb();
    });
}

function copyStatics(cb) {
    // Copy static files into the dist folder

    gulp.src("src/app/static/**/*").pipe(
        gulp.dest("dist/app/static")).on("end", () => {
            cb();
        });

}

function cleanFrontend(cb) {
    // Removes the app folder from the dist folder

    del([
        "dist/app/**/*"
    ]).then(() => {
        cb();
    })
}

function startWithLiveReload(cb) {
    // Watch for changes in the frontend of the application

    watch("src/app/**/*", () => {
        console.log("File changed. Reloading the app.");
        series(copyStatics, lint, compileTypeScriptFrontend)();
    });
    cb();
}

exports.clean = clean;
exports.build = series(clean, lint, compileTypeScriptBackend, compileTypeScriptFrontend, copyStatics);
exports.liveReload = startWithLiveReload;
exports.default = series(clean, lint, compileTypeScriptBackend, compileTypeScriptFrontend, copyStatics, startWithLiveReload);