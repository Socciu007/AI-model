import recorder from 'node-record-lpcm16';
import fs from 'fs';

// Tạo luồng ghi âm vào tệp .wav
const file = fs.createWriteStream('test.wav', { encoding: 'binary' });

// Cấu hình ghi âm với node-record-lpcm16 sử dụng sox và thiết bị âm thanh
const recording = recorder.record({
  sampleRate: 44100,           // Tần số mẫu (44.1 kHz)
  channels: 2,                 // Số kênh âm thanh (stereo)
  verbose: true,               // Hiển thị thông tin chi tiết quá trình ghi âm
  recordProgram: 'sox',        // Chương trình ghi âm được sử dụng là 'sox'
  device: 'your-device-name',  // Thay thế bằng tên thiết bị âm thanh của bạn
  audioType: 'wav'             // Định dạng âm thanh đầu ra là wav
});

// Ghi luồng âm thanh vào tệp
recording.stream().pipe(file);

// Dừng ghi âm sau 3 giây
setTimeout(() => {
  console.log('Stopping recording...');
  recording.stop();  // Dừng ghi âm và kết thúc tiến trình
}, 3000);

// // Xử lý sự kiện lỗi
// recording.on('error', (err) => {
//   console.error('Recording error:', err);
// });

// // Xử lý khi quá trình ghi âm kết thúc
// recording.on('end', () => {
//   console.log('Recording finished.');
// });
