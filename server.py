from fastapi import FastAPI
import requests
from LLM_gen.llm_predict import genai

app = FastAPI()


@app.post("/query")
async def get_info(query_text: str):
    # NLP
    conver_text = query_text.lower()

    # Gửi yêu cầu POST đến Rasa Action Server
    response = requests.post('http://127.0.0.1:5005/webhooks/rest/webhook',
                             json={"sender": "test", "message": query_text}).json()
    print("check res", response)
    # Kiểm tra phản hồi từ server
    # Kiểm tra phản hồi từ server
    if response:
        results = []  # Tạo danh sách để lưu kết quả
        for message in response:  # Duyệt qua từng mục trong danh sách phản hồi
            text = message.get("text", "")  # Lấy văn bản từ phản hồi, mặc định là chuỗi rỗng
            if text == "LLM_predict" or len(text) == 0:
                results.append(genai(conver_text))  # Thực hiện dự đoán nếu cần
            else:
                results.append(text)  # Thêm văn bản vào kết quả

        # Ghép tất cả văn bản thành một chuỗi
        final_response = "\n".join(results)
        print("Response from Rasa:", final_response)
    else:
        print(f"Failed to get a response.")

    return final_response


# Chạy ứng dụng FastAPI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)