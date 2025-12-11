'use client';

import { Button } from '@/components/ui/button';
import { ChatErrorBoundary } from '@/components/ui/ErrorBoundary';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Volume2, VolumeX } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { EnhancedChatInput } from './EnhancedChatInput';
import { EnhancedMessage } from './EnhancedMessage';
// import { WelcomeMessage } from './WelcomeMessage';
// import { SuccessNotification } from './SuccessNotification';
// import { ErrorMessage } from './ErrorMessage';
import { scheduleAIClient } from '@/utils/scheduleai-client';
import { AppointmentData, Message } from '@/utils/types';

interface EnhancedChatInterfaceProps {
  sessionId?: string;
  businessId?: string;
  consultantId?: string;
  onAppointmentCreated?: (appointment: AppointmentData) => void;
}

export const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({
  sessionId = 'default',
  businessId,
  consultantId,
  onAppointmentCreated
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?',
      role: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [isSoundEnabled, setIsSoundEnabled] = useState(true);
  const [lastActivity, setLastActivity] = useState<Date>(new Date());
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollArea = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]') as HTMLElement;
      if (scrollArea) {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }
    }
  }, [messages, streamingMessage]);

  // Update last activity
  const updateActivity = useCallback(() => {
    setLastActivity(new Date());
  }, []);

  // Play sound notification
  const playNotificationSound = useCallback(() => {
    if (isSoundEnabled && typeof window !== 'undefined') {
      try {
        const audio = new Audio('/sounds/notification.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {
          // Ignore audio play errors
        });
      } catch (error) {
        console.log('Audio notification failed:', error);
      }
    }
  }, [isSoundEnabled]);

  // Handle message sending
  const handleSendMessage = useCallback(async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) return;

    updateActivity();
    setShowWelcome(false);
    setError(null);

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent.trim(),
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      console.log('🚀 Sending message to ScheduleAI...');

      const response = await scheduleAIClient.sendMessage(
        messageContent.trim(),
        sessionId,
        {
          businessId,
          consultantId
        }
      );

      console.log('✅ Got response from ScheduleAI:', response);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response,
        role: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      playNotificationSound();

      // Check if response contains appointment data
      if (response.toLowerCase().includes('appuntamento confermato') ||
        response.toLowerCase().includes('prenotazione effettuata')) {
        // Extract appointment data if available
        if (onAppointmentCreated) {
          // This would need to be enhanced to parse actual appointment data
          onAppointmentCreated({
            clientName: 'Cliente',
            serviceType: 'Servizio',
            dateTime: new Date().toISOString(),
            duration: 60,
            status: 'confirmed'
          });
        }
      }

    } catch (error) {
      console.error('❌ Error sending message:', error);

      let errorMessage = 'Si è verificato un errore durante la comunicazione con l\'assistente. Riprova più tardi.';

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return; // Request was cancelled
        }

        if (error.message.includes('fetch') || error.message.includes('network')) {
          errorMessage = 'Impossibile connettersi al server. Controlla la tua connessione internet.';
        } else if (error.message.includes('404')) {
          errorMessage = 'Servizio non disponibile. Riprova più tardi.';
        } else if (error.message.includes('500')) {
          errorMessage = 'Il server sta riscontrando problemi tecnici. Riprova più tardi.';
        } else {
          errorMessage = `Errore: ${error.message}`;
        }
      }

      setError(errorMessage);

      // Add error message to chat
      const errorChatMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessage,
        role: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorChatMessage]);

    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [isLoading, sessionId, businessId, consultantId, onAppointmentCreated, updateActivity, playNotificationSound]);

  // Handle attachment click
  const handleAttachmentClick = useCallback(() => {
    // Placeholder for attachment functionality
    console.log('Attachment clicked - feature coming soon');
  }, []);

  // Handle voice recording
  const handleVoiceRecordClick = useCallback(() => {
    // Placeholder for voice recording functionality
    console.log('Voice recording clicked - feature coming soon');
  }, []);

  // Handle retry
  const handleRetry = useCallback(() => {
    setError(null);
    if (messages.length > 0) {
      const lastUserMessage = messages
        .filter(m => m.role === 'user')
        .pop();
      if (lastUserMessage) {
        handleSendMessage(lastUserMessage.content);
      }
    }
  }, [messages, handleSendMessage]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <ChatErrorBoundary>
      <div className="flex flex-col h-full bg-background">
        {/* Messages Area */}
        <ScrollArea
          ref={scrollAreaRef}
          className="flex-1 custom-scrollbar"
          role="log"
          aria-label="Messaggi della chat"
          aria-live="polite"
        >
          <div className="p-4 space-y-4">
            {/* Welcome Message */}
            {/* {showWelcome && messages.length === 1 && (
              <WelcomeMessage />
            )} */}

            {/* Messages */}
            {messages.map((message) => (
              <EnhancedMessage
                key={message.id}
                message={message}
                isStreaming={message === messages[messages.length - 1] && isLoading}
              />
            ))}

            {/* Streaming Message */}
            {isLoading && streamingMessage && (
              <EnhancedMessage
                message={{
                  id: 'streaming',
                  content: streamingMessage,
                  role: 'assistant',
                  timestamp: new Date()
                }}
                isStreaming={true}
              />
            )}

            {/* Loading Indicator */}
            {isLoading && !streamingMessage && (
              <div className="flex gap-3 justify-start">
                <div className="flex items-center gap-2 py-3 px-4 bg-muted rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm text-muted-foreground">Sto scrivendo...</span>
                </div>
              </div>
            )}

            {/* Error Notification */}
            {/* {error && (
              <ErrorMessage
                error={error}
                onRetry={handleRetry}
                onDismiss={clearError}
              />
            )} */}
          </div>
        </ScrollArea>

        <Separator />

        {/* Sound Toggle */}
        <div className="flex items-center justify-between px-4 py-2 border-b">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Notifiche sonore</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSoundEnabled(!isSoundEnabled)}
            className="h-8 w-8 p-0"
            aria-label={isSoundEnabled ? "Disattiva suoni" : "Attiva suoni"}
          >
            {isSoundEnabled ? (
              <Volume2 className="w-4 h-4" />
            ) : (
              <VolumeX className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Enhanced Input Area */}
        <EnhancedChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          showShortcuts={true}
          allowAttachments={true}
          allowVoiceRecording={true}
          onAttachmentClick={handleAttachmentClick}
          onVoiceRecordClick={handleVoiceRecordClick}
          maxLength={1000}
        />
      </div>
    </ChatErrorBoundary>
  );
};

export default EnhancedChatInterface;