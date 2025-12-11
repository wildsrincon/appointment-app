'use client';

import React from 'react';
import { CalendarPlus, Clock, Settings, Calendar, Sparkles } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export const WelcomeMessage: React.FC = () => {
  const quickActions = [
    {
      icon: CalendarPlus,
      title: 'Prenota',
      description: 'Prenota un nuovo appuntamento',
      message: 'Vorrei prenotare un appuntamento',
      color: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20'
    },
    {
      icon: Clock,
      title: 'Verifica',
      description: 'Controlla disponibilità e orari',
      message: 'Quali orari sono disponibili?',
      color: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-900/20'
    },
    {
      icon: Settings,
      title: 'Gestisci',
      description: 'Modifica o cancella prenotazioni',
      message: 'Vorrei modificare la mia prenotazione',
      color: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20'
    }
  ];

  const handleQuickAction = (message: string) => {
    // Find the input element and set its value
    const inputElement = document.querySelector('textarea[placeholder*="Scrivi il tuo messaggio"]') as HTMLTextAreaElement;
    if (inputElement) {
      inputElement.value = message;
      inputElement.focus();
      // Trigger the change event
      inputElement.dispatchEvent(new Event('input', { bubbles: true }));
    }
  };

  return (
    <div className="text-center py-8 px-4 animate-fadeIn">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Welcome Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <Calendar className="w-16 h-16 text-blue-500" />
              <Sparkles className="w-6 h-6 text-yellow-500 absolute -top-2 -right-2" />
            </div>
          </div>

          <h2 className="text-2xl font-bold text-foreground mb-2">
            Benvenuto in ScheduleAI!
          </h2>

          <p className="text-muted-foreground text-lg leading-relaxed">
            Sono il tuo assistente personale per le prenotazioni. Posso aiutarti a gestire i tuoi appuntamenti in modo semplice e veloce.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {quickActions.map((action, index) => (
            <Card
              key={index}
              className={`p-4 cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-0 ${action.bgColor} group`}
              onClick={() => handleQuickAction(action.message)}
            >
              <div className="flex flex-col items-center text-center space-y-3">
                <div className={`p-3 rounded-full bg-white dark:bg-gray-800 group-hover:scale-110 transition-transform`}>
                  <action.icon className={`w-6 h-6 ${action.color}`} />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">{action.title}</h3>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Tips Section */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-bold">💡</span>
            </div>
            <div className="text-left">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                Consigli per iniziare
              </h4>
              <div className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                <p>
                  <strong>Per prenotare:</strong> Scrivi "Vorrei prenotare un appuntamento" oppure specifica il servizio desiderato
                </p>
                <p>
                  <strong>Per modificare:</strong> Menziona "modifica" o "cambia" seguito dall'appuntamento da modificare
                </p>
                <p>
                  <strong>Per cancellare:</strong> Usa "cancella" o "elimina" per rimuovere una prenotazione
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="space-y-2">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto">
              <span className="text-xl">⚡</span>
            </div>
            <h4 className="font-medium text-sm">Veloce</h4>
            <p className="text-xs text-muted-foreground">Prenotazioni immediate</p>
          </div>

          <div className="space-y-2">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto">
              <span className="text-xl">🔒</span>
            </div>
            <h4 className="font-medium text-sm">Sicuro</h4>
            <p className="text-xs text-muted-foreground">Dati protetti</p>
          </div>

          <div className="space-y-2">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center mx-auto">
              <span className="text-xl">📱</span>
            </div>
            <h4 className="font-medium text-sm">Mobile</h4>
            <p className="text-xs text-muted-foreground">Disponibile ovunque</p>
          </div>

          <div className="space-y-2">
            <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mx-auto">
              <span className="text-xl">🎯</span>
            </div>
            <h4 className="font-medium text-sm">Intelligente</h4>
            <p className="text-xs text-muted-foreground">Assistente AI avanzato</p>
          </div>
        </div>

        {/* Example Questions */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-3">
            Oppure prova con una di queste domande:
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              'Ci sono disponibilità per domani?',
              'Quali servizi offrite?',
              'Posso spostare il mio appuntamento?',
              'Come funziona la cancellazione?'
            ].map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction(question)}
                className="text-xs h-8 px-3 hover:bg-muted"
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeMessage;