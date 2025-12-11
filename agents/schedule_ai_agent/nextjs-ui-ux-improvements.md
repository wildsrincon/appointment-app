# Next.js Appointment Scheduling App - UI/UX Analysis & Improvements

## 📊 Current State Analysis

### Technology Stack
- **Next.js**: 16.0.3 (appears to be using cutting-edge features)
- **React**: 19.2.0 (latest version with modern hooks)
- **UI Library**: Radix UI components with Tailwind CSS v4
- **Styling**: Tailwind CSS v4 with custom CSS variables
- **State Management**: React useState/useEffect (no global state management)

### Current Architecture
- **App Router**: Modern Next.js 13+ App Router pattern
- **Component Structure**: Well-organized with UI components library
- **TypeScript**: Fully typed with comprehensive interfaces
- **Responsive Design**: Basic mobile responsiveness with breakpoints

## 🔍 Key Issues Identified

### 1. Chat Interface Problems
- **Link Rendering**: Links escape containers and aren't properly clickable
- **Message Layout**: Basic styling without visual hierarchy
- **Loading States**: Basic bouncing dots, could be more engaging
- **User Feedback**: Limited error states and success indicators

### 2. Appointment Display Issues
- **Meeting Links**: No proper link styling or click handling
- **Appointment Cards**: Basic styling without clear action buttons
- **Status Indicators**: Simple badges without clear visual hierarchy

### 3. Responsive Design Gaps
- **Mobile Experience**: Sidebar has issues on small screens
- **Touch Targets**: Button sizes could be improved for mobile
- **Layout Breaks**: Some components don't adapt well to different screen sizes

### 4. User Experience Flow
- **Onboarding**: No clear user guidance
- **Error Handling**: Basic error messages without recovery options
- **Success States**: Limited confirmation feedback
- **Accessibility**: Missing ARIA labels and keyboard navigation

## 🎨 Comprehensive UI/UX Improvements

### 1. Enhanced Chat Interface

#### Message Link Rendering Fix
```tsx
// Enhanced Message Component with Link Detection
import React from 'react';
import Link from 'next/link';

const MessageContent: React.FC<{ content: string }> = ({ content }) => {
  // Enhanced link detection pattern
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi;

  const renderContent = () => {
    const parts = content.split(/(\s+)/);

    return parts.map((part, index) => {
      // Check for URLs
      if (urlRegex.test(part)) {
        return (
          <Link
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-medium break-all"
          >
            {part}
          </Link>
        );
      }

      // Check for emails
      if (emailRegex.test(part)) {
        return (
          <Link
            key={index}
            href={`mailto:${part}`}
            className="text-blue-600 hover:text-blue-800 underline"
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
```

#### Enhanced Message Styling
```tsx
// Improved Message Component
const EnhancedMessage: React.FC<MessageProps> = ({ message }) => {
  return (
    <div className={`flex gap-3 mb-4 animate-fadeIn ${
      message.role === 'user' ? 'justify-end' : 'justify-start'
    }`}>
      {/* Avatar */}
      <Avatar className="w-10 h-10 flex-shrink-0">
        <AvatarFallback className={
          message.role === 'user'
            ? 'bg-green-500 text-white'
            : 'bg-blue-500 text-white'
        }>
          {message.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </AvatarFallback>
      </Avatar>

      {/* Message Bubble */}
      <div className={`max-w-[70%] lg:max-w-[60%]`}>
        <Card className={`p-4 shadow-sm border-0 ${
          message.role === 'user'
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
            : 'bg-gray-50 dark:bg-gray-800'
        }`}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            <MessageContent content={message.content} />
          </p>

          {/* Appointment Card */}
          {message.appointment && (
            <div className="mt-3 p-3 bg-white/10 dark:bg-black/10 rounded-lg border border-white/20">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span className="font-semibold text-sm">Appuntamento</span>
                </div>
                <Badge variant={
                  message.appointment.status === 'confirmed'
                    ? 'default'
                    : 'secondary'
                }>
                  {message.appointment.status === 'confirmed' ? 'Confermato' : 'In attesa'}
                </Badge>
              </div>

              <div className="space-y-1 text-sm">
                <p><strong>{message.appointment.clientName}</strong></p>
                <p>{message.appointment.serviceType}</p>
                <p className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {scheduleAIClient.formatDateTime(new Date(message.appointment.dateTime))}
                </p>
              </div>

              {/* Action Buttons */}
              {message.appointment.meetingLink && (
                <div className="mt-3">
                  <Link
                    href={message.appointment.meetingLink}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Button variant="outline" size="sm" className="w-full">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Join Meeting
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Timestamp */}
        <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground px-1">
          <Clock className="w-3 h-3" />
          <span>{formatTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  );
};
```

### 2. Enhanced Loading States

```tsx
// Improved Loading Components
const TypingIndicator: React.FC = () => (
  <div className="flex gap-1 justify-center items-center py-2">
    <div className="flex gap-1">
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
    <span className="text-sm text-muted-foreground ml-2">Sto scrivendo...</span>
  </div>
);

const StreamingMessage: React.FC<{ content: string }> = ({ content }) => (
  <div className="flex gap-3 justify-start">
    <Avatar className="w-8 h-8 mt-1">
      <AvatarFallback className="bg-blue-500 text-white">
        <Bot className="w-4 h-4" />
      </AvatarFallback>
    </Avatar>
    <Card className="p-3 bg-muted max-w-[80%] relative">
      <p className="text-sm whitespace-pre-wrap pr-6">
        {content}
      </p>
      <div className="absolute bottom-3 right-3">
        <div className="w-2 h-4 bg-blue-500 animate-pulse" />
      </div>
    </Card>
  </div>
);
```

### 3. Responsive Design Improvements

#### Enhanced Mobile Sidebar
```tsx
// Mobile-Optimized Sidebar Component
const MobileSidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden fixed top-4 left-4 z-50"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Menu className="w-5 h-5" />
      </Button>

      {/* Mobile Sidebar Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed top-0 left-0 h-full w-80 bg-background border-r z-50 transform transition-transform duration-300 md:relative md:transform-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}>
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
        />
      </div>
    </>
  );
};
```

#### Responsive Input Area
```tsx
// Enhanced Input Component
const ChatInput: React.FC = () => {
  const [inputValue, setInputValue] = useState('');

  return (
    <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Scrivi il tuo messaggio..."
              className="min-h-[48px] max-h-48 resize-none pr-12 border-2 focus:border-blue-500 transition-colors"
              rows={1}
              style={{
                height: 'auto',
                minHeight: '48px'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = `${Math.min(target.scrollHeight, 192)}px`;
              }}
            />

            {/* Character count for long messages */}
            {inputValue.length > 200 && (
              <div className="absolute bottom-2 right-12 text-xs text-muted-foreground">
                {inputValue.length}/1000
              </div>
            )}
          </div>

          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="h-12 px-6 shrink-0"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Input Helper */}
        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>Premi Invio per inviare, Shift+Invio per andare a capo</span>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="h-6 px-2">
              <Paperclip className="w-3 h-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2">
              <Mic className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### 4. Enhanced Error Handling & User Feedback

```tsx
// Error Boundary Component
class ChatErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Chat Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="m-4 p-6 border-red-200 bg-red-50 dark:bg-red-900/10">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
              Qualcosa è andato storto
            </h3>
          </div>

          <p className="text-sm text-red-700 dark:text-red-300 mb-4">
            Si è verificato un errore nella chat. Prova a ricaricare la pagina o contatta il supporto.
          </p>

          <div className="flex gap-2">
            <Button onClick={() => window.location.reload()} variant="outline">
              Ricarica Pagina
            </Button>
            <Button onClick={() => this.setState({ hasError: false })}>
              Riprova
            </Button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}

// Enhanced Error Message Component
const ErrorMessage: React.FC<{ error: string; onRetry?: () => void }> = ({ error, onRetry }) => (
  <Card className="m-4 p-4 border-red-200 bg-red-50 dark:bg-red-900/10">
    <div className="flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-red-800 dark:text-red-200 mb-1">
          Errore di comunicazione
        </h4>
        <p className="text-sm text-red-700 dark:text-red-300 mb-3">
          {error}
        </p>
        {onRetry && (
          <Button
            onClick={onRetry}
            variant="outline"
            size="sm"
            className="border-red-200 text-red-700 hover:bg-red-100"
          >
            Riprova
          </Button>
        )}
      </div>
    </div>
  </Card>
);
```

### 5. Success States & User Onboarding

```tsx
// Success Notification Component
const SuccessNotification: React.FC<{ message: string; appointment?: AppointmentData }> = ({
  message,
  appointment
}) => (
  <Card className="m-4 p-4 border-green-200 bg-green-50 dark:bg-green-900/10">
    <div className="flex items-start gap-3">
      <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-green-800 dark:text-green-200 mb-1">
          Operazione completata!
        </h4>
        <p className="text-sm text-green-700 dark:text-green-300 mb-3">
          {message}
        </p>

        {appointment && (
          <div className="p-3 bg-white/50 dark:bg-black/20 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">{appointment.serviceType}</p>
                <p className="text-xs text-muted-foreground">
                  {scheduleAIClient.formatDateTime(new Date(appointment.dateTime))}
                </p>
              </div>
              <Button size="sm" variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                Aggiungi al calendario
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  </Card>
);

// Welcome/Onboarding Component
const WelcomeMessage: React.FC = () => (
  <div className="text-center py-8 px-4">
    <div className="max-w-md mx-auto">
      <div className="mb-4">
        <Calendar className="w-12 h-12 text-blue-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">
          Benvenuto in ScheduleAI!
        </h2>
        <p className="text-muted-foreground">
          Sono il tuo assistente personale per le prenotazioni. Posso aiutarti a:
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
        <Card className="p-3">
          <CalendarPlus className="w-6 h-6 text-blue-500 mb-2" />
          <h3 className="font-medium text-sm mb-1">Prenotare</h3>
          <p className="text-xs text-muted-foreground">
            Prenota appuntamenti facilmente
          </p>
        </Card>

        <Card className="p-3">
          <Clock className="w-6 h-6 text-green-500 mb-2" />
          <h3 className="font-medium text-sm mb-1">Verificare</h3>
          <p className="text-xs text-muted-foreground">
            Controlla disponibilità e orari
          </p>
        </Card>

        <Card className="p-3">
          <Settings className="w-6 h-6 text-purple-500 mb-2" />
          <h3 className="font-medium text-sm mb-1">Gestire</h3>
          <p className="text-xs text-muted-foreground">
            Modifica o cancella prenotazioni
          </p>
        </Card>
      </div>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          💡 <strong>Consiglio:</strong> Scrivi semplicemente "Vorrei prenotare un appuntamento" per iniziare!
        </p>
      </div>
    </div>
  </div>
);
```

### 6. Accessibility Improvements

```tsx
// Accessible Chat Interface
const AccessibleChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="flex flex-col h-full" role="application" aria-label="Chat di prenotazione">
      {/* Screen Reader Announcements */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {isLoading && "L'assistente sta scrivendo una risposta"}
      </div>

      {/* Messages Area */}
      <ScrollArea
        className="flex-1 p-4"
        role="log"
        aria-label="Messaggi della chat"
        aria-live="polite"
      >
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 mb-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
            role="article"
            aria-label={`Messaggio da ${message.role === 'user' ? 'utente' : 'assistente'}`}
          >
            {/* Message content with proper ARIA labels */}
          </div>
        ))}
      </ScrollArea>

      {/* Accessible Input */}
      <form
        onSubmit={handleSendMessage}
        className="p-4 border-t"
        role="form"
        aria-label="Invia messaggio"
      >
        <label htmlFor="chat-input" className="sr-only">
          Scrivi il tuo messaggio
        </label>
        <Textarea
          id="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Scrivi il tuo messaggio..."
          className="min-h-[48px] resize-none"
          aria-describedby="input-help"
          aria-label="Messaggio per l'assistente"
        />

        <div id="input-help" className="sr-only">
          Premi Invio per inviare il messaggio, Shift+Invio per andare a capo
        </div>

        <Button
          type="submit"
          disabled={!inputValue.trim() || isLoading}
          aria-label={isLoading ? "Invio in corso" : "Invia messaggio"}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
          ) : (
            <Send className="w-4 h-4" aria-hidden="true" />
          )}
        </Button>
      </form>
    </div>
  );
};
```

### 7. Enhanced Design System

```css
/* Enhanced CSS Variables and Animations */
:root {
  --background: #ffffff;
  --foreground: #171717;
  --card: #ffffff;
  --card-foreground: #171717;
  --popover: #ffffff;
  --popover-foreground: #171717;
  --primary: #2563eb;
  --primary-foreground: #ffffff;
  --secondary: #f1f5f9;
  --secondary-foreground: #0f172a;
  --muted: #f8fafc;
  --muted-foreground: #64748b;
  --accent: #f1f5f9;
  --accent-foreground: #0f172a;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: #e2e8f0;
  --input: #e2e8f0;
  --ring: #2563eb;
  --radius: 0.5rem;

  /* Custom animations */
  --animation-duration: 0.3s;
  --animation-timing: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-fadeIn {
  animation: fadeIn var(--animation-duration) var(--animation-timing);
}

.animate-slideIn {
  animation: slideIn var(--animation-duration) var(--animation-timing);
}

/* Enhanced focus states */
.focus-ring {
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white;
}

/* Dark mode improvements */
@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
    --card: #0a0a0a;
    --card-foreground: #ededed;
    --popover: #0a0a0a;
    --popover-foreground: #ededed;
    --primary: #3b82f6;
    --primary-foreground: #ffffff;
    --secondary: #1f2937;
    --secondary-foreground: #f9fafb;
    --muted: #1f2937;
    --muted-foreground: #9ca3af;
    --accent: #1f2937;
    --accent-foreground: #f9fafb;
    --destructive: #ef4444;
    --destructive-foreground: #ffffff;
    --border: #374151;
    --input: #374151;
    --ring: #3b82f6;
  }
}

/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Enhanced responsive utilities */
@media (max-width: 640px) {
  .mobile-hidden {
    display: none;
  }

  .mobile-full {
    width: 100%;
  }

  .mobile-text-sm {
    font-size: 0.875rem;
  }
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }

  .print-break {
    page-break-after: always;
  }
}
```

## 🚀 Implementation Recommendations

### Phase 1: Critical Fixes (Immediate)
1. **Fix Link Rendering**: Implement proper link detection and styling
2. **Mobile Sidebar**: Fix mobile navigation and responsiveness
3. **Error Handling**: Improve error messages and retry mechanisms
4. **Loading States**: Enhance loading indicators

### Phase 2: Enhanced UX (1-2 weeks)
1. **Message Improvements**: Better message styling and animations
2. **Success Notifications**: Add confirmation states
3. **Accessibility**: Implement ARIA labels and keyboard navigation
4. **Dark Mode**: Enhance dark mode support

### Phase 3: Advanced Features (2-3 weeks)
1. **Voice Input**: Add speech-to-text capabilities
2. **File Attachments**: Allow file uploads in chat
3. **Calendar Integration**: Add "Add to Calendar" functionality
4. **Push Notifications**: Implement browser notifications

### Phase 4: Performance & Analytics (3-4 weeks)
1. **Performance Optimization**: Code splitting and lazy loading
2. **Analytics**: Add user interaction tracking
3. **A/B Testing**: Test different UI patterns
4. **Progressive Web App**: PWA capabilities

## 📱 Mobile-Specific Improvements

### Touch Interactions
```tsx
// Touch-optimized components
const TouchOptimizedButton: React.FC<ButtonProps> = ({ children, ...props }) => (
  <Button
    {...props}
    className="min-h-[44px] min-w-[44px] active:scale-95 transition-transform"
  >
    {children}
  </Button>
);

// Swipe gestures for mobile
const SwipeableMessage: React.FC<{ message: Message }> = ({ message }) => {
  const [swipeOffset, setSwipeOffset] = useState(0);

  return (
    <div
      className="touch-pan-y"
      style={{ transform: `translateX(${swipeOffset}px)` }}
    >
      {/* Message content */}
    </div>
  );
};
```

### Mobile Keyboard Handling
```tsx
// Mobile keyboard optimization
const MobileOptimizedChat: React.FC = () => {
  const [isKeyboardOpen, setIsKeyboardOpen] = useState(false);
  const [viewportHeight, setViewportHeight] = useState(0);

  useEffect(() => {
    const handleResize = () => {
      const currentHeight = window.visualViewport?.height || window.innerHeight;
      setViewportHeight(currentHeight);
      setIsKeyboardOpen(currentHeight < window.innerHeight * 0.8);
    };

    window.visualViewport?.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.visualViewport?.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div
      className="flex flex-col h-screen"
      style={{ height: isKeyboardOpen ? viewportHeight : '100vh' }}
    >
      {/* Chat content */}
    </div>
  );
};
```

## 🎨 Design System Enhancements

### Color Palette
```typescript
// Enhanced color system
export const colors = {
  primary: {
    50: '#eff6ff',
    500: '#2563eb',
    600: '#1d4ed8',
    700: '#1e40af',
    900: '#1e3a8a',
  },
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
  },
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    600: '#d97706',
  },
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
  },
  neutral: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    500: '#64748b',
    700: '#334155',
    900: '#0f172a',
  }
};
```

### Typography Scale
```typescript
// Typography system
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],
    sm: ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem', { lineHeight: '1.5rem' }],
    lg: ['1.125rem', { lineHeight: '1.75rem' }],
    xl: ['1.25rem', { lineHeight: '1.75rem' }],
    '2xl': ['1.5rem', { lineHeight: '2rem' }],
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
  },
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};
```

## 📊 Performance Optimizations

### Code Splitting
```tsx
// Lazy load heavy components
const ChatInterface = lazy(() => import('@/components/chat/ChatInterface'));
const Sidebar = lazy(() => import('@/components/layout/Sidebar'));

// Dynamic imports for features
const loadAdvancedFeatures = () => import('@/components/advanced-features');
```

### Image Optimization
```tsx
// Optimized Avatar component
const OptimizedAvatar: React.FC<AvatarProps> = ({ src, alt, ...props }) => (
  <Avatar {...props}>
    {src && (
      <AvatarImage
        src={src}
        alt={alt}
        sizes="(max-width: 768px) 32px, 40px"
      />
    )}
    <AvatarFallback>
      <User className="w-4 h-4" />
    </AvatarFallback>
  </Avatar>
);
```

## 🔄 Testing Strategy

### Component Testing
```typescript
// Example tests with React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/ChatInterface';

describe('ChatInterface', () => {
  test('renders welcome message', () => {
    render(<ChatInterface />);
    expect(screen.getByText(/Buongiorno! Sono ScheduleAI/)).toBeInTheDocument();
  });

  test('sends message on form submission', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Scrivi il tuo messaggio/);
    const sendButton = screen.getByRole('button', { name: /invia/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
  });

  test('renders links as clickable elements', () => {
    render(<ChatInterface />);

    const messageWithLink = 'Visit https://example.com for more info';
    // Mock the message with link
    // Test that link is rendered as clickable element
  });
});
```

## 📈 Analytics & Monitoring

### User Interaction Tracking
```typescript
// Analytics integration
import { analytics } from '@/lib/analytics';

const trackUserAction = (action: string, properties?: Record<string, any>) => {
  analytics.track(action, {
    timestamp: new Date().toISOString(),
    sessionId: getCurrentSessionId(),
    ...properties,
  });
};

// Usage in components
const handleSendMessage = () => {
  trackUserAction('message_sent', {
    messageLength: inputValue.length,
    hasAppointment: inputValue.toLowerCase().includes('appuntamento'),
  });

  // Send message logic
};
```

This comprehensive UI/UX improvement plan addresses all the key issues identified and provides a roadmap for enhancing the Next.js appointment scheduling application with modern best practices, accessibility considerations, and mobile optimizations.