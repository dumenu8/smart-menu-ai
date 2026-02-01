import { Component, inject, signal, effect, ElementRef, ViewChild, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatMessage } from '../../services/chat.service';

@Component({
    selector: 'app-chat-widget',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chat-widget.component.html',
    styleUrls: ['./chat-widget.component.scss']
})
export class ChatWidgetComponent {
    public chatService = inject(ChatService);

    // Bindings for template
    isOpen = this.chatService.isOpen;

    messages = this.chatService.messages;
    userInput = signal('');
    isTyping = this.chatService.isTyping;

    @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

    constructor() {
        // Auto-scroll effect
        effect(() => {
            this.messages(); // Dependency
            setTimeout(() => this.scrollToBottom(), 50);
        });
    }

    sendMessage() {
        const text = this.userInput().trim();
        if (!text) return;

        this.chatService.sendMessage(text);
        this.userInput.set('');
    }

    scrollToBottom() {
        if (this.scrollContainer) {
            this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
        }
    }
}
