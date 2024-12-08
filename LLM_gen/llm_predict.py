from groq import Groq
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

def genai(question):
    """
    Function trả về output từ Groq API dựa trên câu hỏi đầu vào mà không cần giao diện.
    """
    
    # Lấy API key của Groq
    groq_api_key = "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"
    # Thiết lập các thông số
    system_prompt = "Bạn là một hướng dẫn viên du lịch giàu kinh nghiệm ở Cần Thơ. Hãy trả lời câu hỏi về các điểm du lịch, nhà hàng, và hoạt động giải trí với sự thân thiện và chi tiết liên quan đến các địa điểm sau : Vườn cò Bằng Lăng , thiền viện Trúc Lâm Phương Nam, Bến Ninh Kiều , chợ nổi Cái Răng."
    model = 'llama-3.1-70b-versatile'
    conversational_memory_length = 5
    limit_token=4096
    user_question = question

    # Bộ nhớ hội thoại
    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    # Khởi tạo đối tượng chat Groq
    groq_chat = ChatGroq(
        groq_api_key= groq_api_key, 
        model_name=model,
        max_tokens=limit_token
    )

    # Xử lý câu hỏi và tạo prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=system_prompt
            ),  # Prompt hệ thống
            MessagesPlaceholder(
                variable_name="chat_history"
            ),  # Lịch sử chat (nếu có)
            HumanMessagePromptTemplate.from_template(
                "{human_input}"
            ),  # Câu hỏi của người dùng
        ]
    )

    # Chuỗi hội thoại
    conversation = LLMChain(
        llm=groq_chat,  # Chatbot Groq
        prompt=prompt,  # Prompt template
        verbose=True,   # Xuất chi tiết
        memory=memory,  # Bộ nhớ hội thoại
    )
    
    # Dự đoán câu trả lời
    response = conversation.predict(human_input=user_question)
    return response