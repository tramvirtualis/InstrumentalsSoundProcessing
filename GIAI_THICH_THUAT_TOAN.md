# QUY TRÌNH CHI TIẾT CÁC BƯỚC TÍNH TOÁN THUẬT TOÁN (STEP-BY-STEP)

Tài liệu này mô tả chi tiết **trình tự thực hiện từng bước** (pipeline) để tính toán ra các kết quả hiển thị trên ứng dụng.

---

## PHẦN 1: BA BIỂU ĐỒ TRỰC QUAN (VISUALIZATIONS)

### 1. Phân tích LPC (Linear Predictive Coding)
*Mục đích: Vẽ đường bao phổ mô phỏng đặc tính cộng hưởng của nhạc cụ.*

**Quy trình thực hiện:**
1.  **Bước 1 - Tiền xử lý (Pre-processing)**:
    *   Cắt một đoạn tín hiệu ngắn (Frame), thường là 20ms - 30ms từ giữa file.
    *   Áp dụng **Cửa sổ Hamming** lên đoạn tín hiệu này để làm mượt 2 đầu, tránh nhiễu do cắt gọt.
2.  **Bước 2 - Tính Tự tương quan (Autocorrelation)**:
    *   Tính chuỗi tự tương quan $R[k]$ của tín hiệu với chính nó ở các độ trễ khác nhau.
3.  **Bước 3 - Giải phương trình Levinson-Durbin**:
    *   Sử dụng chuỗi $R[k]$ làm đầu vào.
    *   Chạy đệ quy để giải hệ phương trình Yule-Walker.
    *   **Kết quả**: Tìm ra bộ hệ số LPC $a_1, a_2, ..., a_p$ (với $p$ là bậc bộ lọc, thường chọn 20-30 cho nhạc cụ).
4.  **Bước 4 - Tính phổ LPC (Frequency Response)**:
    *   Tạo bộ lọc IIR từ các hệ số $a_k$: $H(z) = \frac{1}{1 - \sum a_k z^{-k}}$.
    *   Tính đáp ứng tần số của bộ lọc này.
5.  **Bước 5 - Hiển thị**:
    *   Vẽ đường cong đáp ứng tần số lên biểu đồ Log-Frequency.

### 2. Dạng sóng (Waveform)
*Mục đích: Hiển thị hình dáng tín hiệu theo thời gian.*

**Quy trình thực hiện:**
1.  **Bước 1 - Đọc dữ liệu thô (PCM)**:
    *   Đọc toàn bộ file âm thanh vào mảng số liệu (Digital Samples).
    *   Nếu là Stereo (2 kênh), lấy trung bình cộng để về Mono (1 kênh).
2.  **Bước 2 - Giảm mẫu (Downsampling)**:
    *   Vì file có thể có hàng triệu điểm mẫu (quá nhiều để vẽ), ta chia file thành khoảng 600-1000 đoạn nhỏ.
3.  **Bước 3 - Tìm đỉnh (Min/Max Decimation)**:
    *   Trong mỗi đoạn nhỏ, tìm giá trị lớn nhất (Max) và nhỏ nhất (Min).
4.  **Bước 4 - Hiển thị**:
    *   Vẽ các đường thẳng nối từ Min đến Max cho từng đoạn để tạo hình dạng sóng.

### 3. Bồi âm (Harmonics Analysis)
*Mục đích: Tìm các tần số thành phần cấu tạo nên âm sắc.*

**Quy trình thực hiện:**
1.  **Bước 1 - Biến đổi Fourier (FFT)**:
    *   Lấy mẫu tín hiệu (toàn bộ hoặc một đoạn lớn).
    *   Chạy thuật toán **FFT (Fast Fourier Transform)** để chuyển từ miền Thời gian sang miền Tần số.
2.  **Bước 2 - Tính độ lớn (Magnitude)**:
    *   Tính biên độ tuyệt đối của kết quả số phức FFT: $|X[k]| = \sqrt{Re^2 + Im^2}$.
3.  **Bước 3 - Tìm đỉnh (Peak Picking)**:
    *   Quét qua phổ tần số để tìm các điểm đỉnh (local maxima) cục bộ.
    *   Lọc bỏ các đỉnh quá nhỏ (dưới ngưỡng 5-10% so với đỉnh cao nhất) để loại nhiễu.
4.  **Bước 4 - Sắp xếp & Hiển thị**:
    *   Sắp xếp các đỉnh theo thứ tự tần số tăng dần: Cơ bản ($f_0$), Bồi âm 2 ($2f_0$), Bồi âm 3 ($3f_0$)...
    *   Vẽ các vạch đứng (Bar chart) tại các tần số này.

---

## PHẦN 2: TRÍCH ĐẶC ĐIỂM CHI TIẾT (FEATURE EXTRACTION)

Đây là các bước tính toán theo chuẩn sách giáo khoa xử lý tín hiệu.

### 4.1. Short-time Energy (Năng lượng ngắn hạn)
**Quy trình:**
1.  Chia tín hiệu thành các khung nhỏ chồng lấp nhau (Overlapping Frames, ví dụ: dài 1024 mẫu, bước nhảy 512 mẫu).
2.  Với mỗi khung, bình phương giá trị của tất cả các mẫu (để lấy năng lượng dương): $x[n]^2$.
3.  Cộng tổng tất cả các bình phương đó lại: $E = \sum x[n]^2$.
4.  Lấy trung bình cộng của giá trị năng lượng E trên toàn bộ các khung.

### 4.2. Zero-crossing Rate (Tỷ lệ qua điểm 0)
**Quy trình:**
1.  Quét từng cặp mẫu liền kề nhau: $x[n]$ và $x[n-1]$.
2.  Kiểm tra dấu: Nếu tích $x[n] \cdot x[n-1] < 0$ nghĩa là dấu đã thay đổi (từ âm sang dương hoặc ngược lại).
3.  Đếm tổng số lần đổi dấu trong 1 giây.
4.  Chuẩn hóa về tỷ lệ (chia cho tổng số mẫu).

### 4.3. Endpoint Detection (Xác định độ dài hiệu dụng)
**Quy trình:**
1.  Tính năng lượng (dB) cho từng khung tín hiệu ngắn (khoảng 10-20ms).
2.  Đặt một **Ngưỡng (Threshold)**, ví dụ: 25dB so với nền yên tĩnh.
3.  Quét từ đầu file: Tìm điểm đầu tiên mà năng lượng vượt qua ngưỡng $\rightarrow$ **Điểm Bắt đầu (Start)**.
4.  Quét từ cuối file ngược lại: Tìm điểm đầu tiên mà năng lượng vượt qua ngưỡng $\rightarrow$ **Điểm Kết thúc (End)**.
5.  Độ dài hiệu dụng = (Thời gian End - Thời gian Start).

### 4.5. Formant Tracking (Dò tìm F1, F2)
**Quy trình:**
1.  Chọn một khung tín hiệu rõ nét nhất (thường ở giữa file, nơi âm thanh ổn định).
2.  Thực hiện **Phân tích LPC** (như phần 1) để tìm ra bộ hệ số đa thức $A(z)$.
3.  **Giải nghiệm đa thức**: Tìm các nghiệm (roots) của đa thức $A(z) = 0$ trên mặt phẳng phức.
4.  Lọc nghiệm:
    *   Chỉ giữ lại các nghiệm có phần ảo dương (nửa trên vòng tròn đơn vị).
    *   Tính góc pha ($\theta$) của nghiệm.
5.  **Chuyển đổi sang Hz**: $F = \theta \cdot \frac{SampleRate}{2\pi}$.
6.  Sắp xếp các tần số tìm được từ thấp đến cao. $F_1$ là tần số thấp nhất (sau $F_0$), $F_2$ là tần số tiếp theo.

### 4.6. Pitch Extraction (Dò Cao độ $f_0$) - Thuật toán YIN
**Quy trình:**
1.  **Bước 1 - Difference Function**: Thay vì nhân (như Autocorrelation), thuật toán YIN tính bình phương sai số giữa tín hiệu gốc và tín hiệu trễ.
    $$ d(\tau) = \sum (x[n] - x[n+\tau])^2 $$
2.  **Bước 2 - Cumulative Mean**: Chuẩn hóa hàm sai số để tránh lỗi ở độ trễ bằng 0.
3.  **Bước 3 - Tìm cực tiểu**: Tìm điểm trễ $\tau$ đầu tiên mà tại đó hàm sai số nhỏ hơn một ngưỡng nhất định.
4.  **Bước 4 - Nội suy (Interpolation)**: Tinh chỉnh giá trị $\tau$ bằng Parabolic Interpolation để đạt độ chính xác cao hơn cả tần số lấy mẫu.
5.  Kết quả: $f_0 = \frac{SampleRate}{\tau}$.

### 4.7. Phonetic Analysis (MFCCs)
**Quy trình "4 bước vàng" để trích xuất đặc trưng:**
1.  **Bước 1 - Frame & Window**: Chia nhỏ tín hiệu và áp dụng cửa sổ Hamming.
2.  **Bước 2 - FFT & Power Spectrum**: Chuyển sang miền tần số ($|FFT|^2$).
3.  **Bước 3 - Mel Filterbank**:
    *   Áp dụng bộ lọc tam giác theo thang đo Mel (mô phỏng tai người: độ phân giải cao ở tần số thấp, thấp ở tần số cao).
    *   Tính tổng năng lượng trong từng băng lọc.
    *   Lấy Logarithm của năng lượng (mô phỏng cảm nhận âm lượng của tai).
4.  **Bước 4 - DCT (Discrete Cosine Transform)**:
    *   Biến đổi ngược chuỗi Log-Energy.
    *   Giữ lại 13 hệ số đầu tiên. Đây chính là **MFCC véc-tơ**, đại diện cho âm sắc/ngữ âm của âm thanh đó.
