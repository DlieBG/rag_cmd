import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ChatIdModel, ChatModel, ChatReducedModel, LLMType, MessageModel } from '../../types/chat.type';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  constructor(
    private httpClient: HttpClient,
  ) { }

  get_chats(): Observable<ChatReducedModel[]> {
    return this.httpClient.get<ChatReducedModel[]>('api/chat');
  }

  get_chat(id: string): Observable<ChatModel> {
    return this.httpClient.get<ChatModel>(`api/chat/${id}`);
  }

  create_chat(llm_type: LLMType): Observable<ChatIdModel> {
    return this.httpClient.post<ChatIdModel>('api/chat', {
      llm_type,
    });
  }

  send_message(id: string, text: string): Observable<MessageModel[]> {
    return this.httpClient.put<MessageModel[]>(`api/chat/${id}/message`, {
      text,
    });
  }

  remove_chat(id: string) {
    return this.httpClient.delete(`api/chat/${id}`);
  }

}
