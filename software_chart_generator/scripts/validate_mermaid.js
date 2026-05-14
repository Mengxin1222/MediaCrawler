#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile) {
    console.error(JSON.stringify({
        success: false,
        error: "No input file specified"
    }));
    process.exit(1);
}

const tempOutput = path.join(path.dirname(inputFile), `.temp-${Date.now()}.svg`);

const mmdcPath = require.resolve('@mermaid-js/mermaid-cli');
const scriptDir = path.dirname(mmdcPath);

let mmdcBin = path.join(scriptDir, 'bin', 'mmdc');
if (process.platform === 'win32') {
    mmdcBin += '.cmd';
}

if (!fs.existsSync(mmdcBin)) {
    console.error(JSON.stringify({
        success: false,
        error: "mmdc binary not found. Please run 'npm install'."
    }));
    process.exit(1);
}

execFile(mmdcBin, ['-i', inputFile, '-o', tempOutput], (error, stdout, stderr) => {
    try {
        if (fs.existsSync(tempOutput)) {
            fs.unlinkSync(tempOutput);
        }
    } catch (e) {}

    if (error) {
        const errorMsg = stderr || stdout || error.message || "Unknown error";
        console.error(JSON.stringify({
            success: false,
            error: errorMsg.trim()
        }));
        process.exit(1);
    } else {
        console.log(JSON.stringify({
            success: true
        }));
        process.exit(0);
    }
});
