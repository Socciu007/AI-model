import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const captureAudio = () => {
  // 使用sox命令捕获音频
  const soxProcess = spawn('sox', ['-t', 'waveaudio', '0', '-t', 'wav', '-']);

  // 创建一个可写流来保存音频数据
  const DIRECTORY = 'audio'
  const fileName = path.join(
    DIRECTORY,
    Math.random()
      .toString(36)
      .replace(/[^0-9a-zA-Z]+/g, '')
      .concat('.wav')
  );
  const writeStream = fs.createWriteStream(fileName, { flags: 'a' });

  // 监听sox的标准输出，处理实时音频数据
  soxProcess.stdout.on('data', (data) => {
    console.log('Captured audio chunk:', data);

    // 将捕获的音频数据写入文件
    writeStream.write(data);
  });

  // 监听sox的标准错误输出
  soxProcess.stderr.on('data', (data) => {
    console.error('Error:', data.toString());
  });

  // 监听sox进程的退出事件
  soxProcess.on('close', (code) => {
    console.log(`sox process exited with code ${code}`);

    // 关闭文件流
    writeStream.end();
  });
};

// 调用函数开始捕获音频
captureAudio();