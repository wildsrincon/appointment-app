'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';
import { Sidebar } from '@/components/layout/Sidebar';
import { ToastProvider } from '@/contexts/ToastContext';
import { generateSessionTitle } from '@/utils/generateSessionTitleDemo';
import { AppointmentData, ChatSession, Message } from '@/utils/types';
import { useEffect, useState } from 'react';

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('default');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load sessions from localStorage on mount
  useEffect(() => {
    const loadSessions = () => {
      const savedSessions = localStorage.getItem('scheduleai-sessions');
      if (savedSessions) {
        try {
          const parsedData = JSON.parse(savedSessions);
          if (Array.isArray(parsedData)) {
            const parsedSessions: ChatSession[] = parsedData.map((session: {
              id: string;
              title: string;
              messages: {
                id: string;
                content: string;
                role: 'user' | 'assistant' | 'system';
                timestamp: string;
                appointment?: AppointmentData;
              }[];
              createdAt: string;
              updatedAt: string;
            }) => ({
              ...session,
              createdAt: new Date(session.createdAt),
              updatedAt: new Date(session.updatedAt),
              messages: session.messages.map((msg) => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
              }))
            }));
            setSessions(parsedSessions);
          }
        } catch (error) {
          console.error('Error loading sessions:', error);
        }
      }
    };

    loadSessions();
  }, []);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('scheduleai-sessions', JSON.stringify(sessions));
  }, [sessions]);

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: 'Nuova Conversazione',
      messages: [
        {
          id: '1',
          content: 'Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?',
          role: 'assistant',
          timestamp: new Date()
        }
      ],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
  };

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleMessageAdd = (sessionId: string, messages: Message[]) => {
    setSessions(prev => prev.map(session => {
      if (session.id === sessionId) {
        return {
          ...session,
          messages,
          title: generateSessionTitle(messages),
          updatedAt: new Date()
        };
      }
      return session;
    }));
  };

  const handleDeleteSession = (sessionId: string) => {
    setSessions(prev => {
      const updatedSessions = prev.filter(session => session.id !== sessionId);

      // If deleting current session, switch to another session or create new one
      if (sessionId === currentSessionId) {
        if (updatedSessions.length > 0) {
          setCurrentSessionId(updatedSessions[0].id);
        } else {
          // Create new default session if no sessions left
          const newSession: ChatSession = {
            id: Date.now().toString(),
            title: 'Nuova Conversazione',
            messages: [
              {
                id: '1',
                content: 'Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?',
                role: 'assistant',
                timestamp: new Date()
              }
            ],
            createdAt: new Date(),
            updatedAt: new Date()
          };
          updatedSessions.push(newSession);
          setCurrentSessionId(newSession.id);
        }
      }

      return updatedSessions;
    });
  };

  const handleSettings = () => {
    // TODO: Implement settings modal/page
    console.log('Settings clicked');
  };

  const currentSession = sessions.find(s => s.id === currentSessionId);

  return (
    <ToastProvider
      defaultOptions={{
        position: 'bottom-right',
        duration: 4000,
        dismissible: true,
      }}
    >
      <div className="flex h-screen bg-background">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 border-r hidden md:block`}>
          {sidebarOpen && (
            <Sidebar
              sessions={sessions}
              currentSessionId={currentSessionId}
              onSessionSelect={handleSessionSelect}
              onNewChat={handleNewChat}
              onDeleteSession={handleDeleteSession}
              onSettings={handleSettings}
              userName="Cliente"
            />
          )}
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="border-b p-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold">ScheduleAI</h1>
                <p className="text-sm text-muted-foreground">
                  {currentSession?.title || 'Assistente per prenotazioni'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="md:hidden p-2 hover:bg-muted rounded-lg"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <ChatInterface
            sessionId={currentSessionId}
            initialMessages={currentSession?.messages}
            onMessagesUpdate={handleMessageAdd}
            onAppointmentCreated={(appointment) => {
              console.log('Appointment created:', appointment);
            }}
          />
        </div>
      </div>
    </ToastProvider>
  );
}
