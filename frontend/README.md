# ScheduleAI Frontend

Interfaccia di chat tipo ChatGPT per l'assistente di prenotazioni ScheduleAI basato su Pydantic AI.

## 🚀 Quick Start

1. **Installa le dipendenze**
   ```bash
   npm install
   ```

2. **Configura le variabili d'ambiente**
   ```bash
   cp .env.local.example .env.local
   ```
   Modifica `.env.local` con le tue configurazioni:
   ```env
   NEXT_PUBLIC_SCHEDULEAI_URL=http://localhost:8000
   SCHEDULEAI_API_KEY=your-api-key-here
   ```

3. **Avvia il frontend**
   ```bash
   npm run dev
   ```

4. **Apri il browser**
   Vai su [http://localhost:3000](http://localhost:3000)

## 🏗️ Architettura

### Tecnologie Utilizzate
- **Next.js 15** con App Router
- **TypeScript** per type safety
- **Tailwind CSS** per styling
- **shadcn/ui** per componenti UI
- **Lucide React** per icone
- **date-fns** per formattazione date italiane

### Struttura del Progetto

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat/           # API routes per ScheduleAI
│   │   ├── globals.css        # Stili globali
│   │   ├── layout.tsx         # Layout principale
│   │   └── page.tsx           # Pagina principale chat
│   ├── components/
│   │   ├── chat/              # Componenti chat
│   │   │   └── ChatInterface.tsx
│   │   ├── layout/            # Componenti layout
│   │   │   └── Sidebar.tsx
│   │   └── ui/                # Componenti shadcn/ui
│   └── lib/
│       ├── scheduleai-client.ts  # Client per ScheduleAI
│       ├── types.ts              # Tipi TypeScript
│       └── utils.ts              # Utilità varie
```

## 🎨 Caratteristiche dell'Interfaccia

### ChatGPT-like Design
- **Sidebar** con conversazioni precedenti
- **Area chat** con messaggi user/assistant
- **Input area** con textarea multi-linea
- **Streaming responses** per esperienze real-time
- **Typing indicators** durante elaborazione

### Localizzazione Italiana
- **Lingua**: Completamente in italiano
- **Date**: Formato DD/MM/YYYY europeo
- **Ora**: formato 24 ore con timezone Europe/Rome
- **Colori**: Tema ispirato ai colori italiani (blu, verde, rosso)

### Funzionalità Principali
- ✅ **Chat in tempo reale** con streaming
- ✅ **Storia conversazioni** persistente in localStorage
- ✅ **Multiple chat sessions**
- ✅ **Responsive design** per mobile/tablet/desktop
- ✅ **Integration with ScheduleAI backend**
- ✅ **Appointment booking interface**
- ✅ **Error handling** e loading states

## 🔌 Integrazione ScheduleAI

Il frontend si integra con il backend ScheduleAI attraverso:

### API Routes
- `/api/chat` - Comunica con ScheduleAI per messaggi
- `/api/appointments` - Gestisce prenotazioni (TODO)
- `/api/availability` - Verifica disponibilità (TODO)
- `/api/services` - Lista servizi disponibili (TODO)

### ScheduleAI Client
```typescript
import { scheduleAIClient } from '@/lib/scheduleai-client';

// Invia messaggio con streaming
const response = await scheduleAIClient.sendMessage(
  "Vorrei prenotare un appuntamento",
  sessionId,
  {
    onChunk: (chunk) => console.log('Streaming:', chunk)
  }
);
```

## 📱 Responsive Design

### Mobile (<640px)
- **Full-width chat** senza sidebar permanente
- **Slide-out menu** per conversazioni
- **Touch-optimized** controls e input
- **Bottom sheet** per navigazione

### Tablet (641px-1024px)
- **Collapsible sidebar** a 320px
- **Adaptive layout** per orientamento
- **Touch gestures** support

### Desktop (>1025px)
- **Fixed sidebar** a 320px
- **Keyboard shortcuts** (Enter per inviare)
- **Hover states** e tooltips
- **Multi-window** support

## 🚀 Deployment

### Vercel (Raccomandato)
1. Connect repository GitHub a Vercel
2. Imposta variabili d'ambiente in Vercel
3. Automatic deployment su push

### Docker
```bash
# Build
docker build -t scheduleai-frontend .

# Run
docker run -p 3000:3000 scheduleai-frontend
```

### Manual Build
```bash
npm run build
npm start
```

## 🔧 Sviluppo

### Environment Variables
```env
# ScheduleAI Backend
NEXT_PUBLIC_SCHEDULEAI_URL=http://localhost:8000
SCHEDULEAI_API_KEY=your-api-key

# Optional IDs
NEXT_PUBLIC_BUSINESS_ID=biz-123
NEXT_PUBLIC_CONSULTANT_ID=cons-456
```

### Development Commands
```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## 🧪 Testing

### Component Testing
```bash
# TODO: Add testing setup
npm run test
```

### Integration Testing
```bash
# TODO: Add E2E testing
npm run test:e2e
```

## 🤝 Contributing

1. Fork il repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri Pull Request

## 📄 Licenza

MIT License - vedi file [LICENSE](LICENSE) per dettagli.

## 🆘 Supporto

Per problemi o domande:
- **GitHub Issues**: [Issues tracker](https://github.com/your-repo/issues)
- **Discord**: [ScheduleAI Community](https://discord.gg/scheduleai)
- **Email**: support@scheduleai.it
