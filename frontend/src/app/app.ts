import { Component, signal, inject, HostListener } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { ChatWidgetComponent } from './components/chat-widget/chat-widget.component';
import { FloatingChatComponent } from './components/floating-chat/floating-chat.component';
import { ChatService } from './services/chat.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, ChatWidgetComponent, FloatingChatComponent, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  chatService = inject(ChatService);
  isResizing = false;

  startResizing(event: MouseEvent) {
    this.isResizing = true;
    event.preventDefault();
  }

  @HostListener('window:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (!this.isResizing) return;
    const newWidth = window.innerWidth - event.clientX;
    // Constrain width
    if (newWidth > 300 && newWidth < 800) {
      this.chatService.setWidth(newWidth);
    }
  }

  @HostListener('window:mouseup')
  stopResizing() {
    this.isResizing = false;
  }
}
