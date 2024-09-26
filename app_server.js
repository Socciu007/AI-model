import { spawn } from 'child_process';
import express from 'express';
import http from 'http';
import zalo from 'zalo-sdk';

const app = express();
const PORT = 3001;
let soxProcess = null;
let fileName = null;

// Func send audio chunks to the server
const sendAudioChunk = (data, isFinalChunk = false) => {
  const options = {
    hostname: 'localhost',
    port: 5000,
    path: '/receive-audio',
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream',
      'File-Name': fileName,
      ...(isFinalChunk && { 'Recording-Complete': 'true' }), // Add custom header if it's the final chunk
    },
  };

  const req = http.request(options, (res) => {
    res.setEncoding('utf8');
    res.on('data', (chunk) => {
      console.log({
        status: res.statusCode,
        message: chunk,
      });
    });
  });

  req.on('error', (e) => {
    console.error(`Problem with request: ${e.message}`);
  });

  req.write(data);
  req.end();
};

// Func start the recording
const startCapture = () => {
  soxProcess = spawn('sox', ['-t', 'waveaudio', '0', '-t', 'wav', '-']);
  fileName = Math.random().toString(36).replace(/[^0-9a-zA-Z]+/g, '') + '.wav';

  soxProcess.stdout.on('data', (data) => {
    console.log('Captured audio chunk:', data);
    // 将录制的音频数据发送到另一台服务器
    sendAudioChunk(data);
  });

  // 监听sox的标准错误输出
  soxProcess.stderr.on('data', (data) => {
    console.error('Error:', data.toString());
  });

  // 监听sox进程的退出事件
  soxProcess.on('close', (code) => {
    console.log(`sox process exited with code ${code}`);
  });
};

// Func stop the recording
const stopCapture = () => {
  if (soxProcess) {
    soxProcess.kill();
    soxProcess = null;
    console.log('Audio capture stopped');

    // Send final empty chunk with Recording-Complete header
    sendAudioChunk(Buffer.alloc(0), true);
  }
};


// Define routes using Express
app.post('/start-capture', (req, res) => {
  startCapture();
  res.send('Audio capture started');
});

app.post('/stop-capture', (req, res) => {
  stopCapture();
  res.send('Audio capture stopped');
});

app.post('/send-message', (req, res) => {
  // Create a new Zalo instance
  const zlConfig = {
    appId: '940104600531434314',
    redirectUri: 'http://localhost/login/zalo-callback',
    appSecret: '1bgMx7eaUCETRJ223R0a',
  };
  const ZSClient = new zalo.ZaloSocial(zlConfig);

  // Get Access Token by Oauth Code and set value of access_token after you initialize ZaloSocial Instance
  ZSClient.getAccessTokenByOauthCode(req.body.code)
    .then((accessToken) => {
      console.log('Access Token:', accessToken);
      res.send('Message sent');
    })
    .catch((error) => {
      console.error('Error:', error);
    });
});

// Start the Express server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
