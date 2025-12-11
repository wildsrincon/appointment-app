'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { scheduleAIClient } from '@/utils/scheduleai-client';
import { AppointmentData } from '@/utils/types';
import { AlertCircle, Calendar, CheckCircle, ExternalLink, Info, X } from 'lucide-react';
import React from 'react';

// Success Notification Component
interface SuccessNotificationProps {
  message: string;
  appointment?: AppointmentData;
  onDismiss?: () => void;
  showCalendarButton?: boolean;
}

export const SuccessNotification: React.FC<SuccessNotificationProps> = ({
  message,
  appointment,
  onDismiss,
  showCalendarButton = true
}) => {
  const handleAddToCalendar = () => {
    if (!appointment) return;

    try {
      const event = {
        title: `${appointment.serviceType} - ${appointment.clientName}`,
        start: new Date(appointment.dateTime),
        duration: appointment.duration || 60,
        description: appointment.notes || `Appuntamento per ${appointment.serviceType}`
      };

      // Create Google Calendar URL
      const calendarUrl = new URL('https://calendar.google.com/calendar/render');
      calendarUrl.searchParams.set('action', 'TEMPLATE');
      calendarUrl.searchParams.set('text', event.title);

      const startTime = event.start.toISOString().replace(/[-:]/g, '').split('.')[0];
      const endTime = new Date(event.start.getTime() + event.duration * 60000)
        .toISOString().replace(/[-:]/g, '').split('.')[0];

      calendarUrl.searchParams.set('dates', `${startTime}/${endTime}`);
      calendarUrl.searchParams.set('details', event.description);

      window.open(calendarUrl.toString(), '_blank');
    } catch (error) {
      console.error('Failed to create calendar event:', error);
    }
  };

  return (
    <Card className="m-4 p-4 border-green-200 bg-green-50 dark:bg-green-900/10 animate-slideUp notification notification-success">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <CheckCircle className="w-5 h-5 text-green-500" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-green-800 dark:text-green-200 mb-2">
            Operazione completata!
          </h4>

          <p className="text-sm text-green-700 dark:text-green-300 mb-3">
            {message}
          </p>

          {/* Appointment Details */}
          {appointment && (
            <div className="p-3 bg-white/50 dark:bg-black/20 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-green-600" />
                  <span className="font-medium text-sm">Dettagli appuntamento</span>
                </div>
                <Badge variant="default" className="bg-green-500 text-white">
                  {appointment.status === 'confirmed' ? 'Confermato' : appointment.status}
                </Badge>
              </div>

              <div className="space-y-1 text-sm text-green-800 dark:text-green-200">
                <p><strong>Cliente:</strong> {appointment.clientName}</p>
                <p><strong>Servizio:</strong> {appointment.serviceType}</p>
                <p><strong>Data e ora:</strong> {scheduleAIClient.formatDateTime(new Date(appointment.dateTime))}</p>
                {appointment.duration && (
                  <p><strong>Durata:</strong> {appointment.duration} minuti</p>
                )}
                {appointment.meetingLink && (
                  <div className="mt-2 pt-2 border-t border-green-200 dark:border-green-800">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(appointment.meetingLink, '_blank')}
                      className="text-green-700 border-green-300 hover:bg-green-100"
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Apri link meeting
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-4 flex gap-2">
            {appointment && showCalendarButton && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleAddToCalendar}
                className="text-green-700 border-green-300 hover:bg-green-100"
              >
                <Calendar className="w-4 h-4 mr-2" />
                Aggiungi al calendario
              </Button>
            )}

            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="text-green-700 hover:bg-green-100"
              >
                Chiudi
              </Button>
            )}
          </div>
        </div>

        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-6 w-6 p-0 text-green-600 hover:bg-green-100"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>
    </Card>
  );
};

// Error Message Component
interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  showRetryButton?: boolean;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  onRetry,
  onDismiss,
  showRetryButton = true
}) => {
  return (
    <Card className="m-4 p-4 border-red-200 bg-red-50 dark:bg-red-900/10 animate-slideUp notification notification-error">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <AlertCircle className="w-5 h-5 text-red-500" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-red-800 dark:text-red-200 mb-2">
            Si è verificato un errore
          </h4>

          <p className="text-sm text-red-700 dark:text-red-300 mb-3">
            {error}
          </p>

          {/* Action Buttons */}
          <div className="flex gap-2">
            {showRetryButton && onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="border-red-200 text-red-700 hover:bg-red-100"
              >
                Riprova
              </Button>
            )}

            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="text-red-700 hover:bg-red-100"
              >
                Chiudi
              </Button>
            )}
          </div>
        </div>

        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-6 w-6 p-0 text-red-600 hover:bg-red-100"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>
    </Card>
  );
};

// Info Message Component
interface InfoMessageProps {
  message: string;
  title?: string;
  onDismiss?: () => void;
  type?: 'info' | 'warning';
}

export const InfoMessage: React.FC<InfoMessageProps> = ({
  message,
  title,
  onDismiss,
  type = 'info'
}) => {
  const colors = type === 'warning'
    ? {
      bg: 'bg-yellow-50 dark:bg-yellow-900/10',
      border: 'border-yellow-200 dark:border-yellow-800',
      text: 'text-yellow-800 dark:text-yellow-200',
      subText: 'text-yellow-700 dark:text-yellow-300',
      icon: 'text-yellow-500'
    }
    : {
      bg: 'bg-blue-50 dark:bg-blue-900/10',
      border: 'border-blue-200 dark:border-blue-800',
      text: 'text-blue-800 dark:text-blue-200',
      subText: 'text-blue-700 dark:text-blue-300',
      icon: 'text-blue-500'
    };

  return (
    <Card className={`m-4 p-4 border ${colors.border} ${colors.bg} animate-slideUp notification ${type === 'warning' ? 'notification-warning' : 'notification-info'
      }`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <Info className={`w-5 h-5 ${colors.icon}`} />
        </div>

        <div className="flex-1 min-w-0">
          {title && (
            <h4 className={`text-sm font-semibold ${colors.text} mb-2`}>
              {title}
            </h4>
          )}

          <p className={`text-sm ${colors.subText}`}>
            {message}
          </p>

          {/* Dismiss Button */}
          {onDismiss && (
            <div className="mt-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className={`${colors.subText} hover:opacity-80`}
              >
                Chiudi
              </Button>
            </div>
          )}
        </div>

        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className={`h-6 w-6 p-0 ${colors.icon} hover:opacity-80`}
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>
    </Card>
  );
};

// Toast Notification Component (for floating notifications)
interface ToastNotificationProps {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onClose?: () => void;
}

export const ToastNotification: React.FC<ToastNotificationProps> = ({
  message,
  type,
  duration = 5000,
  onClose
}) => {
  const [isVisible, setIsVisible] = React.useState(true);

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onClose?.(), 300);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose?.(), 300);
  };

  const icons = {
    success: <CheckCircle className="w-4 h-4" />,
    error: <AlertCircle className="w-4 h-4" />,
    info: <Info className="w-4 h-4" />,
    warning: <AlertCircle className="w-4 h-4" />
  };

  const colors = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    info: 'bg-blue-500 text-white',
    warning: 'bg-yellow-500 text-white'
  };

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm w-full transform transition-all duration-300 ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
        }`}
    >
      <div className={`${colors[type]} rounded-lg shadow-lg p-4 flex items-center gap-3`}>
        <div className="flex-shrink-0">
          {icons[type]}
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">{message}</p>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleClose}
          className="h-6 w-6 p-0 text-white/80 hover:text-white hover:bg-white/20"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

export default {
  SuccessNotification,
  ErrorMessage,
  InfoMessage,
  ToastNotification
};