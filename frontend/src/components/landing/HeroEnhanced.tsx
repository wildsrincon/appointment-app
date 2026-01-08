'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Calendar, CheckCircle2, Sparkles, MessageCircle, Clock, Zap } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function HeroEnhanced() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Floating animation variants
  const floatVariants = {
    animate: {
      y: [0, -20, 0],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  // Pulse animation for gradient orbs
  const pulseVariants = {
    animate: {
      scale: [1, 1.2, 1],
      opacity: [0.3, 0.5, 0.3],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  // Typing effect for subtitle
  const words = ['24/7', 'Intelligenti', 'Automatiche', 'Efficienti'];
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    const word = words[currentWordIndex];
    let currentIndex = 0;

    const typeInterval = setInterval(() => {
      if (currentIndex <= word.length) {
        setDisplayText(word.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(typeInterval);
        setTimeout(() => {
          setCurrentWordIndex((prev) => (prev + 1) % words.length);
        }, 2000);
      }
    }, 100);

    return () => clearInterval(typeInterval);
  }, [currentWordIndex]);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-white via-blue-50 to-white">
      {/* Interactive Background that follows mouse */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-100/30 via-purple-50/20 to-blue-50/30"
        animate={{
          backgroundPosition: `${mousePosition.x}% ${mousePosition.y}%`
        }}
        transition={{ type: "spring", damping: 30, stiffness: 100 }}
      />

      {/* Animated Grid Pattern */}
      <div className="absolute inset-0 bg-grid-blue-50/[0.4] [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]" />

      {/* Floating Elements */}
      <motion.div
        variants={floatVariants}
        animate="animate"
        className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-br from-blue-400/30 to-purple-400/30 rounded-full blur-3xl"
      />
      <motion.div
        variants={floatVariants}
        animate="animate"
        transition={{ delay: 1 }}
        className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"
      />
      <motion.div
        variants={pulseVariants}
        animate="animate"
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-br from-blue-300/20 to-purple-300/20 rounded-full blur-3xl"
      />

      {/* Floating Icons */}
      <motion.div
        animate={{
          y: [0, -15, 0],
          rotate: [0, 5, -5, 0]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-32 right-1/4 hidden lg:block"
      >
        <div className="w-16 h-16 bg-white rounded-2xl shadow-xl flex items-center justify-center">
          <Calendar className="w-8 h-8 text-blue-600" />
        </div>
      </motion.div>

      <motion.div
        animate={{
          y: [0, -15, 0],
          rotate: [0, -5, 5, 0]
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.5
        }}
        className="absolute bottom-32 left-1/4 hidden lg:block"
      >
        <div className="w-14 h-14 bg-white rounded-2xl shadow-xl flex items-center justify-center">
          <MessageCircle className="w-7 h-7 text-purple-600" />
        </div>
      </motion.div>

      <motion.div
        animate={{
          y: [0, -15, 0],
          rotate: [0, 5, -5, 0]
        }}
        transition={{
          duration: 4.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute top-1/3 left-20 hidden lg:block"
      >
        <div className="w-12 h-12 bg-white rounded-xl shadow-xl flex items-center justify-center">
          <Clock className="w-6 h-6 text-green-600" />
        </div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Animated Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-8"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-4 h-4 text-blue-600" />
            </motion.div>
            <span className="text-sm font-medium text-blue-900">AI-Powered Scheduling Platform</span>
          </motion.div>

          {/* Main Headline with Staggered Animation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
              <motion.span
                className="block text-gray-900"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                Prenotazioni
              </motion.span>
              <motion.span
                className="block text-blue-600 mt-2 relative inline-block"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                whileHover={{ scale: 1.05 }}
              >
                {displayText}
                <motion.span
                  className="inline-block w-1 h-12 bg-blue-600 ml-1"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                />
              </motion.span>
            </h1>
          </motion.div>

          {/* Subheadline */}
          <motion.p
            className="mt-6 text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            L'assistente AI che gestisce i tuoi appuntamenti{' '}
            <motion.span
              className="text-blue-600 font-semibold inline-block"
              whileHover={{ scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              24/7
            </motion.span>
            . Più tempo per te,
            <span className="text-blue-600 font-semibold"> zero perdite di clienti</span>.
          </motion.p>

          {/* CTA Buttons with Hover Effects */}
          <motion.div
            className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <Link href="/app">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onHoverStart={() => setIsHovered(true)}
                onHoverEnd={() => setIsHovered(false)}
              >
                <Button
                  size="lg"
                  className="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg shadow-xl shadow-blue-600/20 hover:shadow-2xl hover:shadow-blue-600/30 transition-all duration-300 rounded-full relative overflow-hidden"
                >
                  <motion.span
                    className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600"
                    animate={{
                      x: isHovered ? ['0%', '100%'] : '0%'
                    }}
                    transition={{ duration: 0.5 }}
                  />
                  <span className="relative flex items-center">
                    Inizia Gratis Ora
                    <motion.div
                      animate={{ x: isHovered ? 5 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </motion.div>
                  </span>
                </Button>
              </motion.div>
            </Link>

            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                size="lg"
                variant="outline"
                className="px-8 py-6 text-lg border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-300 rounded-full"
              >
                Guarda Demo
              </Button>
            </motion.div>
          </motion.div>

          {/* Trust Indicators with Staggered Animation */}
          <motion.div
            className="mt-16 flex flex-wrap justify-center items-center gap-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
          >
            {[
              { icon: CheckCircle2, text: 'Nessuna carta richiesta' },
              { icon: Calendar, text: 'Configurazione in 2 minuti' },
              { icon: Zap, text: 'AI multilingua' }
            ].map((item, index) => (
              <motion.div
                key={index}
                className="flex items-center gap-2 text-gray-600"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                <motion.div
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: index * 0.2 }}
                >
                  <item.icon className="w-5 h-5 text-blue-600 flex-shrink-0" />
                </motion.div>
                <span className="text-sm font-medium">{item.text}</span>
              </motion.div>
            ))}
          </motion.div>

          {/* Social Proof with Animated Stars */}
          <motion.div
            className="mt-16"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 1.4 }}
          >
            <p className="text-sm text-gray-500 mb-4">Più di 500+ professionisti usano ScheduleAI</p>
            <motion.div
              className="flex justify-center items-center gap-1"
              whileHover={{ scale: 1.05 }}
            >
              {[...Array(5)].map((_, i) => (
                <motion.svg
                  key={i}
                  className="w-5 h-5 text-yellow-400 fill-current"
                  viewBox="0 0 20 20"
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: 1.6 + i * 0.1 }}
                  whileHover={{ scale: 1.2, rotate: 5 }}
                >
                  <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                </motion.svg>
              ))}
            </motion.div>
            <motion.p
              className="text-sm text-gray-600 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 2.2 }}
            >
              <span className="font-semibold text-blue-600">4.9/5</span> basato su 200+ recensioni
            </motion.p>
          </motion.div>
        </div>
      </div>

      {/* Animated Scroll Indicator */}
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

      {/* Interactive Particle Effect on Mouse */}
      <motion.div
        className="fixed w-4 h-4 bg-blue-600 rounded-full pointer-events-none z-50 mix-blend-multiply"
        animate={{
          x: mousePosition.x * 10,
          y: mousePosition.y * 10,
          scale: [1, 1.5, 1],
          opacity: [0.3, 0.6, 0.3]
        }}
        transition={{
          type: "spring",
          damping: 30,
          stiffness: 200,
          opacity: { duration: 1, repeat: Infinity }
        }}
      />
    </section>
  );
}
