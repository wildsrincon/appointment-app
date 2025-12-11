'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatSession } from '@/utils/types';
import { cn } from '@/utils/utils';
import { formatDistanceToNow } from 'date-fns';
import { it } from 'date-fns/locale';
import {
  Archive,
  Calendar,
  Clock,
  Menu,
  MoreHorizontal,
  Plus,
  Search,
  Settings,
  Trash2,
  X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface MobileOptimizedSidebarProps {
  sessions: ChatSession[];
  currentSessionId: string;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
  onSettings: () => void;
  userName?: string;
  className?: string;
}

export const MobileOptimizedSidebar: React.FC<MobileOptimizedSidebarProps> = ({
  sessions,
  currentSessionId,
  onSessionSelect,
  onNewChat,
  onSettings,
  userName = "Utente",
  className
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSessions, setFilteredSessions] = useState(sessions);

  // Handle mobile responsiveness
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768;
      if (!isMobile) {
        setIsOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Filter sessions based on search query
  useEffect(() => {
    const filtered = sessions.filter(session =>
      session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.messages.some(msg =>
        msg.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
    setFilteredSessions(filtered);
  }, [sessions, searchQuery]);

  const handleSessionClick = (sessionId: string) => {
    onSessionSelect(sessionId);
    setIsOpen(false);
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return formatDistanceToNow(date, { addSuffix: true, locale: it });
    } else {
      return date.toLocaleDateString('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  // Mobile menu button
  const MobileMenuButton = () => (
    <Button
      variant="ghost"
      size="icon"
      className="md:hidden fixed top-4 left-4 z-50 h-10 w-10"
      onClick={() => setIsOpen(true)}
      aria-label="Apri menu"
    >
      <Menu className="w-5 h-5" />
    </Button>
  );

  // Mobile overlay
  const MobileOverlay = () => (
    <div
      className={cn(
        "fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity duration-300",
        isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
      )}
      onClick={() => setIsOpen(false)}
    />
  );

  // Sidebar content
  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-background border-r">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-blue-500 text-white">
                {userName.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="font-semibold">{userName}</h2>
              <p className="text-xs text-muted-foreground">Assistente AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={onSettings}
              className="h-8 w-8"
              aria-label="Impostazioni"
            >
              <Settings className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="md:hidden h-8 w-8"
              aria-label="Chiudi menu"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* New Chat Button */}
        <Button
          onClick={() => {
            onNewChat();
            setIsOpen(false);
          }}
          className="w-full justify-start gap-2"
          size="sm"
        >
          <Plus className="w-4 h-4" />
          Nuova Conversazione
        </Button>
      </div>

      {/* Search */}
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Cerca conversazioni..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Sessions List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {searchQuery ? 'Nessuna conversazione trovata' : 'Nessuna conversazione'}
            </div>
          ) : (
            filteredSessions.map((session) => {
              const lastMessage = session.messages[session.messages.length - 1];
              const isActive = session.id === currentSessionId;

              return (
                <Card
                  key={session.id}
                  className={cn(
                    "cursor-pointer transition-all hover:bg-accent/50 border-0 p-3",
                    isActive && "bg-accent border-l-4 border-l-blue-500"
                  )}
                  onClick={() => handleSessionClick(session.id)}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h3 className="font-medium text-sm truncate flex-1">
                      {session.title}
                    </h3>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatDate(session.updatedAt)}
                    </span>
                  </div>

                  {lastMessage && (
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                      {lastMessage.content}
                    </p>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      {session.messages.some(msg => msg.appointment) && (
                        <Badge variant="secondary" className="text-xs">
                          <Calendar className="w-3 h-3 mr-1" />
                          Appuntamento
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <span>{session.messages.length}</span>
                      <span>messaggi</span>
                    </div>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t">
        <div className="grid grid-cols-2 gap-2 text-xs">
          <Button
            variant="ghost"
            size="sm"
            className="justify-start gap-1 h-8"
          >
            <Archive className="w-3 h-3" />
            Archivia
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="justify-start gap-1 h-8 text-destructive hover:text-destructive"
          >
            <Trash2 className="w-3 h-3" />
            Elimina
          </Button>
        </div>

        <div className="mt-3 pt-3 border-t text-center">
          <p className="text-xs text-muted-foreground">
            ScheduleAI v1.0.0
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <MobileMenuButton />
      <MobileOverlay />

      <div
        className={cn(
          "fixed top-0 left-0 h-full w-80 z-50 transform transition-transform duration-300 md:relative md:transform-none",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          className
        )}
      >
        <SidebarContent />
      </div>
    </>
  );
};

// Quick Actions Component for Mobile
export const MobileQuickActions: React.FC<{
  onNewChat: () => void;
  onScheduleAppointment: () => void;
  onCheckAvailability: () => void;
  onHelp: () => void;
}> = ({ onNewChat, onScheduleAppointment, onCheckAvailability, onHelp }) => {
  return (
    <div className="md:hidden fixed bottom-20 left-0 right-0 bg-background/95 backdrop-blur border-t p-2 z-30">
      <div className="grid grid-cols-4 gap-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={onNewChat}
          className="flex-col h-auto py-2 px-1"
        >
          <Plus className="w-4 h-4 mb-1" />
          <span className="text-xs">Nuovo</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onScheduleAppointment}
          className="flex-col h-auto py-2 px-1"
        >
          <Calendar className="w-4 h-4 mb-1" />
          <span className="text-xs">Prenota</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCheckAvailability}
          className="flex-col h-auto py-2 px-1"
        >
          <Clock className="w-4 h-4 mb-1" />
          <span className="text-xs">Orari</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onHelp}
          className="flex-col h-auto py-2 px-1"
        >
          <MoreHorizontal className="w-4 h-4 mb-1" />
          <span className="text-xs">Altro</span>
        </Button>
      </div>
    </div>
  );
};

export default MobileOptimizedSidebar;