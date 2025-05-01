import { Component, OnInit } from '@angular/core';
import { ChatService } from '../../services/chat/chat.service';
import { Observable } from 'rxjs';
import { ChatReducedModel } from '../../types/chat.type';

@Component({
  selector: 'app-chat-list',
  standalone: false,
  templateUrl: './chat-list.component.html',
  styleUrl: './chat-list.component.scss'
})
export class ChatListComponent implements OnInit {

  chats$!: Observable<ChatReducedModel[]>;

  constructor(
    private chatService: ChatService,
  ) { }

  ngOnInit(): void {
    this.getChats();
  }

  getChats() {
    this.chats$ = this.chatService.get_chats();
  }

}
