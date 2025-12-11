'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { ChatSession } from '@/utils/types';
import {
  Calendar,
  Clock,
  LogOut,
  Menu,
  MessageSquarePlus,
  Settings,
  Sparkles,
  Trash2,
  User
} from 'lucide-react';
import React, { useState } from 'react';

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  onSettings: () => void;
  userName?: string;
  userAvatar?: string;
  className?: string;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onSessionSelect,
  onNewChat,
  onDeleteSession,
  onSettings,
  userName = 'Utente',
  userAvatar,
  className
}: SidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Oggi';
    } else if (days === 1) {
      return 'Ieri';
    } else if (days < 7) {
      return `${days} giorni fa`;
    } else {
      return new Intl.DateTimeFormat('it-IT', {
        day: '2-digit',
        month: '2-digit'
      }).format(date);
    }
  };

  const truncateTitle = (title: string, maxLength: number = 30) => {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength) + '...';
  };

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation(); // Prevent session selection when clicking delete
    if (window.confirm('Sei sicuro di voler eliminare questa conversazione?')) {
      onDeleteSession(sessionId);
    }
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Avatar className="w-8 h-8">
              <AvatarImage src={userAvatar} alt={userName} />
              <AvatarFallback className="bg-green-500 text-white">
                <User className="w-4 h-4" />
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-medium text-sm">{userName}</h3>
              <p className="text-xs text-muted-foreground">Online</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <ThemeToggle variant="compact" />
            <Button
              variant="ghost"
              size="sm"
              onClick={onSettings}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <Button
          onClick={onNewChat}
          className="w-full justify-start bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white border-0 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 group relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
          <div className="relative flex items-center">
            <MessageSquarePlus className="w-4 h-4 mr-2 group-hover:rotate-12 transition-transform duration-200" />
            <span className="font-medium">Nuova Conversazione</span>
            <Sparkles className="w-4 h-4 ml-2 opacity-70 group-hover:opacity-100 group-hover:scale-110 transition-all duration-200" />
          </div>
        </Button>
      </div>

      {/* Sessions List */}
      <ScrollArea className="flex-1 p-2">
        <div className="space-y-1">
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <MessageSquarePlus className="w-12 h-12 mx-auto mb-2 opacity-50 dark:opacity-40" />
              <p className="text-sm font-medium">Nessuna conversazione</p>
              <p className="text-xs dark:text-gray-400">Inizia una nuova chat</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div key={session.id} className="relative group">
                <Button
                  variant={currentSessionId === session.id ? "secondary" : "ghost"}
                  className={`w-full justify-start h-auto p-3 text-left pr-12 transition-all duration-200 hover:scale-[1.02] hover:shadow-sm ${currentSessionId === session.id
                      ? 'bg-secondary hover:bg-secondary/80'
                      : 'hover:bg-accent/50 dark:hover:bg-gray-800'
                    }`}
                  onClick={() => {
                    onSessionSelect(session.id);
                    setIsMobileOpen(false);
                  }}
                >
                  <div className="w-full">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm truncate group-hover:text-primary transition-colors">
                        {truncateTitle(session.title)}
                      </span>
                      {session.messages.some(m => m.appointment) && (
                        <Badge variant="secondary" className="ml-2 px-1 py-0 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                          <Calendar className="w-3 h-3" />
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground dark:text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(session.updatedAt)}</span>
                      <span className="opacity-60">•</span>
                      <span>{session.messages.length} messaggi</span>
                    </div>
                  </div>
                </Button>

                {/* Delete button - only visible on hover */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 p-1 h-8 w-8 hover:bg-red-50 dark:hover:bg-red-900/20 hover:scale-110"
                  onClick={(e) => handleDeleteSession(e, session.id)}
                  title="Elimina conversazione"
                >
                  <Trash2 className="w-4 h-4 text-destructive hover:text-red-600 dark:hover:text-red-400" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t dark:border-gray-800">
        <div className="flex items-center justify-between text-xs text-muted-foreground dark:text-gray-400 mb-3">
          <span className="font-medium">ScheduleAI Assistant</span>
          <Badge variant="outline" className="text-xs dark:border-gray-700 dark:text-gray-300">
            v1.0
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle variant="icon-only" className="flex-1" />
          <Button
            variant="ghost"
            size="sm"
            className="flex-1 justify-start text-xs hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <LogOut className="w-3 h-3 mr-2" />
            Esci
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <div className={`hidden md:flex md:flex-col ${className}`}>
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={isMobileOpen} onOpenChange={setIsMobileOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden fixed top-4 left-4 z-50"
          >
            <Menu className="w-4 h-4" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </>
  );
}