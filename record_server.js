import express from 'express';
import recorder from 'node-record-lpcm16';
import fs from 'fs';
import path from 'path';

const app = express();
const port = 3000;

// Endpoint để ghi âm thanh
app.post('/record', (req, res) => {
  const filePath = path.join('/data', 'audio', 'audio.wav');

  // Tạo luồng ghi âm
  const fileStream = fs.createWriteStream(filePath, { encoding: 'binary' });

  // Bắt đầu ghi âm
  recorder.record({
    sampleRate: 16000,
    threshold: 0.5,
    audioType: 'wav',
    recorder: 'sox', // Sử dụng 'sox' vì 'rec' không hỗ trợ trên Windows
  })
    .stream()
    .pipe(fileStream)

  // Dừng ghi âm sau 5 giây
  setTimeout(() => {
    recorder.stop();
    fileStream.end();

    // Trả về file âm thanh đã ghi
    res.sendFile(filePath, (err) => {
      if (err) {
        console.error(err);
        res.status(500).send('Error sending file');
      }

      // Xóa file sau khi gửi xong
      fs.unlink(filePath, (err) => {
        if (err) console.error(err);
      });
    });
  }, 5000); // Thay đổi thời gian ghi âm tùy thuộc vào nhu cầu
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
