import streamlit as st
from google import genai
from google.genai.errors import APIError
import os
# --- Cấu hình ------------------------------------------------------------------

# Tên biến môi trường chứa API Key. Bạn nên đặt khóa API trong biến môi trường
# tên là GEMINI_API_KEY
# Nếu không, bạn cần thay thế os.getenv("GEMINI_API_KEY") bằng khóa API của bạn
# (nhưng KHÔNG NÊN LÀM VẬY trong ứng dụng thực tế).
API_KEY = os.getenv("GEMINI_API_KEY")

# Khởi tạo client Gemini.
try:
    if API_KEY:
        client = genai.Client(api_key=API_KEY)
    else:
        st.error("Lỗi: Không tìm thấy khóa API. Vui lòng đặt khóa API của bạn vào biến môi trường 'GEMINI_API_KEY'.")
        client = None # Vẫn thiết lập client thành None nếu lỗi
except Exception as e:
    st.error(f"Lỗi khi khởi tạo client Gemini: {e}")
    client = None

# Mô hình sử dụng
MODEL_NAME = "gemini-2.5-flash" 

# --- Giao diện và Logic Streamlit ----------------------------------------------

st.set_page_config(page_title="Streamlit Chatbot với Gemini 🤖", layout="centered")
st.title("Chatbot Hỏi Đáp với Gemini 💬")

# 1. Khởi tạo Lịch sử Chat
# Sử dụng st.session_state để lưu trữ lịch sử cuộc trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Thêm tin nhắn chào mừng ban đầu
    st.session_state.messages.append({"role": "assistant", "content": "Xin chào! Tôi là Gemini. Bạn có câu hỏi gì cho tôi không?"})

# 2. Hiển thị Lịch sử Chat
# Lặp qua tất cả tin nhắn đã lưu và hiển thị chúng
for message in st.session_state.messages:
    # Sử dụng st.chat_message để hiển thị tin nhắn với avatar phù hợp
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Khung Chat Input (Đầu vào của người dùng)
# st.chat_input sẽ luôn nằm ở cuối màn hình và trả về nội dung khi người dùng nhấn Enter
if prompt := st.chat_input("Nhập câu hỏi của bạn ở đây..."):
    if not client:
        # Nếu client không được khởi tạo (do thiếu API Key), dừng lại
        st.error("Không thể gửi tin nhắn. Vui lòng kiểm tra cấu hình API Key.")
    else:
        # Thêm tin nhắn của người dùng vào lịch sử và hiển thị
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4. Gọi API Gemini và Xử lý Phản hồi
        with st.chat_message("assistant"):
            # st.spinner sẽ hiển thị thông báo "Đang chạy..." trong khi chờ phản hồi
            with st.spinner("Gemini đang suy nghĩ..."):
                try:
                    # Tạo một chuỗi lịch sử chat để truyền cho mô hình
                    # Đây là cách đơn giản, nhưng bạn có thể dùng genai.Chat (client.chats.create)
                    # cho các cuộc trò chuyện phức tạp hơn và có ngữ cảnh dài.
                    
                    # Tùy chọn 1: Sử dụng genai.Chat để quản lý lịch sử trò chuyện
                    # (Khuyên dùng cho ứng dụng chat thực tế)
                    
                    # Chuyển đổi lịch sử st.session_state thành định dạng cần thiết
                    history = []
                    for message in st.session_state.messages:
                        # Bỏ qua tin nhắn chào mừng ban đầu (vì nó không phải là phần của lịch sử chat API)
                        if message.get("role") != "assistant" or message.get("content") != "Xin chào! Tôi là Gemini. Bạn có câu hỏi gì cho tôi không?":
                            # Lược đồ API yêu cầu 'model' là 'assistant' và 'user' là 'user'
                            api_role = "model" if message["role"] == "assistant" else "user"
                            history.append({"role": api_role, "parts": [{"text": message["content"]}]})
                    
                    # Chỉ lấy lịch sử thực tế (bỏ tin nhắn chào mừng và tin nhắn cuối cùng của user để tránh trùng lặp)
                    # Lấy tất cả tin nhắn *trừ* tin nhắn user vừa gửi
                    chat_history_for_api = [
                        {"role": "model" if msg["role"] == "assistant" else "user", "parts": [{"text": msg["content"]}]}
                        for msg in st.session_state.messages[:-1]
                        if msg["content"] != "Xin chào! Tôi là Gemini. Bạn có câu hỏi gì cho tôi không?" # Bỏ tin nhắn chào mừng
                    ]
                    
                    # Khởi tạo hoặc tiếp tục cuộc trò chuyện
                    chat = client.chats.create(
                        model=MODEL_NAME,
                        history=chat_history_for_api # Truyền lịch sử trước đó
                    )
                    
                    # Gửi tin nhắn mới nhất
                    response = chat.send_message(prompt)
                    
                    # Lấy nội dung phản hồi
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
💡 Hướng Dẫn Tích Hợp và Chạy
1. Cài đặt Thư viện
Bạn cần cài đặt thư viện Streamlit và thư viện Python của Google GenAI.

Bash

pip install streamlit google-genai
