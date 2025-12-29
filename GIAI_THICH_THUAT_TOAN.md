# GIẢI THÍCH CHI TIẾT CÁC KỸ THUẬT PHÂN TÍCH ÂM THANH

Tài liệu này giải thích chi tiết về nguyên lý hoạt động, cơ sở toán học và ý nghĩa của các công cụ phân tích tín hiệu âm thanh có trong ứng dụng.

---

## 1. Phân tích LPC (Linear Predictive Coding - Mã hóa Dự đoán Tuyến tính)

### 🧐 Khái niệm cơ bản
LPC là một trong những kỹ thuật mạnh mẽ nhất trong xử lý tiếng nói và nhạc cụ. Ý tưởng cốt lõi của nó dựa trên **Mô hình Nguồn-Bộ lọc (Source-Filter Model)**.

Hãy tưởng tượng cơ chế tạo âm thanh giống như việc chơi đàn Guitar:
*   **Nguồn (Source)**: Dây đàn rung lên. Tín hiệu này giàu năng lượng nhưng chưa có hình thù rõ ràng.
*   **Bộ lọc (Filter)**: Thùng đàn cộng hưởng. Thùng đàn sẽ khuếch đại một số tần số nhất định và làm yếu đi các tần số khác, tạo nên âm sắc đặc trưng của cây đàn.

LPC cố gắng tách biệt hai thành phần này ra khỏi âm thanh thu được để phân tích đặc tính của "thùng đàn" (tức là cấu trúc cộng hưởng của nhạc cụ hoặc thanh quản con người).

### 📐 Nguyên lý Toán học & Thuật toán
LPC giả định rằng pha mẫu hiện tại của tín hiệu âm thanh có thể được "dự đoán" bằng cách cộng gộp (tổ hợp tuyến tính) các mẫu trong quá khứ.

Công thức dự đoán:
$$ \hat{s}[n] = \sum_{k=1}^{p} a_k \cdot s[n-k] $$

Trong đó:
*   $ s[n] $: Giá trị mẫu âm thanh hiện tại.
*   $ s[n-k] $: Các mẫu âm thanh trong quá khứ.
*   $ a_k $: Các **hệ số LPC** (đây chính là cái chúng ta cần tìm).
*   $ p $: Bậc của bộ lọc (Order). Với nhạc cụ, ta thường chọn $p=20$ đến $30$ để mô tả chính xác.

**Cách tính toán:**
1.  **Tính sai số (Error)**: $ e[n] = s[n] - \hat{s}[n] $.
2.  **Tối ưu hóa**: Máy tính sẽ tìm bộ hệ số $ a_k $ sao cho tổng bình phương sai số $ E = \sum e[n]^2 $ là **nhỏ nhất**.
3.  **Thuật toán Levinson-Durbin**: Đây là giải thuật đệ quy cực nhanh được dùng để giải hệ phương trình tìm ra $ a_k $ từ hàm tự tương quan của tín hiệu.

### 💡 Ý nghĩa trong ứng dụng
Khi bạn thấy biểu đồ LPC, bạn đang nhìn thấy đường bao phổ (spectral envelope) mô tả đặc tính cộng hưởng của nhạc cụ. Các đỉnh nhọn trên đường LPC chính là các tần số cộng hưởng mạnh nhất.

---

## 2. Dạng sóng (Waveform)

### 🧐 Khái niệm cơ bản
Đây là hình ảnh chân thực nhất của âm thanh. Nó biểu diễn sự thay đổi của áp suất không khí (hoặc điện áp microphone) theo thời gian.

### 📐 Nguyên lý & Cách tính
*   **Trục hoành (Ngang)**: Thời gian (Time).
*   **Trục tung (Dọc)**: Biên độ (Amplitude).

Âm thanh trong máy tính được lưu trữ dưới dạng **PCM (Pulse Code Modulation)**. Tín hiệu liên tục được "chụp ảnh" (lấy mẫu) hàng nghìn lần mỗi giây (ví dụ: 44100 lần/giây).
Mỗi điểm trên biểu đồ Waveform chính là giá trị của một mẫu (sample) đó.

### 💡 Ý nghĩa
*   Nhìn vào độ cao thấp: Biết được âm lượng (Loudness).
*   Nhìn vào độ dày đặc: Biết được tần số sơ bộ (Cao độ).
*   Hình dạng đường bao (Envelope): Cho biết đặc tính ADSR (Attack, Decay, Sustain, Release) của nốt nhạc.

---

## 3. Bồi âm (Harmonics)

### 🧐 Khái niệm cơ bản
Một nốt nhạc không bao giờ chỉ có một tần số đơn lẻ. Khi bạn gảy nốt La (A4 - 440Hz), thực tế bạn đang nghe:
*   Tần số cơ bản ($f_0$): 440Hz (To nhất, quyết định cao độ).
*   Bồi âm bậc 2 ($2f_0$): 880Hz.
*   Bồi âm bậc 3 ($3f_0$): 1320Hz.
*   ... và vô số bồi âm khác nhỏ hơn.

Tập hợp các bồi âm này tạo nên **Âm sắc (Timbre)**. Tại sao Guitar và Piano chơi cùng nốt A4 nghe lại khác nhau? Chính là do cường độ các bồi âm này khác nhau.

### 📐 Nguyên lý Toán học (FFT)
Để tìm bồi âm, ta dùng phép biến đổi **FFT (Fast Fourier Transform)**.
FFT giúp "bẻ gãy" tín hiệu phức tạp theo thời gian thành các thành phần tần số đơn giản.

$$ X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j 2\pi k n / N} $$

### 💡 Ý nghĩa
Biểu đồ này cho bạn biết "công thức pha màu" của âm thanh. Những đỉnh nhọn trên biểu đồ chính là các bồi âm đang hiện diện.

---

## 4. Trích đặc điểm (Feature Extraction)

Phần này đi sâu vào các thông số định lượng (Quantitative Features) dùng trong nghiên cứu học thuật.

### 4.1. Short-time Energy (Năng lượng ngắn hạn)
*   **Khái niệm**: Đo lường cường độ âm thanh trong một khoảng thời gian cực ngắn (frame).
*   **Công thức**:
    $$ E_n = \sum_{m} [x(m) w(n-m)]^2 $$
    (Tổng bình phương biên độ các mẫu trong khung).
*   **Ý nghĩa**: Giúp phân biệt đoạn có âm thanh và khoảng lặng, hoặc sự thay đổi cường độ đột ngột (như tiếng trống).

### 4.2. Zero-crossing Rate (Tỷ lệ đi qua điểm 0)
*   **Khái niệm**: Đếm số lần tín hiệu đổi dấu (từ âm sang dương hoặc ngược lại) trong một đơn vị thời gian.
*   **Nguyên lý**:
    *   Âm thanh trầm (Bass): Sóng dao động chậm $\rightarrow$ Ít cắt trục 0 $\rightarrow$ ZCR thấp.
    *   Âm thanh cao/Tiếng ồn (Treble/Noise): Dao động nhanh $\rightarrow$ Cắt trục 0 liên tục $\rightarrow$ ZCR cao.
*   **Ý nghĩa**: Phân biệt tiếng ồn (như tiếng sáo gió, tiếng chũm chọe) với tiếng nhạc cụ có cao độ rõ ràng.

### 4.3. Endpoint Detection (Xác định điểm đầu cuối)
*   **Khái niệm**: Tự động cắt bỏ khoảng lặng vô nghĩa ở đầu và cuối file.
*   **Thuật toán**: Dựa trên hai ngưỡng (Threshold):
    1.  **Ngưỡng năng lượng**: Nếu năng lượng tín hiệu vượt quá ngưỡng này $\rightarrow$ Bắt đầu ghi nhận.
    2.  **Ngưỡng ZCR**: Đôi khi âm thanh bắt đầu bằng phụ âm vô thanh (năng lượng thấp nhưng ZCR cao), thuật toán sẽ kết hợp cả ZCR để bắt chính xác điểm bắt đầu.

### 4.5. Formant Tracking (Dò tìm Formant)
*   **Khái niệm**: Formant là các tần số cộng hưởng đặc trưng của ống cộng hưởng (thùng đàn, vòm họng).
*   **Thuật toán (Dựa trên LPC)**:
    1.  Tính hệ số LPC ($a_k$).
    2.  Coi các hệ số này là hệ số của một đa thức $ A(z) $.
    3.  Tìm **nghiệm (roots)** của đa thức này trên mặt phẳng phức.
    4.  Góc pha (angle) của các nghiệm phức này tương ứng trực tiếp với tần số của Formant.
*   **Ý nghĩa**: F1, F2 (Formant 1 và 2) quyết định nguyên âm chúng ta nghe được (A, O, E...) hoặc tính chất rỗng/đặc của thùng đàn.

### 4.6. Pitch Extraction (Trích xuất Cao độ - $f_0$)
*   **Phương pháp Autocorrelation (Tự tương quan)**:
    *   So sánh tín hiệu gốc với bản sao trễ của nó.
    *   Khi độ trễ (lag) trùng với **chu kỳ** của sóng, tín hiệu sẽ khớp nhau hoàn hảo $\rightarrow$ Hàm tương quan đạt đỉnh.
    *   Khoảng cách từ gốc đến đỉnh phụ đầu tiên chính là Chu kỳ cơ bản ($T_0$).
    *   Tần số $f_0 = 1/T_0$.
*   **Thuật toán YIN**:
    *   Là phiên bản cải tiến của Autocorrelation.
    *   Thay vì tìm cực đại của tích, nó tìm **cực tiểu** của hàm sai biệt (Difference Function). Giúp tránh lỗi "nhảy quãng 8" (Octave error) thường gặp.

### 4.7. Phonetic Analysis (MFCCs)
*   **Khái niệm**: MFCC (Mel-frequency Cepstral Coefficients) là đặc trưng mô phỏng cách tai người nghe âm thanh.
*   **Quy trình tính toán**:
    1.  **FFT**: Chuyển sang miền tần số.
    2.  **Mel Filterbank**: Gom nhóm năng lượng theo thang đo Mel (tai người nhạy cảm ở tần số thấp hơn tần số cao).
    3.  **Logarithm**: Lấy log (vì tai người cảm nhận âm lượng theo thang log).
    4.  **DCT (Biến đổi Cosine rời rạc)**: Bước cuối cùng để giải nén thông tin, tạo ra bộ hệ số MFCC.
*   **Ý nghĩa**: Đây là "vân tay" của âm thanh. Nó dùng để nhận dạng giọng nói, phân loại nhạc cụ, hoặc xác định âm sắc.
