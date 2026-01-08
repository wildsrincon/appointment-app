'use client';

import { Bot, CalendarClock, Globe, Lock, MessageSquare, TrendingUp } from 'lucide-react';

export function Features() {
  const features = [
    {
      icon: Bot,
      title: 'AI Intelligente',
      description: 'Il nostro assistente AI comprende il linguaggio naturale e gestisce prenotazioni complesse in italiano, inglese e spagnolo.',
      color: 'bg-blue-500',
      lightColor: 'bg-blue-50'
    },
    {
      icon: CalendarClock,
      title: 'Disponibilità 24/7',
      description: 'I tuoi clienti possono prenotare in qualsiasi momento. Niente più telefonate perse orari di lavoro limitati.',
      color: 'bg-green-500',
      lightColor: 'bg-green-50'
    },
    {
      icon: MessageSquare,
      title: 'Conversazioni Naturali',
      description: 'Chat fluida come con un umano. L\'AI ricorda il contesto e adatta le risposte in base alle esigenze del cliente.',
      color: 'bg-purple-500',
      lightColor: 'bg-purple-50'
    },
    {
      icon: Globe,
      title: 'Google Calendar Integrato',
      description: 'Sincronizzazione automatica con il tuo calendario. Ogni prenotazione viene aggiunta istantaneamente.',
      color: 'bg-red-500',
      lightColor: 'bg-red-50'
    },
    {
      icon: Lock,
      title: 'Sicurezza & Privacy',
      description: 'Dati crittografati end-to-end. Conformità completa con GDPR e le normative europee sulla privacy.',
      color: 'bg-orange-500',
      lightColor: 'bg-orange-50'
    },
    {
      icon: TrendingUp,
      title: 'Analytics Avanzato',
      description: 'Statistiche dettagliate su prenotazioni, orari di punta e preferenze dei clienti per ottimizzare il tuo business.',
      color: 'bg-cyan-500',
      lightColor: 'bg-cyan-50'
    }
  ];

  return (
    <section id="features" className="py-24 bg-white scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-4">
            <span className="text-sm font-semibold text-blue-900">Funzionalità</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Tutto ciò che ti serve per
            <span className="text-blue-600"> gestire prenotazioni</span>
          </h2>
          <p className="text-xl text-gray-600">
            Potente AI intelligente che si prende cura di ogni aspetto delle tue prenotazioni,
            lasciandoti libero di concentrarti sul tuo business.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative p-8 bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-xl hover:shadow-blue-900/5 transition-all duration-300"
            >
              {/* Icon Container */}
              <div className={`inline-flex p-3 ${feature.lightColor} rounded-xl mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>

              {/* Hover Effect Border */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-50/0 to-purple-50/0 group-hover:from-blue-50/50 group-hover:to-purple-50/50 transition-all duration-300 -z-10" />
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            Vuoi vedere tutte le funzionalità in azione?
          </p>
          <a
            href="#pricing"
            className="inline-flex items-center gap-2 text-blue-600 font-semibold hover:text-blue-700 transition-colors"
          >
            Guarda i piani disponibili
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}
