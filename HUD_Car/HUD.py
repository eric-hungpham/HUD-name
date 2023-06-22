import pygame
import csv
import time
import threading
import obd
import datetime

# Khởi tạo Pygame
pygame.init()

pygame.init()
#res = (320,240)
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
#screen = pygame.display.set_mode(res)
width = screen.get_width()
height = screen.get_height()
#WHITE = (255, 255, 255)
WHITE = (0, 255, 0)

BLACK = (0, 0, 0)
# Thiết lập màn hình Pygame
pygame.display.set_caption("OBD2 Data")
font = pygame.font.SysFont(None, 28)

previous_speed = None
previous_time = None


# Tạo biến để lưu trữ trạng thái kết nối OBD2
obd_connected = False

# Tạo thread lock cho việc đồng bộ hóa dữ liệu
data_lock = threading.Lock()

# Tạo biến để lưu trữ dữ liệu OBD2
obd_data = {'Speed': None, 'RPM': None, 'Throttle Position': None,
            'Engine Load': None, 
            'Engine Coolant Temp': None,
            'Intake Air Temp': None
            }
previous_speed = 0
# Tạo thread cho việc cập nhật dữ liệu từ OBD2
def update_obd_data():
    global obd_data, obd_connected, connection, previous_speed
    
    while True:
        # Kiểm tra trạng thái kết nối OBD2
        if not obd_connected:
            # Nếu chưa kết nối, ngủ 1 giây và tiếp tục lặp lại
            #print("Loading...")
            time.sleep(1)
            continue
        try:
            # Lấy giá trị từ các lệnh OBD2
            speed = round(connection.query(obd.commands.SPEED).value.magnitude, 2)
            rpm = round(connection.query(obd.commands.RPM).value.magnitude, 2)
            throttle_pos = round(connection.query(obd.commands.THROTTLE_POS).value.magnitude, 2)
            
            
            #một vài giá trị khác
            engine_load = round(connection.query(obd.commands.ENGINE_LOAD).value.to("percent").magnitude,2)
            coolant_temp = round(connection.query(obd.commands.COOLANT_TEMP).value.to("celsius").magnitude,2)
            intake_air_temp = round(connection.query(obd.commands.INTAKE_TEMP).value.to("celsius").magnitude,2)

            # Đồng bộ hóa dữ liệu với thread khác
            with data_lock:
                # Lưu các giá trị vào biến obd_data
                obd_data = {'Speed': speed, 'RPM': rpm, 'Throttle Position': throttle_pos,
                            'Engine Load': engine_load, 
                            'Engine Coolant Temp': coolant_temp,
                            'Intake Air Temp': intake_air_temp}
            # Ngủ 1 giây trước khi lấy các giá trị mới
            time.sleep(1)
        except Exception as e:
            # Nếu có lỗi trong quá trình lấy giá trị, in thông báo lỗi và tiếp tục lặp lại
            print(f"Mất kết nối : {e}")
            obd_connected = False
        else:
            obd_connected = True

# Tạo thread cho việc hiển thị dữ liệu OBD2 trên Pygame
def display_obd_data():
    while True:
        # Lấy ra các dữ liệu OBD2 từ biến obd_data
        with data_lock:
            speed = obd_data['Speed']
            rpm = obd_data['RPM']
            throttle_pos = obd_data['Throttle Position']
        # Xóa màn hình Pygame và hiển thị dữ liệu OBD2
        screen.fill(BLACK)
            # ve 3 hinh vuong
        pygame.draw.rect(screen, WHITE, pygame.Rect(3, height/3+15, width-5, height/1.7), 3)
        pygame.draw.rect(screen, WHITE, pygame.Rect(3, 0, width/2-10, height/3+10), 3)
        pygame.draw.rect(screen, WHITE, pygame.Rect(width/2, 0, width/2-5, height/3+10), 3)
            #chon cỡ chữ
        speedF = pygame.font.SysFont(None, 25)
        rpmF = pygame.font.SysFont(None, 20)
        throttle_possitionF = pygame.font.SysFont(None, 20)
            #gán chữ
        speedText = speedF.render("Speed", True, WHITE)
        rpmText= rpmF.render("RPM", True, WHITE)
        throttle_possitionText = throttle_possitionF.render("Throttle Possion", True, WHITE)
    
            #đảo ngược chữ và hiển thị lên màn hình
        speedText_with_flip = pygame.transform.flip(speedText, False, True)
        rpmText_with_flip = pygame.transform.flip(rpmText, False, True)
        throttle_possitionText_with_flip = pygame.transform.flip(throttle_possitionText, False, True)
            
        screen.blit(speedText_with_flip, (width/2-35, height/2-20))
        screen.blit(rpmText_with_flip,(width/6-5, 5) )
        screen.blit(throttle_possitionText_with_flip, (width/1.5-20, 5))
            
            #co chu cua gia tri
        speed_font = pygame.font.SysFont(None, 180)
        rpmfont = pygame.font.SysFont(None, 85)
        throttle_possitionfont = pygame.font.SysFont(None, 65)
            
            #giá trị            
        speed_surface = speed_font.render(f'{speed}', True, WHITE)
        rpm_surface = rpmfont.render(f'{rpm}', True, WHITE)
        throttle_pos_surface = throttle_possitionfont.render(f'{throttle_pos} %', True, WHITE)
            
        speed_surface_with_flip = pygame.transform.flip(speed_surface, False, True)
        rpm_surface_with_flip = pygame.transform.flip(rpm_surface, False, True)
        throttle_pos_surface_with_flip = pygame.transform.flip(throttle_pos_surface, False, True)
        
        screen.blit(speed_surface_with_flip, (width/3.5, height/1.70))
        screen.blit(rpm_surface_with_flip, (width/8, height/7.5))
        screen.blit(throttle_pos_surface_with_flip, (width/1.5-10, height/7.5))
        pygame.display.update()
        time.sleep(0.1)

# Tạo thread cho việc xuất dữ liệu OBD2 ra file CSV
def write_obd_data():
    global obd_data, obd_connected, previous_speed, previous_time

    while True:
		# Kiểm tra trạng thái kết nối OBD2
        if not obd_connected:
            # Nếu chưa kết nối, ngủ 1 giây và tiếp tục lặp lại
            time.sleep(1)
            
            continue 
        try:
            if obd_connected:
                # Lấy ngày giờ hiện tại để đặt tên file CSV
                now = datetime.datetime.now()
                filename = f'/home/pi/code/csv/obd_data_{now.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
            # Mở file CSV để ghi dữ liệu
                with open(filename, 'w', newline='') as f:
                    csv_writer = csv.writer(f)
                # Viết header cho file CSV
                    csv_writer.writerow(['Time', 'Speed (kmph)', 'RPM', 'Throttle Position (%)', 'Acceleration (m/s2)',
                                        'Engine Load (%)', 'Engine Coolant Temp (°C)', 'Intake Air Temp (°C)'])
                    while obd_connected:
                        # Lấy các giá trị mới nhất từ OBD2 để ghi vào file CSV
                        with data_lock:
                            speed = obd_data['Speed']
                            rpm = obd_data['RPM']
                            throttle_pos = obd_data['Throttle Position']
                                                        
                            engine_load = obd_data['Engine Load']
                            coolant_temp = obd_data['Engine Coolant Temp']
                            intake_air_temp = obd_data['Intake Air Temp']
                            
                        # Lấy thời gian hiện tại
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        if previous_speed is not None and previous_time is not None:
                            time_interval = time.time() - previous_time
                            #acceleration = (speed - previous_speed) / time_interval
                            #chuyển từ km/h sang m/s để nhận được đơn vị gia tốc là m/s2
                            acceleration = round((speed * 0.277778 -previous_speed* 0.277778)/time_interval,2)
                        else:
                            acceleration = 0

                        previous_speed = speed
                        previous_time = time.time()

                    # Ghi các giá trị vào file CSV
                        csv_writer.writerow([current_time, speed, rpm, throttle_pos, acceleration, 
                                            engine_load, coolant_temp, intake_air_temp])
                        f.flush()
                    # Ngủ và lặp lại việc ghi các giá trị mới vào file CSV
                        time.sleep(3)
        except Exception as e:
            # Nếu có lỗi trong quá trình lấy giá trị, in thông báo lỗi và tiếp tục lặp lại
            obd_connected = False
# Tạo thread cho việc kiểm tra kết nối OBD2
def check_obd():
    global obd_connected, connection
    while True:
        if not obd_connected:
            try:
            # Thử kết nối OBD2 với xe ô tô
                connection = obd.OBD()
            # Kiểm tra trạng thái kết nối
                if connection.status() == obd.OBDStatus.CAR_CONNECTED:
                    obd_connected = True
                    print("Kết nối OBD2 thành công")
                elif connection.status() == obd.OBDStatus.OBD_CONNECTED:
                    obd_connected = False
                    print ("Khởi động xe để truyền dữ liệu")
            # Ngủ 1 giây trước khi thử kết nối OBD2 lần tiếp theo
                time.sleep(0.1)
            except:
            # Nếu có lỗi xảy ra trong quá trình kết nối, hiển thị thông báo lỗi và thử kết nối lại
                    print("Lỗi trong quá trình kết nối OBD2")
                    obd_connected = False
                    time.sleep(0.1)


# Tạo các thread cho việc cập nhật dữ liệu OBD2, hiển thị dữ liệu và xuất dữ liệu ra file CSV
check_obd_thread = threading.Thread(target=check_obd)
update_obd_data_thread = threading.Thread(target=update_obd_data)
display_obd_data_thread = threading.Thread(target=display_obd_data)
write_obd_data_thread = threading.Thread(target=write_obd_data)

#đặt các thread là deamon
check_obd_thread.daemon = True
update_obd_data_thread.daemon = True
display_obd_data_thread.daemon = True
write_obd_data_thread.daemon = True

# Bắt đầu các thread
check_obd_thread.start()
update_obd_data_thread.start()
display_obd_data_thread.start()
write_obd_data_thread.start()

     
# Chờ cho đến khi người dùng đóng cửa sổ Pygame
import sys

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    # Thực hiện các hoạt động khác ở đây
    
# Đóng Pygame
pygame.quit()

# Kết thúc các thread
check_obd_thread.join()
update_obd_data_thread.join()
display_obd_data_thread.join()
write_obd_data_thread.join()

# Thoát khỏi chương trình
sys.exit()





