'use client';

import React, { createContext, useContext, useCallback } from 'react';
import { toast, Toaster } from 'sonner';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastOptions {
  duration?: number;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, options?: ToastOptions) => void;
  showSuccess: (message: string, options?: ToastOptions) => void;
  showError: (message: string, options?: ToastOptions) => void;
  showInfo: (message: string, options?: ToastOptions) => void;
  showWarning: (message: string, options?: ToastOptions) => void;
  dismissToast: (id?: string | number) => void;
  clearAllToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
  defaultOptions?: ToastOptions;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  defaultOptions = {}
}) => {
  const showToast = useCallback((
    message: string,
    type: ToastType = 'info',
    options: ToastOptions = {}
  ) => {
    const mergedOptions = { ...defaultOptions, ...options };

    switch (type) {
      case 'success':
        toast.success(message, mergedOptions);
        break;
      case 'error':
        toast.error(message, mergedOptions);
        break;
      case 'warning':
        toast.warning(message, mergedOptions);
        break;
      case 'info':
      default:
        toast.info(message, mergedOptions);
        break;
    }
  }, [defaultOptions]);

  const showSuccess = useCallback((message: string, options?: ToastOptions) => {
    showToast(message, 'success', options);
  }, [showToast]);

  const showError = useCallback((message: string, options?: ToastOptions) => {
    showToast(message, 'error', options);
  }, [showToast]);

  const showInfo = useCallback((message: string, options?: ToastOptions) => {
    showToast(message, 'info', options);
  }, [showToast]);

  const showWarning = useCallback((message: string, options?: ToastOptions) => {
    showToast(message, 'warning', options);
  }, [showToast]);

  const dismissToast = useCallback((id?: string | number) => {
    if (id) {
      toast.dismiss(id);
    } else {
      toast.dismiss();
    }
  }, []);

  const clearAllToasts = useCallback(() => {
    toast.dismiss();
  }, []);

  const value: ToastContextType = {
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    dismissToast,
    clearAllToasts,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Toaster
        position={defaultOptions.position || 'bottom-right'}
        richColors
        closeButton
        duration={defaultOptions.duration || 4000}
        expand={false}
        theme="system"
      />
    </ToastContext.Provider>
  );
};

// Pre-defined toast messages for common actions
export const appointmentToasts = {
  created: (appointmentDetails: string) => `Appuntamento creato con successo! ${appointmentDetails}`,
  updated: (appointmentDetails: string) => `Appuntamento aggiornato! ${appointmentDetails}`,
  cancelled: () => `Appuntamento cancellato con successo`,
  error: (error: string) => `Errore durante la gestione dell'appuntamento: ${error}`,
  noAvailability: () => `Nessuna disponibilità trovata per l'orario richiesto`,
  conflict: () => `Esiste già un appuntamento per questo orario`,
};

export const chatToasts = {
  messageSent: () => `Messaggio inviato con successo`,
  messageError: () => `Errore durante l'invio del messaggio`,
  sessionSaved: () => `Conversazione salvata`,
  sessionDeleted: () => `Conversazione eliminata`,
  copySuccess: () => `Testo copiato negli appunti`,
  copyError: () => `Errore durante la copia del testo`,
};

export const connectionToasts = {
  connected: () => `Connesso con successo`,
  disconnected: () => `Connessione persa`,
  reconnecting: () => `Riconnessione in corso...`,
  error: (error: string) => `Errore di connessione: ${error}`,
};