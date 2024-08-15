import AudioRecorder from 'node-audiorecorder'
import fs from 'fs'
import path from 'path'

// Constants.
const DIRECTORY = 'data/audio'

// Create path to write recordings to.
if (!fs.existsSync(DIRECTORY)) {
  fs.mkdirSync(DIRECTORY);
}

// Options is an optional parameter for the constructor call.
const OPTIONS = {
  program: 'sox', // Which program to use, either `arecord`, `rec`, or `sox`.
  device: null, // Recording device to use. Null means default.
  driver: null, // Recording driver to use. Null means default.
  bits: 16, // Sample size. (only for `rec` and `sox`)
  channels: 1, // Channel count.
  encoding: 'signed-integer', // Audio encoding format. (only for `rec` and `sox`)
  rate: 16000, // Sample rate. Higher rate for better quality.
  type: 'wav', // Format type.
  silence: 2, // Duration of silence in seconds before it stops recording.
  keepSilence: true, // Keep the silence in the recording.
}

// Initialize recorder and file stream.
const recorder = new AudioRecorder(OPTIONS, console);

// Create file path with random name.
const fileName = path.join(
  DIRECTORY,
  Math.random()
    .toString(36)
    .replace(/[^0-9a-zA-Z]+/g, '')
    .concat('.wav')
);
console.log('Writing new recording file at:', fileName);

// Create write stream.
const fileStream = fs.createWriteStream(fileName);

// Start and write to the file.
recorder.start()

recorder.stream().pipe(fileStream)

// Stop after 5 seconds.
setTimeout(() => {
  console.log('123');
  recorder.stop();
  console.log('123111');
}, 5000);