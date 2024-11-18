const fs = require('fs');
const readline = require('readline');

async function mergeJSONLFiles() {
  // Tạo file đầu ra
  const writeStream = fs.createWriteStream('merged_port_data.jsonl', { flags: 'w' });

  // Danh sách các file cần nối
  const files = [
    'data/port_data_add.jsonl',
    'data/port_data1.jsonl'
  ];

  // Xử lý từng file
  for (const file of files) {
    const rl = readline.createInterface({
      input: fs.createReadStream(file),
      crlfDelay: Infinity
    });

    for await (let line of rl) {
      // Bỏ qua các dòng trống hoặc chỉ chứa số
      if (line.trim() && !line.match(/^\d+\|$/)) {
        // Loại bỏ số dòng và ký tự '|' nếu có
        line = line.replace(/^\d+\|\s*/, '');

        // Kiểm tra xem dòng có phải là JSON hợp lệ không
        try {
          JSON.parse(line);
          writeStream.write(line + '\n');
        } catch (e) {
          console.log(`Bỏ qua dòng không hợp lệ trong file ${file}:`, line);
        }
      }
    }
  }

  writeStream.end();
  console.log('Đã hoàn thành việc nối file!');
}

// Chạy hàm
mergeJSONLFiles().catch(error => {
  console.error('Có lỗi xảy ra:', error);
});