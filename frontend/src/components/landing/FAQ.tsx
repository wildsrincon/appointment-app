'use client';

import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: 'Come funziona ScheduleAI?',
      answer: 'ScheduleAI utilizza intelligenza artificiale avanzata per gestire le prenotazioni tramite chat. I tuoi clienti possono chattare con il nostro assistente AI che comprende le loro esigenze e propone automaticamente gli orari disponibili, sincronizzando tutto con il tuo Google Calendar.'
    },
    {
      question: 'È difficile configurare?',
      answer: 'Assolutamente no! La configurazione richiede meno di 2 minuti. Ti basta collegare il tuo account Google Calendar e il sistema è pronto per ricevere prenotazioni. Non serve essere esperti di tecnologia.'
    },
    {
      question: 'In che lingue lavora l\'assistente?',
      answer: 'ScheduleAI è ottimizzato per l\'italiano ma supporta perfettamente anche inglese e spagnolo. L\'AI riconosce automaticamente la lingua del cliente e risponde nella stessa lingua.'
    },
    {
      question: 'Posso personalizzare le risposte?',
      answer: 'Sì! Nel piano Professional ed Enterprise puoi personalizzare le risposte dell\'AI, aggiungere i tuoi servizi, definire orari di lavoro e molto altro. L\'AI si adatterà al tuo stile e alle tue esigenze.'
    },
    {
      question: 'I miei dati sono al sicuro?',
      answer: 'Assolutamente sì. Utilizziamo crittografia end-to-end, siamo conformi al GDPR e i nostri server si trovano in Europa. Non condividiamo mai i tuoi dati con terze parti e tu mantieni il pieno controllo.'
    },
    {
      question: 'Posso cancellare quando voglio?',
      answer: 'Certamente! Non ci sono contratti a lungo termine. Puoi cancellare o modificare il tuo piano in qualsiasi momento senza penali. I tuoi dati rimangono disponibili per 30 giorni dopo la cancellazione.'
    }
  ];

  return (
    <section id="faq" className="py-24 bg-gradient-to-br from-gray-50 to-blue-50 scroll-mt-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-4">
            <span className="text-sm font-semibold text-blue-900">FAQ</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Domande
            <span className="text-blue-600"> Frequenti</span>
          </h2>
          <p className="text-xl text-gray-600">
            Tutto ciò che devi sapere su ScheduleAI
          </p>
        </div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full px-6 py-5 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <span className="text-lg font-semibold text-gray-900 pr-8">
                  {faq.question}
                </span>
                <ChevronDown
                  className={`w-5 h-5 text-gray-500 flex-shrink-0 transition-transform duration-300 ${
                    openIndex === index ? 'rotate-180' : ''
                  }`}
                />
              </button>
              <div
                className={`overflow-hidden transition-all duration-300 ${
                  openIndex === index ? 'max-h-96' : 'max-h-0'
                }`}
              >
                <div className="px-6 pb-5">
                  <p className="text-gray-600 leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            Hai altre domande?
          </p>
          <a
            href="mailto:support@scheduleai.it"
            className="inline-flex items-center gap-2 text-blue-600 font-semibold hover:text-blue-700 transition-colors"
          >
            Contatta il nostro supporto
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}
