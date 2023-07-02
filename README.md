# Thiết kế và thi công HUD cho xe hơi
Đây là đề tài tốt nghiệp được hoàn thành vào đầu tháng 6 năm 2023, ngành **Điện tử viễn thông** tại trường Đại học Công nghiệp TP Hồ Chí Minh của mình.

## Mục tiêu đề tài:
Thiết kế một bộ HUD (Head-up Display) hiển thị các thông tin lên kính lái của xe ô tô, thỏa mãn yêu cầu sau:
- Đọc các giá trị tốc độ, vận tốc, vị trí bướm ga, nhiệt độ nước làm mát... hiển thị lên màn hình HUD cho xe hơi
- Các giá trị này được đọc và tự động liên tục theo thời gian, từ khi xe khởi động cho tới khi xe tắt máy.
- Xuất tất cả các giá trị đọc được ra một file csv để lưu trữ (phục vụ các quá trình phân tích)

## Các thiết bị cần thiết:
- Raspberry Pi 4B
- USB ELM327 kết nối với cáp OBD2 của xe ô tô để đọc dữ liệu
- Màn hinh PiTFT để hiển thị dữ liệu
- Code trong thư mục HUD_Car của mình

## Mô tả các công việc đã làm:
Mình đã thực hiện xử lý đa luồng (threading) các công việc `update_obd_data`, `display_obd_data`, `write_obd_data` và `check_obd_thread`.
*Vì sao phải sử dụng đa luồng thay vì lập trình tuần tự ?* Vì chuẩn OBD2 của xe ô tô cung cấp một cơ chế làm việc theo kiểu `Command-Response`, cơ chế này cho phép chúng ta truy xuất dữ liệu của xe ô tô theo kiểu lệnh-phản hồi. Có nghĩa là nếu ta nhập các lệnh của obd vào terminal của rasp thì sẽ được trả về giá trị tương ứng, tuy nhiên nó chỉ cho phép ta thực hiện duy nhất một nhiệm vụ với dữ liệu được lấy về này. Cụ thể ta chỉ có thể thực hiện một nhiệm vụ là hiển thị dữ liệu lên màn hình HUD hoặc xuất dữ liệu này vào file csv, ta không thể làm hai nhiệm vụ cùng một lúc vì trình trạng xung đột dữ liệu. Do đó xử lý đa luồng đã được áp dụng để tránh tình trạng này.

## Giải thích code và quá trình mình thực hiện:
Có 4 hàm tương đương 4 nhiệm vụ cần quan tâm. Đó là:
- `update_obd_data` cập nhật giá trị lấy về từ obd2 của xe ô tô vào biến obd_data.
- `display_obd_data` hiểm thị giá trị speed, rpm, throttle position lên màn hình.
- `write_obd_data` xuất toàn bộ giá trị đọc về từ obd2 của xe vào một file csv.
- `check_obd_thread` kiểm tra trạng thái của obd2.

**Giải thích quá trình các hàm này làm việc song song**

Tất cả các thread như check_obd_thread( ), update_obd_data_thread( ), display_obd_data_thread( ), write_obd_data_thread( ) sẽ đảm nhiệm các chức năng riêng của mình đồng thời. Tuy nhiên, chúng sẽ bị quản lý bởi biến toàn cục obd_connected, được đặt là false. Ban đầu, thread check_obd_thread( ) sẽ chạy để kiểm tra kết nối của cổng OBD2 trên xe ô tô với Raspberry . Nếu có kết nối thì biến obd_connected = True. Từ đây, khi biến toàn cục obd_connected được xác lập là True thì các thread còn lại mới bắt đầu thực hiện công việc của mình. Nếu mỗi thread xảy ra lỗi bất kỳ hoặc biến obd_connected = False thì tất cả thread sẽ dừng lại và khởi động lại từ đầu.

Vì tất cả các thread đều đồng thời truy cập vào biến obd_data để lấy dữ liệu phục vụ cho chức năng của từng thread nên sẽ dẫn tới tình trạng xung đột dữ liệu. Vì vậy, để tránh tình trạng này, ta phải sử dụng threading.lock( ) trong lập trình đa luồng để đảm bảo rằng chỉ có một thread được phép truy cập vào tài nguyên dữ liệu tại một thời điểm. Khi một thread đang sử dụng tài nguyên, các thread khác sẽ phải chờ đợi cho đến khi tài nguyên được giải phóng trước khi truy cập. Từ đây sẽ tránh xung đột dữ liệu và đảm bảo tính nhất quán của ứng dụng. 

## **Video kết quả thực tế:** 
https://www.youtube.com/watch?v=cF7k8qJQ8BI

*Video thông tin:* https://www.youtube.com/watch?v=_nL23KFYJxs
