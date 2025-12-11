'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { scheduleAIClientFixed } from '@/lib/scheduleai-client-fixed';
import { AppointmentData, Message } from '@/utils/types';
import { AlertCircle, Bot, Calendar, Clock, Send, User } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';

interface ChatInterfaceProps {
  sessionId?: string;
  businessId?: string;
  consultantId?: string;
  onAppointmentCreated?: (appointment: AppointmentData) => void;
}

export function ChatInterfaceFixed({
  sessionId = 'default',
  businessId,
  consultantId,
  onAppointmentCreated
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?',
      role: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Check backend connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const checkConnection = async () => {
    try {
      setConnectionStatus('checking');
      const connectionResult = await scheduleAIClientFixed.testConnection();

      if (connectionResult.success) {
        setConnectionStatus('connected');
        console.log('✅ Backend connected:', connectionResult);
      } else {
        setConnectionStatus('error');
        console.error('❌ Backend connection failed:', connectionResult);
      }
    } catch (error) {
      setConnectionStatus('error');
      console.error('❌ Connection check error:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('🚀 Sending message to ScheduleAI Fixed Client...');
      console.log(`📝 Message: ${inputValue.trim()}`);
      console.log(`🔑 Session ID: ${sessionId}`);

      const response = await scheduleAIClientFixed.sendMessage(
        inputValue.trim(),
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
    } catch (error) {
      console.error('❌ Error sending message:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Mi dispiace, si è verificato un errore: ${error}. Riprova più tardi.`,
        role: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return scheduleAIClientFixed.formatTime(date);
  };

  const getConnectionStatusBadge = () => {
    switch (connectionStatus) {
      case 'checking':
        return (
          <Badge variant="outline" className="text-yellow-600">
            <AlertCircle className="w-3 h-3 mr-1" />
            Verificando connessione...
          </Badge>
        );
      case 'connected':
        return (
          <Badge variant="default" className="text-green-600">
            <AlertCircle className="w-3 h-3 mr-1" />
            Connesso al backend
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="destructive">
            <AlertCircle className="w-3 h-3 mr-1" />
            Errore di connessione
          </Badge>
        );
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Connection Status Header */}
      <div className="flex items-center justify-between p-3 border-b bg-muted/30">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4" />
          <span className="text-sm font-medium">ScheduleAI Assistant</span>
        </div>
        {getConnectionStatusBadge()}
      </div>

      {/* Messages Area */}
      <ScrollArea
        ref={scrollAreaRef}
        className="flex-1 p-4 space-y-4"
      >
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
          >
            {message.role === 'assistant' && (
              <Avatar className="w-8 h-8 mt-1">
                <AvatarFallback className="bg-blue-500 text-white">
                  <Bot className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
            )}

            <div
              className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : 'order-2'
                }`}
            >
              <Card
                className={`p-3 ${message.role === 'user'
                    ? 'bg-blue-500 text-white ml-auto'
                    : 'bg-muted'
                  }`}
              >
                <p className="text-sm whitespace-pre-wrap">
                  {message.content}
                </p>

                {message.appointment && (
                  <div className="mt-3 p-2 bg-background/10 rounded">
                    <div className="flex items-center gap-2 text-xs">
                      <Calendar className="w-3 h-3" />
                      <span>Appuntamento</span>
                      <Badge
                        variant={
                          message.appointment.status === 'confirmed'
                            ? 'default'
                            : 'secondary'
                        }
                      >
                        {message.appointment.status === 'confirmed'
                          ? 'Confermato'
                          : 'In attesa'}
                      </Badge>
                    </div>
                    <div className="mt-1 text-xs">
                      <p><strong>{message.appointment.clientName}</strong></p>
                      <p>{message.appointment.serviceType}</p>
                      <p>{scheduleAIClientFixed.formatDateTime(
                        new Date(message.appointment.dateTime)
                      )}</p>
                    </div>
                  </div>
                )}
              </Card>

              <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span>{formatTime(message.timestamp)}</span>
              </div>
            </div>

            {message.role === 'user' && (
              <Avatar className="w-8 h-8 mt-1">
                <AvatarFallback className="bg-green-500 text-white">
                  <User className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <Avatar className="w-8 h-8 mt-1">
              <AvatarFallback className="bg-blue-500 text-white">
                <Bot className="w-4 h-4" />
              </AvatarFallback>
            </Avatar>
            <Card className="p-3 bg-muted max-w-[80%]">
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200" />
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

      {/* Input Area */}
      <div className="p-4">
        <div className="flex gap-3 items-end">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Scrivi il tuo messaggio..."
            className="min-h-[80px] max-h-[200px] resize-none"
            disabled={isLoading || connectionStatus === 'error'}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading || connectionStatus === 'error'}
            className="px-4 py-2 h-[80px]"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>

        <div className="mt-2 text-xs text-muted-foreground text-center flex items-center justify-center gap-2">
          <span>Premi Invio per inviare, Shift+Invio per andare a capo</span>
          {connectionStatus === 'error' && (
            <>
              <span>•</span>
              <button
                onClick={checkConnection}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Riprova connessione
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}