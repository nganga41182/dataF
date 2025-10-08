Rất sẵn lòng! Với kinh nghiệm triển khai ứng dụng Streamlit, tôi sẽ cung cấp cho bạn một khung mã Python hoàn chỉnh để tích hợp chức năng chat với Gemini, sử dụng các phương pháp tốt nhất của Streamlit như st.session_state để quản lý lịch sử trò chuyện.

Vì bạn muốn giữ nguyên các đoạn mã khác của mình, tôi sẽ trình bày phần mã dưới dạng các hàm hoặc khối logic có thể dễ dàng chèn vào tệp python.py của bạn.

🛠️ Khung Chat Gemini Tích Hợp Streamlit
Đây là đoạn mã cần thiết để tạo giao diện khung chat và tương tác với API Gemini. Bạn chỉ cần đảm bảo rằng thư viện google-genai đã được cài đặt (pip install google-genai).

Bước 1: Khai báo và Thiết lập API Key
Bạn nên đặt phần này ở đầu tệp python.py của mình, ngay sau các lệnh import khác.

Python

import streamlit as st
from google import genai
from google.genai.errors import APIError
import os

# --- Cấu hình Gemini ---
# KHUYÊN DÙNG: Sử dụng st.secrets cho Streamlit Cloud hoặc os.getenv cho Local
try:
    # Ưu tiên đọc từ Streamlit secrets (khuyến nghị cho deploy)
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, AttributeError):
    # Nếu không có secrets, đọc từ biến môi trường
    API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    try:
        # Khởi tạo client Gemini
        client = genai.Client(api_key=API_KEY)
        MODEL_NAME = "gemini-2.5-flash" 
    except Exception as e:
        st.error(f"Lỗi khi khởi tạo Gemini client: {e}")
        client = None
else:
    st.error("Lỗi: Không tìm thấy khóa API Gemini. Vui lòng đặt khóa vào biến môi trường 'GEMINI_API_KEY' hoặc tệp 'secrets.toml'.")
    client = None
Bước 2: Hàm Chính Tạo Khung Chat
Bạn có thể đặt toàn bộ logic chat này vào một hàm và gọi nó tại vị trí bạn muốn khung chat xuất hiện trong ứng dụng của mình.

Python

def gemini_chat_interface():
    """Tạo giao diện khung chat tương tác với Gemini."""
    
    # 1. Khởi tạo Lịch sử Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Thêm tin nhắn chào mừng ban đầu
        st.session_state.messages.append({"role": "assistant", "content": "Xin chào! Tôi là Gemini. Bạn có câu hỏi gì cho tôi không?"})

    # 2. Hiển thị Lịch sử Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Khung Chat Input (Đầu vào của người dùng)
    if prompt := st.chat_input("Nhập câu hỏi của bạn ở đây..."):
        
        if not client:
            st.error("Không thể gửi tin nhắn. Vui lòng kiểm tra cấu hình API Key.")
            return

        # Thêm tin nhắn của người dùng vào lịch sử và hiển thị
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4. Chuẩn bị và Gửi yêu cầu đến Gemini
        with st.chat_message("assistant"):
            with st.spinner("Gemini đang suy nghĩ..."):
                try:
                    # Chuyển đổi lịch sử Streamlit sang định dạng API cần thiết
                    chat_history_for_api = [
                        {"role": "model" if msg["role"] == "assistant" else "user", 
                         "parts": [{"text": msg["content"]}]}
                        # Bỏ qua tin nhắn chào mừng và tin nhắn cuối cùng của user
                        for msg in st.session_state.messages[:-1]
                        if msg["content"] != "Xin chào! Tôi là Gemini. Bạn có câu hỏi gì cho tôi không?"
                    ]

                    # Khởi tạo phiên chat (để Gemini duy trì ngữ cảnh)
                    chat = client.chats.create(
                        model=MODEL_NAME,
                        history=chat_history_for_api
                    )
                    
                    # Gửi tin nhắn mới nhất
                    response = chat.send_message(prompt)
                    full_response = response.text
                    
                    # HIển thị phản hồi
                    st.markdown(full_response)
                    
                    # Thêm phản hồi của trợ lý vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                except APIError as e:
                    error_message = f"Lỗi API: Không thể giao tiếp với Gemini. Lỗi: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                except Exception as e:
                    error_message = f"Đã xảy ra lỗi không mong muốn: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})


# --- LƯU Ý: Phần mã của bạn (ví dụ: các hàm, giao diện khác) ở đây ---
# st.header("Ứng Dụng Chính Của Tôi") 
# # ... đoạn code khác của bạn ...
# st.write("Đây là nội dung trước khung chat.")


# --- VỊ TRÍ GỌI HÀM CHAT ---
# Gọi hàm này tại vị trí bạn muốn khung chat xuất hiện
if __name__ == '__main__':
    st.title("Ứng Dụng Của Tôi + Chatbot Gemini")
    
    # Giả sử đây là đoạn mã ban đầu của bạn
    st.write("Dữ liệu và giao diện chính của ứng dụng bạn ở đây.")
    # st.selectbox(...)
    # st.dataframe(...)
    
    # Gọi hàm chat
    st.divider() # Dùng để phân tách rõ ràng giao diện chính và khung chat
    st.subheader("Trò chuyện với Gemini")
    gemini_chat_interface()
