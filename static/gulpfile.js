'use strict';

var gulp = require('gulp'),
	browserSync = require("browser-sync"),
    reload = browserSync.reload;

var config = {
    server: {
        baseDir: "./"
    },
    tunnel: true,
    host: 'localhost',
    port: 8080,
    logPrefix: "messenger"
};

gulp.task('webserver', function () {
    browserSync(config, function (err, bs) {
    });
});