'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { chatToasts, useToast } from '@/contexts/ToastContext';
import { scheduleAIClient } from '@/utils/scheduleai-client';
import { AppointmentData, Message } from '@/utils/types';
import { Bot } from 'lucide-react';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { EnhancedChatInput } from './EnhancedChatInput';
import { EnhancedMessage } from './EnhancedMessage';

interface ChatInterfaceProps {
  sessionId?: string;
  businessId?: string;
  consultantId?: string;
  onAppointmentCreated?: (appointment: AppointmentData) => void;
  onMessagesUpdate?: (sessionId: string, messages: Message[]) => void;
  initialMessages?: Message[];
}

export function ChatInterface({
  sessionId = 'default',
  businessId,
  consultantId,
  onAppointmentCreated,
  onMessagesUpdate,
  initialMessages
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages || [
    {
      id: '1',
      content: 'Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?',
      role: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const pendingParentUpdate = useRef<{ sessionId: string; messages: Message[] } | null>(null);
  const { showSuccess, showError, showInfo } = useToast();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle pending parent updates safely after render
  useLayoutEffect(() => {
    if (pendingParentUpdate.current && onMessagesUpdate) {
      onMessagesUpdate(pendingParentUpdate.current.sessionId, pendingParentUpdate.current.messages);
      pendingParentUpdate.current = null;
    }
  });

  // Update messages when initialMessages prop changes (different session selected)
  useEffect(() => {
    if (initialMessages) {
      setMessages(initialMessages);
    }
  }, [sessionId]); // Only re-run when session changes, not when initialMessages changes

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message.trim(),
      role: 'user',
      timestamp: new Date()
    };

    // Add user message and schedule parent update
    setMessages(prev => {
      const newMessages = [...prev, userMessage];
      pendingParentUpdate.current = { sessionId, messages: newMessages };
      return newMessages;
    });

    setIsLoading(true);

    try {
      console.log('🚀 Sending message to ScheduleAI...');

      const response = await scheduleAIClient.sendMessage(
        message.trim(),
        sessionId,
        {
          businessId,
          consultantId
        }
      );

      console.log('✅ Got response from ScheduleAI:', response);

      // Check if response contains appointment creation confirmation
      if (response.toLowerCase().includes('appuntamento creato') ||
        response.toLowerCase().includes('prenotazione confermata')) {
        showSuccess('Appuntamento creato con successo!');
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response,
        role: 'assistant',
        timestamp: new Date()
      };

      // Add assistant message and schedule parent update
      setMessages(prev => {
        const newMessages = [...prev, assistantMessage];
        pendingParentUpdate.current = { sessionId, messages: newMessages };
        return newMessages;
      });
    } catch (error) {
      console.error('❌ Error sending message:', error);
      showError(chatToasts.messageError());

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Mi dispiace, si è verificato un errore: ${error}. Riprova più tardi.`,
        role: 'assistant',
        timestamp: new Date()
      };

      // Add error message and schedule parent update
      setMessages(prev => {
        const newMessages = [...prev, errorMessage];
        pendingParentUpdate.current = { sessionId, messages: newMessages };
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return scheduleAIClient.formatTime(date);
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Messages Area */}
      <ScrollArea
        ref={scrollAreaRef}
        className="flex-1 p-4 space-y-4"
      >
        {messages.map((message) => (
          <EnhancedMessage
            key={message.id}
            message={message}
            isStreaming={false}
          />
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <Avatar className="w-10 h-10 flex-shrink-0 mt-1">
              <AvatarFallback className="bg-blue-500 text-white shadow-lg">
                <Bot className="w-5 h-5" />
              </AvatarFallback>
            </Avatar>
            <Card className="p-4 bg-muted max-w-[70%] lg:max-w-[60%]">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-muted-foreground">
                  Sto scrivendo...
                </span>
              </div>
            </Card>
          </div>
        )}
      </ScrollArea>

      <Separator />

      {/* Enhanced Input Area */}
      <EnhancedChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="Scrivi il tuo messaggio..."
        showShortcuts={true}
        allowAttachments={true}
        allowVoiceRecording={true}
      />
    </div>
  );
}