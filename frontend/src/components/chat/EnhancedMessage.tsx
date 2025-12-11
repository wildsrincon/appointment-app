'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { scheduleAIClient } from '@/utils/scheduleai-client';
import { Message } from '@/utils/types';
import { Bot, Calendar, Clock, ExternalLink, User } from 'lucide-react';
import Link from 'next/link';
import React from 'react';

interface EnhancedMessageProps {
  message: Message;
  isStreaming?: boolean;
}

// Enhanced Message Content Component with Link Detection
const MessageContent: React.FC<{ content: string }> = ({ content }) => {
  // Enhanced URL and email detection patterns
  const calendarLinkRegex = /(https?:\/\/calendar\.google\.com\/calendar[^\s<>"']*\/event[^\s<>"']*|https?:\/\/calendar\.google\.com\/calendar[^\s<>"']*|calendar\.google\.com\/calendar[^\s<>"']*)/gi;
  const meetingLinkRegex = /(https?:\/\/(meet\.google\.com|zoom\.us|teams\.microsoft\.com|webex\.com|jitsi\.org|whereby\.com|chime\.aws|gotomeeting\.com)[^\s<>"]*)/gi;
  const urlRegex = /(https?:\/\/[^\s<>"]+)/g;
  const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi;

  // Function to validate and clean URLs
  const validateAndCleanUrl = (url: string): string | null => {
    try {
      // Remove any surrounding brackets, parentheses, or invalid characters
      let cleanUrl = url.replace(/[\[\]\(\)<>]/g, '').trim();

      // Fix common protocol issues and malformed URLs
      cleanUrl = cleanUrl.replace(/https:\//g, 'https://');
      cleanUrl = cleanUrl.replace(/\/(https?:\/\/)/g, '$1'); // Fix /https:// to https://

      // Handle specific case: /Evento](https:/calendar.google.com/... -> https://calendar.google.com/...
      if (cleanUrl.includes('calendar.google.com')) {
        // Look for malformed calendar URLs like ](https:/calendar.google.com/...
        const malformedMatch = cleanUrl.match(/\]?\(?https:\/?\/?calendar\.google\.com\/([^\s\]]+)/);
        if (malformedMatch) {
          cleanUrl = `https://calendar.google.com/${malformedMatch[1]}`;
        }
        // Handle case where protocol is missing
        else if (!cleanUrl.startsWith('http')) {
          const calendarMatch = cleanUrl.match(/calendar\.google\.com\/([^\s\]]+)/);
          if (calendarMatch) {
            cleanUrl = `https://calendar.google.com/${calendarMatch[1]}`;
          }
        }
      }

      // Skip empty strings
      if (!cleanUrl) {
        return null;
      }

      // Ensure it starts with http:// or https://
      if (!cleanUrl.match(/^https?:\/\//)) {
        return null;
      }

      // Validate the URL structure
      const urlObj = new URL(cleanUrl);

      return urlObj.toString();
    } catch (error) {
      console.warn('Invalid URL detected:', url);
      return null;
    }
  };

  const renderContent = () => {
    const parts = content.split(/(\s+)/);

    return parts.map((part, index) => {
      // Skip empty parts and whitespace-only parts
      if (!part || part.trim() === '') {
        return <span key={index}>{part}</span>;
      }

      // Check if the part contains a URL pattern before cleaning (including malformed patterns)
      const hasUrlPattern = /(https?:\/\/[^\s<>"]+|calendar\.google\.com\/[^\s\]]+|\/\]?https?:\/\/[^\s\]]+)/.test(part);

      if (!hasUrlPattern) {
        return <span key={index}>{part}</span>;
      }

      // Validate and clean URLs before processing
      const cleanedUrl = validateAndCleanUrl(part);

      // Check for calendar links first (highest priority)
      if (cleanedUrl) {
        // Reset regex lastIndex to ensure proper matching
        calendarLinkRegex.lastIndex = 0;
        if (calendarLinkRegex.test(cleanedUrl)) {
          return (
            <span key={index} className="my-2 inline-block">
              <Link
                href={cleanedUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 rounded-lg text-sm font-medium transition-colors shadow-sm hover:shadow-md"
                aria-label="View calendar event"
              >
                <Calendar className="w-4 h-4" />
                Calendar Event
              </Link>
            </span>
          );
        }
      }

      // Check for meeting links
      if (cleanedUrl) {
        // Reset regex lastIndex to ensure proper matching
        meetingLinkRegex.lastIndex = 0;
        if (meetingLinkRegex.test(cleanedUrl)) {
          // Extract platform name for better button text
          let platformName = "Join Meeting";
          let buttonColor = "bg-blue-50 hover:bg-blue-100 text-blue-700";

          if (cleanedUrl.includes('meet.google.com')) {
            platformName = "Google Meet";
          } else if (cleanedUrl.includes('zoom.us')) {
            platformName = "Zoom";
            buttonColor = "bg-purple-50 hover:bg-purple-100 text-purple-700";
          } else if (cleanedUrl.includes('teams.microsoft.com')) {
            platformName = "Microsoft Teams";
            buttonColor = "bg-indigo-50 hover:bg-indigo-100 text-indigo-700";
          } else if (cleanedUrl.includes('webex.com')) {
            platformName = "Webex";
            buttonColor = "bg-green-50 hover:bg-green-100 text-green-700";
          }

          return (
            <span key={index} className="my-2 inline-block">
              <Link
                href={cleanedUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-center gap-2 px-3 py-2 ${buttonColor} rounded-lg text-sm font-medium transition-colors shadow-sm hover:shadow-md`}
                aria-label={`Join ${platformName} meeting`}
              >
                <ExternalLink className="w-4 h-4" />
                {platformName}
              </Link>
            </span>
          );
        }
      }

      // Check for URLs
      if (cleanedUrl && urlRegex.test(cleanedUrl)) {
        return (
          <Link
            key={index}
            href={cleanedUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-medium break-all hover:bg-blue-50 px-1 py-0.5 rounded transition-colors inline-block max-w-full"
            aria-label={`External link: ${cleanedUrl}`}
            title={cleanedUrl}
          >
            {cleanedUrl.length > 50 ? `${cleanedUrl.substring(0, 47)}...` : cleanedUrl}
          </Link>
        );
      }

      // Check for emails
      if (emailRegex.test(part)) {
        return (
          <Link
            key={index}
            href={`mailto:${part}`}
            className="text-blue-600 hover:text-blue-800 underline hover:bg-blue-50 px-1 py-0.5 rounded transition-colors"
            aria-label={`Email: ${part}`}
          >
            {part}
          </Link>
        );
      }

      return part;
    });
  };

  return <>{renderContent()}</>;
};

// Enhanced Timestamp Component
const MessageTimestamp: React.FC<{ timestamp: Date }> = ({ timestamp }) => {
  const [timeAgo, setTimeAgo] = React.useState('');

  React.useEffect(() => {
    const updateTimeAgo = () => {
      const now = new Date();
      const diff = now.getTime() - timestamp.getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (minutes < 1) {
        setTimeAgo('adesso');
      } else if (minutes < 60) {
        setTimeAgo(`${minutes} min fa`);
      } else if (hours < 24) {
        setTimeAgo(`${hours} ore fa`);
      } else if (days < 7) {
        setTimeAgo(`${days} giorni fa`);
      } else {
        setTimeAgo(scheduleAIClient.formatDate(timestamp));
      }
    };

    updateTimeAgo();
    const interval = setInterval(updateTimeAgo, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [timestamp]);

  return (
    <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground px-1">
      <Clock className="w-3 h-3" />
      <span>{timeAgo}</span>
      <span className="text-xs text-muted-foreground">
        {scheduleAIClient.formatTime(timestamp)}
      </span>
    </div>
  );
};

// Appointment Card Component
const AppointmentCard: React.FC<{ appointment: NonNullable<Message['appointment']> }> = ({ appointment }) => {
  return (
    <div className="mt-3 p-3 bg-white/10 dark:bg-black/10 rounded-lg border border-white/20 backdrop-blur-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-blue-500" />
          <span className="font-semibold text-sm">Appuntamento</span>
        </div>
        <Badge
          variant={appointment.status === 'confirmed' ? 'default' : 'secondary'}
          className="text-xs"
        >
          {appointment.status === 'confirmed' ? 'Confermato' : 'In attesa'}
        </Badge>
      </div>

      <div className="space-y-2 text-sm">
        <p className="font-medium">{appointment.clientName}</p>
        <p className="text-muted-foreground">{appointment.serviceType}</p>
        <div className="flex items-center gap-1 text-muted-foreground">
          <Clock className="w-3 h-3" />
          {scheduleAIClient.formatDateTime(new Date(appointment.dateTime))}
        </div>
        {appointment.duration && (
          <div className="flex items-center gap-1 text-muted-foreground">
            <Clock className="w-3 h-3" />
            Durata: {appointment.duration} minuti
          </div>
        )}
        {appointment.notes && (
          <p className="text-xs text-muted-foreground italic mt-2">
            Note: {appointment.notes}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-3 flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={() => {
            try {
              // Add to calendar functionality
              const event = {
                title: `${appointment.serviceType} - ${appointment.clientName}`,
                start: new Date(appointment.dateTime),
                duration: appointment.duration,
                description: appointment.notes
              };

              // Create calendar URL (Google Calendar example)
              const calendarUrl = new URL('https://calendar.google.com/calendar/render');
              calendarUrl.searchParams.set('action', 'TEMPLATE');
              calendarUrl.searchParams.set('text', encodeURIComponent(event.title));

              // Format dates for Google Calendar (YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ)
              const startTime = event.start.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
              const endTime = new Date(event.start.getTime() + (event.duration || 60) * 60000)
                .toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

              calendarUrl.searchParams.set('dates', `${startTime}/${endTime}`);
              calendarUrl.searchParams.set('details', encodeURIComponent(event.description || ''));

              window.open(calendarUrl.toString(), '_blank');
            } catch (error) {
              console.error('Failed to create calendar event:', error);
              alert('Impossibile creare l\'evento calendario. Riprova più tardi.');
            }
          }}
        >
          <Calendar className="w-4 h-4 mr-2" />
          Aggiungi al calendario
        </Button>
      </div>
    </div>
  );
};

// Loading Indicator Component
const LoadingIndicator: React.FC = () => (
  <div className="flex items-center gap-2 py-2">
    <div className="flex gap-1">
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
    <span className="text-sm text-muted-foreground">Sto scrivendo...</span>
  </div>
);

// Streaming Indicator Component
const StreamingIndicator: React.FC = () => (
  <div className="flex items-center gap-2">
    <div className="w-2 h-4 bg-blue-500 animate-pulse" />
  </div>
);

export const EnhancedMessage: React.FC<EnhancedMessageProps> = ({
  message,
  isStreaming = false
}) => {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    // Trigger animation when component mounts
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className={`flex gap-3 mb-4 transition-all duration-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
        } ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={`Messaggio da ${message.role === 'user' ? 'utente' : 'assistente'}`}
    >
      {message.role === 'assistant' && (
        <Avatar className="w-10 h-10 flex-shrink-0 mt-1">
          <AvatarFallback className="bg-blue-500 text-white shadow-lg">
            <Bot className="w-5 h-5" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className={`max-w-[70%] lg:max-w-[60%] flex flex-col ${message.role === 'user' ? 'order-1' : 'order-2'
        }`}>
        <Card
          className={`p-4 shadow-sm border-0 transition-all hover:shadow-md ${message.role === 'user'
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
            : 'bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
            }`}
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            <MessageContent content={message.content} />
          </div>

          {/* Appointment Information */}
          {message.appointment && (
            <AppointmentCard appointment={message.appointment} />
          )}

          {/* Streaming Indicator */}
          {isStreaming && (
            <div className="flex items-center justify-end mt-2">
              <StreamingIndicator />
            </div>
          )}
        </Card>

        {/* Timestamp */}
        <MessageTimestamp timestamp={message.timestamp} />
      </div>

      {message.role === 'user' && (
        <Avatar className="w-10 h-10 flex-shrink-0 mt-1">
          <AvatarFallback className="bg-green-500 text-white shadow-lg">
            <User className="w-5 h-5" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
};

export default EnhancedMessage;