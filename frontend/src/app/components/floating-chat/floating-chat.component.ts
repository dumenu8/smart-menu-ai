import { Component, inject, signal, effect, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';

@Component({
    selector: 'app-floating-chat',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './floating-chat.component.html',
    styleUrls: ['./floating-chat.component.scss']
})
export class FloatingChatComponent {
    private chatService = inject(ChatService);

    // Bindings
    isOpen = this.chatService.isFloatingOpen;
    messages = this.chatService.messages;
    userInput = signal('');

    @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

    constructor() {
        // Auto-scroll effect
        effect(() => {
            this.messages();
            if (this.isOpen()) {
                setTimeout(() => this.scrollToBottom(), 50);
            }
        });
    }

    toggleChat() {
        this.chatService.toggleFloating();
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
