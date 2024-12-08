from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import os
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

# Các mảng chứa các địa điểm
chonoicairang_arr = ["chợ nổi cái răng cần thơ", "chợ nổi cái răng", "chợ nổi","chợ nổi cái","nổi cái răng","cái răng"]
benninhkieu_arr = ["bến ninh kiều", "ninh kiều", "ben ninh kieu", "ninh kieu", "ben", "benninhkieu"]
langmykhanh_arr = ["làng du lịch mỹ khánh", "du lịch mỹ khánh", "làng du lịch", "mỹ khánh","làng mỹ khánh","làng du lịch mỹ","làng du"]
thienvientruc_arr = ["thiền viện trúc lâm phương nam", "thiền viện trúc lâm", "thiền viện","thiền" ,"thiền viện phương nam","thiền viện trúc","viện trúc","viện trúc lâm"]
vuonco_arr = ["vườn cò bằng lăng", "vườn cò","vườn cò bằng","bằng lăng","cò bằng lăng"]
restaurant_arr=["quán ăn","nhà hàng buffet","buffet","nhà hàng","quán ăn vặt","quán cà phê","món chay","chỗ ăn","mon an","dac san","cho an","restaurant","hủ tiếu ngon","món đặc trưng miền Tây","quán ăn hải sản","nhà hàng trên sông","quán ăn","nhà hàng","món ăn","món chay","địa điểm ăn uống","món ăn nổi bật","mon chay","quán bún","quán cơm"]
hotel_arr= ["nhà nghỉ","khách sạn","chỗ nghỉ","chỗ ở","phòng trọ","chỗ nghỉ chân","khu nghỉ dưỡng","cho nghi ngoi","cho ngu","khach san","nha nghi","hotel"]
vehicle_arr=["phương tiện","thuê xe nào","đi thuyền","xe ôm","xe buýt","taxi","xe máy","đi bộ","dịch vụ cho thuê xe","phương tiện nào là tốt nhất","xe bus"]

def main(question):
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


    
def extract_budget_value(budget_entity):
    donViNghin = ['k', 'nghìn']
    donViTrieu = ['tr', 'triệu', 'củ']
    donVikhac = ['giá rẻ', 'rẻ', 'thấp', 'giá thấp']
    
    so = 0
    numbers = ''.join([char for char in budget_entity if char.isdigit()])
    
    if numbers:
        so = int(numbers)
        donVi = budget_entity.replace(str(so), '').strip()
        
        if donVi in donViNghin:
            so *= 1000
        elif donVi in donViTrieu:
            so *= 1000000
    
    else:
        so = 1000000
    
    return so, donVikhac

class ActionExtractLocation(Action):
    def name(self) -> Text:
        return "action_extract_location"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location_entity = next(tracker.get_latest_entity_values("location"), None)
        restaurant_entity = next(tracker.get_latest_entity_values("restaurant"), None)
        hotel_entity = next(tracker.get_latest_entity_values("hotel"), None)
        vehicle_entity = next(tracker.get_latest_entity_values("vehicle"), None)
        budget_entity = next(tracker.get_latest_entity_values("budget"), None)

        response_sent = False  # Biến cờ để kiểm tra phản hồi
        location_entity = location_entity.lower() if location_entity else None
        
        other_entities = {
            "restaurant": restaurant_entity.lower() if restaurant_entity else None,
            "vehicle": vehicle_entity.lower() if vehicle_entity else None,
            "hotel": hotel_entity.lower() if hotel_entity else None,
            "budget": budget_entity.lower() if budget_entity else None,
        }

        location_services = {
            "chonoicairang_arr": "utter_ask_chonoicairang",
            "benninhkieu_arr": "utter_ask_benninhkieu",
            "langmykhanh_arr": "utter_ask_langmykhanh",
            "thienvientruc_arr": "utter_ask_thienvientruc",
            "vuonco_arr": "utter_ask_vuonco",
        }
        services_entites = False
        check_vuonco = False
        if location_entity in vuonco_arr:
            check_vuonco= True
        print(location_entity, " ",restaurant_entity, " ", hotel_entity, " ",vehicle_entity," ",budget_entity )
        if location_entity:
            for typ , entity in other_entities.items():
                if entity :
                    services_entites= True
            print(services_entites)
            if budget_entity and hotel_entity :
                so, donVikhac = extract_budget_value(budget_entity)
                print("gia", so)
                for location_arr, response in location_services.items():
                    if location_entity in globals().get(location_arr, []):
                        print(location_arr[:-4])
                        if so <= 1500000 or budget_entity in donVikhac:
                            dispatcher.utter_message(response=f"utter_{location_arr[:-4]}_hotel_duoi_1trieu")
                            print("phan hoi la ",f"utter_{location_arr[:-4]}_hotel_duoi_1trieu")
                            response_sent = True
                        elif so < 3000000:
                            dispatcher.utter_message(response=f"utter_{location_arr[:-4]}_hotel_duoi_3trieu")
                            response_sent = True
                            print("phan hoi la ",f"utter_{location_arr[:-4]}_hotel_duoi_3trieu")
                        else:
                            dispatcher.utter_message(response=f"utter_{location_arr[:-4]}_hotel_tren_3trieu")
                            response_sent = True
                            print("phan hoi la ",f"utter_{location_arr[:-4]}_hotel_tren_3trieu")
            
            else :      
                if not services_entites :
                    for location_arr, response in location_services.items():
                        if location_entity in globals().get(location_arr, []):
                            dispatcher.utter_message(response= f"utter_ask_{location_arr[:-4]}")
                            response_sent = True
                        
                for location_arr, response in location_services.items():
                    # Kiểm tra nếu location_entity có trong mảng địa điểm
                    if location_entity in globals().get(location_arr, []):
                        # Nếu có thực thể dịch vụ khác, phản hồi theo dịch vụ đó
                        for entity_type, entity_value in other_entities.items():
                            if entity_value:
                                print(entity_type," ",entity_value)
                                # Tạo phản hồi cho dịch vụ với địa điểm tương ứng
                                service_response = f"utter_ask_{entity_type}_{location_arr[:-4]}"  # Bỏ '_arr' khỏi tên địa điểm
                                print("phan hoi utter la:",service_response)
                                dispatcher.utter_message(response= service_response)
                                response_sent = True
        else :
            print ("khong bat dc location")
            user_question = tracker.latest_message.get('text')  # Lấy câu hỏi người dùng
            answer_from_groq = main(user_question)  # Gọi API Groq
            dispatcher.utter_message(text=answer_from_groq)
            response_sent = True
                            
        # Nếu không tìm thấy phản hồi, sử dụng API Groq
        if not response_sent or check_vuonco == True :
            print("khong co phan hoi")
            user_question = tracker.latest_message.get('text')  # Lấy câu hỏi người dùng
            answer_from_groq = main(user_question)  # Gọi API Groq
            dispatcher.utter_message(text=answer_from_groq)
                
        return []
