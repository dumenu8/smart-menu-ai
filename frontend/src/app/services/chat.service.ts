import { Injectable, signal } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, retry } from 'rxjs';

export interface ChatMessage {
    text: string;
    isUser: boolean;
    isTyping?: boolean; // For streaming indicator
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    // Global state for layout
    public isOpen = signal(false);
    public isFloatingOpen = signal(false); // State for the Floating FAB Chat
    public width = signal(400); // Default width in pixels

    // Chat content state (persisted across mode switches)
    public messages = signal<ChatMessage[]>([]);
    public isTyping = signal(false);

    private socket$: WebSocketSubject<any> | undefined;

    constructor() {
        // We don't subscribe to the socket here for message handling yet to avoid double subscription if not careful,
        // but actually, we SHOULD handle data accumulation here now.
        // Let's internally subscribe to the subject we created.
    }

    connect(): void {
        if (!this.socket$ || this.socket$.closed) {
            this.socket$ = webSocket({
                url: 'ws://localhost:8000/ws/chat',
                deserializer: msg => msg.data
            });

            this.socket$.pipe(
                retry({ delay: 3000 })
            ).subscribe({
                next: (msg) => {
                    this.handleIncomingChunk(msg);
                },
                error: (err) => console.error('WebSocket error:', err),
                complete: () => console.log('WebSocket connection closed')
            });
        }
    }

    toggleChat() {
        this.isOpen.update(v => !v);
    }

    toggleFloating() {
        this.isFloatingOpen.update(v => !v);
    }

    setWidth(w: number) {
        this.width.set(w);
    }

    sendMessage(text: string): void {
        // Add user message immediately
        this.messages.update(msgs => [...msgs, { text, isUser: true }]);
        this.isTyping.set(true);

        // Prepare placeholder for AI response
        this.messages.update(msgs => [...msgs, { text: '', isUser: false, isTyping: true }]);

        if (this.socket$) {
            this.socket$.next({ question: text });
        } else {
            console.warn('WebSocket not connected');
            this.connect();
            setTimeout(() => {
                if (this.socket$) this.socket$.next({ question: text });
            }, 1000);
        }
    }

    private handleIncomingChunk(chunk: string) {
        if (chunk === '[DONE]') {
            this.isTyping.set(false);
            this.messages.update(msgs => {
                const last = msgs[msgs.length - 1];
                if (last && !last.isUser) {
                    return [...msgs.slice(0, -1), { ...last, isTyping: false }];
                }
                return msgs;
            });
            return;
        }

        this.messages.update(msgs => {
            const newMsgs = [...msgs];
            const last = newMsgs[newMsgs.length - 1];
            if (last && !last.isUser) {
                last.text += chunk;
            }
            return newMsgs;
        });
    }

    disconnect(): void {
        if (this.socket$) {
            this.socket$.complete();
            this.socket$ = undefined;
        }
    }
}
