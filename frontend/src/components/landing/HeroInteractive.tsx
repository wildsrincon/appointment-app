'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Calendar, CheckCircle2, Sparkles, MessageCircle, Play, Pause } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

// Chat messages for demo
const demoConversation = [
  { role: 'user', text: 'Buongiorno! Vorrei prenotare una consulenza fiscale per martedì prossimo.' },
  { role: 'assistant', text: 'Buongiorno! Certamente, posso aiutarti. Per martedì 14 gennaio ho disponibilità:' },
  { role: 'assistant', text: '📅 09:00 - 09:50\n📅 11:00 - 11:50\n📅 15:00 - 15:50\n\nQuale orario preferisci?' },
  { role: 'user', text: 'Perfetto, prendo le 11:00!' },
  { role: 'assistant', text: '✅ Ottimo! Ho prenotato la tua consulenza fiscale per martedì 14 gennaio alle 11:00.\n\nRiceverai una email di confertra tra pochi minuti. A presto! 🎉' }
];

export function HeroInteractive() {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [typingText, setTypingText] = useState('');
  const [showTyping, setShowTyping] = useState(false);

  const playDemo = async () => {
    setIsPlaying(true);
    setCurrentMessageIndex(0);

    for (let i = 0; i < demoConversation.length; i++) {
      setCurrentMessageIndex(i);
      const message = demoConversation[i];

      if (message.role === 'assistant') {
        setShowTyping(true);
        setTypingText('');

        // Typing effect
        for (let charIndex = 0; charIndex <= message.text.length; charIndex++) {
          await new Promise(resolve => setTimeout(resolve, 30));
          setTypingText(message.text.slice(0, charIndex));
        }

        setShowTyping(false);
      } else {
        setTypingText(message.text);
      }

      // Pause between messages
      if (i < demoConversation.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
    }

    setIsPlaying(false);
  };

  const resetDemo = () => {
    setCurrentMessageIndex(0);
    setTypingText('');
    setShowTyping(false);
    setIsPlaying(false);
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-white via-blue-50 to-white">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-blue-100/40 via-purple-50/30 to-blue-50/40"
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      {/* Animated Grid */}
      <div className="absolute inset-0 bg-grid-blue-50/[0.4] [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]" />

      {/* Floating Gradient Orbs */}
      <motion.div
        className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-br from-blue-400/30 to-purple-400/30 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="text-left">
            {/* Animated Badge */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-8"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4 text-blue-600" />
              </motion.div>
              <span className="text-sm font-medium text-blue-900">Demo Live Interattiva</span>
            </motion.div>

            {/* Headlines */}
            <motion.h1
              className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <span className="block text-gray-900">Vedi come</span>
              <span className="block text-blue-600 mt-2">ScheduleAI lavora</span>
            </motion.h1>

            <motion.p
              className="text-lg sm:text-xl text-gray-600 leading-relaxed mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Guarda l'AI in azione mentre gestisce una prenotazione reale in pochi secondi.
              <span className="text-blue-600 font-semibold"> Niente bottoni complicati</span>, solo conversazione naturale.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Link href="/app">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg shadow-xl shadow-blue-600/20 rounded-full"
                  >
                    Inizia Gratis Ora
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </motion.div>
              </Link>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  size="lg"
                  variant="outline"
                  className="px-8 py-6 text-lg border-2 border-gray-200 hover:border-blue-300 rounded-full"
                >
                  Scopri di Più
                </Button>
              </motion.div>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              className="flex flex-wrap gap-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.6 }}
            >
              {[
                { icon: CheckCircle2, text: 'Setup in 2 min' },
                { icon: Calendar, text: 'Google Calendar' },
                { icon: MessageCircle, text: 'Chat Naturale' }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-2 text-gray-600 px-4 py-2 rounded-full bg-white shadow-sm"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                  whileHover={{ scale: 1.05, y: -2 }}
                >
                  <item.icon className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium">{item.text}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Right Content - Interactive Demo */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="relative"
          >
            {/* Phone/Chat Container */}
            <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                    <Calendar className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="text-white">
                    <h3 className="font-semibold">ScheduleAI Assistant</h3>
                    <p className="text-sm text-blue-100">Online • Risponde subito</p>
                  </div>
                </div>
              </div>

              {/* Chat Messages */}
              <div className="p-6 space-y-4 min-h-[400px] max-h-[400px] overflow-y-auto">
                <AnimatePresence mode='wait'>
                  {demoConversation.slice(0, currentMessageIndex + 1).map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl p-4 ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        {index === currentMessageIndex && message.role === 'assistant' && showTyping ? (
                          <div className="flex items-center gap-1">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-100" />
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-200" />
                          </div>
                        ) : (
                          <p className="text-sm whitespace-pre-line">{message.text}</p>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Controls */}
              <div className="p-4 bg-gray-50 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <motion.div
                    className="text-sm text-gray-600"
                    animate={{ opacity: isPlaying ? 1 : 0.5 }}
                  >
                    {isPlaying ? '🎬 Demo in corso...' : '✨ Pronto per iniziare'}
                  </motion.div>

                  <div className="flex gap-2">
                    {!isPlaying && currentMessageIndex === 0 ? (
                      <motion.button
                        onClick={playDemo}
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Play className="w-4 h-4" />
                        Avvia Demo
                      </motion.button>
                    ) : (
                      <motion.button
                        onClick={resetDemo}
                        className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 transition-colors"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Play className="w-4 h-4" />
                        Riavvia
                      </motion.button>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Elements Around Demo */}
            <motion.div
              className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full flex items-center justify-center shadow-xl"
              animate={{
                y: [0, -10, 0],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <span className="text-3xl">⚡</span>
            </motion.div>

            <motion.div
              className="absolute -bottom-4 -left-4 w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-400 rounded-full flex items-center justify-center shadow-xl"
              animate={{
                y: [0, 10, 0],
                rotate: [0, -5, 5, 0]
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 0.5
              }}
            >
              <span className="text-2xl">✅</span>
            </motion.div>
          </motion.div>
        </div>

        {/* Bottom Stats */}
        <motion.div
          className="mt-20 grid grid-cols-3 gap-8 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1 }}
        >
          {[
            { value: '500+', label: 'Professionisti' },
            { value: '50k+', label: 'Prenotazioni/Mese' },
            { value: '99.9%', label: 'Uptime' }
          ].map((stat, index) => (
            <motion.div
              key={index}
              className="text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
              whileHover={{ scale: 1.1 }}
            >
              <div className="text-3xl font-bold text-blue-600 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="w-6 h-10 border-2 border-gray-300 rounded-full flex items-start justify-center p-2">
          <motion.div
            className="w-1.5 h-3 bg-gray-400 rounded-full"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </div>
      </motion.div>
    </section>
  );
}
