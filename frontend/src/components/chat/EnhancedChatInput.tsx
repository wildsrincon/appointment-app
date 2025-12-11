'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Mic, Paperclip, Send, Smile, X } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';

interface EnhancedChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  showShortcuts?: boolean;
  allowAttachments?: boolean;
  allowVoiceRecording?: boolean;
  onAttachmentClick?: () => void;
  onVoiceRecordClick?: () => void;
}

export const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Scrivi il tuo messaggio...",
  maxLength = 1000,
  showShortcuts = true,
  allowAttachments = true,
  allowVoiceRecording = true,
  onAttachmentClick,
  onVoiceRecordClick,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showEmojis, setShowEmojis] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isComposing, setIsComposing] = useState(false);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = Math.min(textarea.scrollHeight, 192); // Max height of 192px
      textarea.style.height = `${scrollHeight}px`;
    }
  }, [inputValue]);

  // Update character count
  useEffect(() => {
    setCharCount(inputValue.length);
  }, [inputValue]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || disabled || isSending || isComposing) return;

    const messageToSend = inputValue.trim();
    setInputValue('');
    setIsSending(true);

    try {
      await onSendMessage(messageToSend);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Revert the input value if sending failed
      setInputValue(messageToSend);
    } finally {
      setIsSending(false);
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        // Allow line break with Shift+Enter
        return;
      } else if (!e.shiftKey && !isComposing) {
        // Send message with Enter
        e.preventDefault();
        handleSendMessage();
      }
    }

    // Escape key to close emoji picker
    if (e.key === 'Escape' && showEmojis) {
      setShowEmojis(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      setInputValue(newValue);
    }
  };

  const handleEmojiSelect = (emoji: string) => {
    setInputValue(prev => prev + emoji);
    setShowEmojis(false);
    textareaRef.current?.focus();
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    // Handle paste events for rich content
    const items = e.clipboardData?.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          e.preventDefault();
          // Handle image paste
          console.log('Image pasted, would trigger attachment handler');
          if (onAttachmentClick) {
            onAttachmentClick();
          }
        }
      }
    }
  };

  // Emoji picker component
  const EmojiPicker: React.FC = () => {
    const commonEmojis = ['😊', '👍', '❤️', '🎉', '👋', '😅', '🙏', '💯', '✅', '❌', '⏰', '📅'];

    return (
      <Card className="absolute bottom-full left-0 mb-2 p-3 shadow-lg border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Emoji</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowEmojis(false)}
            className="h-6 w-6 p-0"
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
        <div className="grid grid-cols-6 gap-1">
          {commonEmojis.map((emoji, index) => (
            <Button
              key={index}
              variant="ghost"
              size="sm"
              onClick={() => handleEmojiSelect(emoji)}
              className="h-8 w-8 p-0 text-lg hover:bg-muted"
            >
              {emoji}
            </Button>
          ))}
        </div>
      </Card>
    );
  };

  return (
    <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-4xl mx-auto">
        {/* Character count warning */}
        {charCount > maxLength * 0.9 && (
          <div className="mb-2 text-xs text-amber-600 dark:text-amber-400">
            {charCount}/{maxLength} caratteri - quasi al limite
          </div>
        )}

        <div className="relative">
          {/* Emoji Picker */}
          {showEmojis && <EmojiPicker />}

          <div className="flex gap-3 items-end">
            {/* Action Buttons */}
            <div className="flex gap-1 items-center">
              {allowAttachments && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onAttachmentClick}
                  disabled={disabled}
                  className="h-10 w-10 p-0"
                  title="Allega file"
                >
                  <Paperclip className="w-4 h-4" />
                </Button>
              )}

              {allowVoiceRecording && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onVoiceRecordClick}
                  disabled={disabled}
                  className="h-10 w-10 p-0"
                  title="Registra messaggio vocale"
                >
                  <Mic className="w-4 h-4" />
                </Button>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEmojis(!showEmojis)}
                disabled={disabled}
                className="h-10 w-10 p-0"
                title="Inserisci emoji"
              >
                <Smile className="w-4 h-4" />
              </Button>
            </div>

            {/* Text Input */}
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onPaste={handlePaste}
                onCompositionStart={() => setIsComposing(true)}
                onCompositionEnd={() => setIsComposing(false)}
                placeholder={placeholder}
                disabled={disabled || isSending}
                className="min-h-[48px] max-h-48 resize-none pr-12 border-2 focus:border-blue-500 transition-colors"
                rows={1}
                style={{
                  height: 'auto',
                  minHeight: '48px'
                }}
                aria-label={placeholder}
                aria-describedby="input-help"
              />

              {/* Character count for long messages */}
              {charCount > 50 && (
                <div className="absolute bottom-2 right-12 text-xs text-muted-foreground bg-background/90 px-1 rounded">
                  {charCount}/{maxLength}
                </div>
              )}
            </div>

            {/* Send Button */}
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || disabled || isSending}
              className="h-12 px-6 shrink-0"
              size="default"
            >
              {isSending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Invio...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Invia
                </>
              )}
            </Button>
          </div>

          {/* Input Helper */}
          {showShortcuts && (
            <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
              <span id="input-help">
                Premi <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Invio</kbd> per inviare,
                <kbd className="px-1 py-0.5 bg-muted rounded text-xs ml-1">Shift+Invio</kbd> per andare a capo
              </span>
              <div className="flex items-center gap-2">
                {allowAttachments && (
                  <span className="hidden sm:inline">
                    <kbd className="px-1 py-0.5 bg-muted rounded text-xs">Ctrl+V</kbd> per allegare
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions (Mobile) */}
        <div className="mt-3 sm:hidden">
          <div className="flex justify-around">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setInputValue(prev => prev + 'Vorrei prenotare un appuntamento')}
              className="text-xs h-8 px-3"
            >
              📅 Prenota
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setInputValue(prev => prev + 'Quali orari sono disponibili?')}
              className="text-xs h-8 px-3"
            >
              ⏰ Orari
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setInputValue(prev => prev + 'Vorrei modificare la mia prenotazione')}
              className="text-xs h-8 px-3"
            >
              ✏️ Modifica
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setInputValue(prev => prev + 'Aiuto')}
              className="text-xs h-8 px-3"
            >
              ❓ Aiuto
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatInput;