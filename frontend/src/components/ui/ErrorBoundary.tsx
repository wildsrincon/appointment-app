'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { AlertCircle, Home, Mail, RefreshCw } from 'lucide-react';
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | undefined;
  retryCount: number;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  maxRetries?: number;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: undefined,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report to analytics or error tracking service
    this.reportError(error, errorInfo);
  }

  private reportError = (error: Error, errorInfo: React.ErrorInfo) => {
    // In production, you might want to send this to a service like Sentry
    try {
      // Example: Send to analytics
      if (typeof window !== 'undefined' && 'gtag' in window) {
        // Define a proper interface for the gtag function
        interface GTag {
          (command: 'event', eventName: 'exception', params: {
            description: string;
            fatal: boolean;
          }): void;
        }

        const gtag = (window as unknown as { gtag: GTag }).gtag;
        gtag('event', 'exception', {
          description: error.message,
          fatal: false,
        });
      }
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  };

  private handleRetry = () => {
    const { maxRetries = 3 } = this.props;
    const { retryCount } = this.state;

    if (retryCount < maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: undefined,
        retryCount: prevState.retryCount + 1,
      }));
    }
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleContactSupport = () => {
    const subject = encodeURIComponent('Problema con ScheduleAI');
    const body = encodeURIComponent(
      `Ciao, sto riscontrando un problema con l'applicazione ScheduleAI.\n\n` +
      `Errore: ${this.state.error?.message}\n` +
      `URL: ${window.location.href}\n` +
      `User Agent: ${navigator.userAgent}\n` +
      `Timestamp: ${new Date().toISOString()}`
    );
    window.location.href = `mailto:support@scheduleai.com?subject=${subject}&body=${body}`;
  };

  render() {
    const { hasError, error, retryCount } = this.state;
    const { children, fallback: Fallback, maxRetries = 3 } = this.props;

    if (!hasError || !error) {
      return children;
    }

    if (Fallback) {
      return <Fallback error={error} retry={this.handleRetry} />;
    }

    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-background">
        <Card className="max-w-md w-full p-6 shadow-lg border-destructive/20">
          {/* Error Icon */}
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
          </div>

          {/* Error Title */}
          <h2 className="text-xl font-semibold text-center mb-2">
            Qualcosa è andato storto
          </h2>

          {/* Error Description */}
          <p className="text-muted-foreground text-center mb-4">
            Si è verificato un errore imprevisto. Il nostro team è stato informato e sta lavorando per risolvere il problema.
          </p>

          {/* Retry Count */}
          {retryCount > 0 && (
            <div className="text-center mb-4">
              <p className="text-sm text-muted-foreground">
                Tentativo {retryCount} di {maxRetries}
              </p>
            </div>
          )}

          {/* Error Details (Development) */}
          {process.env.NODE_ENV === 'development' && (
            <details className="mb-4 p-3 bg-muted rounded-lg">
              <summary className="cursor-pointer text-sm font-medium mb-2">
                Dettagli errore (sviluppo)
              </summary>
              <pre className="text-xs overflow-auto max-h-40">
                {error.stack || 'No stack trace available'}
              </pre>
            </details>
          )}

          {/* Action Buttons */}
          <div className="space-y-2">
            {/* Retry Button */}
            {retryCount < maxRetries && (
              <Button
                onClick={this.handleRetry}
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Riprova ({maxRetries - retryCount} tentativi rimanenti)
              </Button>
            )}

            {/* Reload Page Button */}
            <Button
              variant="outline"
              onClick={this.handleReload}
              className="w-full"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Ricarica la pagina
            </Button>

            {/* Go Home Button */}
            <Button
              variant="outline"
              onClick={this.handleGoHome}
              className="w-full"
            >
              <Home className="w-4 h-4 mr-2" />
              Torna alla home
            </Button>

            {/* Contact Support Button */}
            <Button
              variant="ghost"
              onClick={this.handleContactSupport}
              className="w-full"
            >
              <Mail className="w-4 h-4 mr-2" />
              Contatta il supporto
            </Button>
          </div>

          {/* Footer */}
          <div className="mt-6 pt-4 border-t text-center">
            <p className="text-xs text-muted-foreground">
              ID errore: {Date.now().toString(36)}
            </p>
          </div>
        </Card>
      </div>
    );
  }
}

// Hook for functional components to catch errors
export const useErrorBoundary = () => {
  const [error, setError] = React.useState<Error | undefined>(undefined);

  const resetError = React.useCallback(() => {
    setError(undefined);
  }, []);

  const captureError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { captureError, resetError };
};

// Specific error boundary for chat components
export const ChatErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary
      maxRetries={2}
      fallback={({ error, retry }) => (
        <Card className="m-4 p-6 border-red-200 bg-red-50 dark:bg-red-900/10">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
                Errore nella chat
              </h3>
              <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                La chat ha riscontrato un problema. Puoi provare a ricaricare la conversazione o iniziare una nuova chat.
              </p>

              <div className="flex gap-2">
                <Button
                  onClick={retry}
                  variant="outline"
                  size="sm"
                  className="border-red-200 text-red-700 hover:bg-red-100"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Riprova
                </Button>
                <Button
                  onClick={() => window.location.reload()}
                  size="sm"
                >
                  Ricarica pagina
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
    >
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundary;