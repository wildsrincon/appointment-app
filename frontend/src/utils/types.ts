export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  appointment?: AppointmentData;
}

export interface AppointmentData {
  id?: string;
  clientName: string;
  serviceType: string;
  dateTime: string;
  duration: number;
  status: 'pending' | 'confirmed' | 'cancelled';
  notes?: string;
  meetingLink?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ScheduleAIResponse {
  message: string;
  appointment?: AppointmentData;
  suggestions?: string[];
  requiresAction?: boolean;
  actionType?: 'book_appointment' | 'reschedule' | 'cancel';
}

export interface User {
  id: string;
  name: string;
  email?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  language: 'it' | 'en';
  timezone: string;
  notifications: boolean;
}

export interface Consultant {
  id: string;
  name: string;
  services: string[];
  availability: {
    [key: string]: {
      start: string;
      end: string;
      available: boolean;
    }[];
  };
}

export interface Service {
  id: string;
  name: string;
  description: string;
  duration: number;
  price?: number;
  category: string;
}