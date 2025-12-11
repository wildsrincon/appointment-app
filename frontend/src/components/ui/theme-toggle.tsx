'use client';

import React, { useState, useEffect } from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/contexts/ThemeContext';

interface ThemeToggleProps {
  variant?: 'default' | 'compact' | 'icon-only';
  className?: string;
}

export function ThemeToggle({ variant = 'default', className = '' }: ThemeToggleProps) {
  const { theme, setTheme, effectiveTheme, toggleTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch by only rendering theme-dependent content after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  const getIcon = () => {
    if (!mounted) return <Sun className="h-4 w-4" />; // Default icon for SSR

    switch (effectiveTheme) {
      case 'light':
        return <Sun className="h-4 w-4" />;
      case 'dark':
        return <Moon className="h-4 w-4" />;
      default:
        return <Sun className="h-4 w-4" />;
    }
  };

  const getLabel = () => {
    if (!mounted) return 'Sistema'; // Default label for SSR

    switch (theme) {
      case 'light':
        return 'Chiaro';
      case 'dark':
        return 'Scuro';
      case 'system':
        return 'Sistema';
      default:
        return 'Sistema';
    }
  };

  
  if (variant === 'icon-only') {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleTheme}
        className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 ${className}`}
        title={mounted ? (effectiveTheme === 'light' ? 'Passa alla modalità scura' : 'Passa alla modalità chiara') : 'Cambia tema'}
      >
        {getIcon()}
      </Button>
    );
  }

  if (variant === 'compact') {
    return (
      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsOpen(!isOpen)}
          className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${className}`}
          title={mounted ? `Tema corrente: ${getLabel()}` : 'Cambia tema'}
        >
          {getIcon()}
        </Button>

        {isOpen && (
          <div className="absolute top-full right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 min-w-32">
            <div className="py-1">
              <button
                onClick={() => { setTheme('light'); setIsOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                  theme === 'light' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                }`}
              >
                <Sun className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
                Chiaro
              </button>
              <button
                onClick={() => { setTheme('dark'); setIsOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                  theme === 'dark' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                }`}
              >
                <Moon className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
                Scuro
              </button>
              <button
                onClick={() => { setTheme('system'); setIsOpen(false); }}
                className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                  theme === 'system' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                }`}
              >
                <Monitor className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
                Sistema
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default variant with text
  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className={`justify-start h-8 px-3 ${className}`}
      >
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="text-xs font-medium">{getLabel()}</span>
        </div>
      </Button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 min-w-40">
          <div className="py-1">
            <button
              onClick={() => { setTheme('light'); setIsOpen(false); }}
              className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                theme === 'light' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
              }`}
            >
              <Sun className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
              Chiaro
            </button>
            <button
              onClick={() => { setTheme('dark'); setIsOpen(false); }}
              className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                theme === 'dark' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
              }`}
            >
              <Moon className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
              Scuro
            </button>
            <button
              onClick={() => { setTheme('system'); setIsOpen(false); }}
              className={`w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                theme === 'system' ? 'bg-blue-50 dark:bg-blue-900/30' : ''
              }`}
            >
              <Monitor className="h-4 w-4 mr-2 inline text-gray-600 dark:text-gray-300" />
              Sistema
            </button>
          </div>
        </div>
      )}
    </div>
  );
}