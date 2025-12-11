import { AppointmentData } from "./types";

export class ScheduleAIClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl?: string, apiKey?: string) {
    this.baseUrl =
      baseUrl || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    this.apiKey = apiKey || process.env.SCHEDULEAI_API_KEY;
  }

  async sendMessage(
    message: string,
    sessionId: string = "default",
    options?: {
      businessId?: string;
      consultantId?: string;
      onChunk?: (chunk: string) => void;
    }
  ): Promise<string> {
    // Use proper backend URL with fallbacks
    let backendUrl = this.baseUrl;

    // If no baseUrl, try environment variable, then fallback to localhost
    if (!backendUrl) {
      backendUrl =
        process.env.NEXT_PUBLIC_SCHEDULEAI_URL || "http://localhost:8000";
    }

    // Ensure the URL is properly formatted
    if (!backendUrl.startsWith("http")) {
      backendUrl = `http://${backendUrl}`;
    }

    // Remove trailing slash if present
    backendUrl = backendUrl.replace(/\/$/, "");

    try {
      console.log(
        `📤 Sending message to ScheduleAI backend: ${backendUrl}/chat`
      );
      console.log(`📝 Message: ${message.substring(0, 50)}...`);
      console.log(`🔑 Session ID: ${sessionId}`);
      console.log(`🌐 Backend URL: ${backendUrl}`);
      console.log(`🔗 Request body:`, {
        message,
        session_id: sessionId,
        business_id: options?.businessId,
        consultant_id: options?.consultantId,
        stream: false,
      });

      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          session_id: sessionId, // Backend expects session_id (snake_case)
          business_id: options?.businessId, // Backend expects business_id
          consultant_id: options?.consultantId, // Backend expects consultant_id
          stream: false, // Disable streaming for now to simplify
        }),
      });

      console.log(`📬 Response status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ HTTP error: ${response.status} - ${errorText}`);
        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      // Get response as JSON
      const data = await response.json();
      console.log(`✅ Response data:`, data);

      // Handle different response formats from the backend
      let responseText = "";

      if (data.response) {
        responseText = data.response;

        // If response is an object with output property
        if (typeof data.response === "object" && data.response.output) {
          responseText = data.response.output;
        }
        // If response is an object with data property
        else if (typeof data.response === "object" && data.response.data) {
          responseText =
            data.response.data.response || data.response.data.message || "";
        }
        // If response is a string
        else if (typeof responseText === "string") {
          // Try to extract content from AgentRunResult format if present
          if (responseText.includes("AgentRunResult(output=")) {
            const match = responseText.match(
              /AgentRunResult\(output="([^"]*(?:\\.[^"]*)*)"\)/
            );
            if (match && match[1]) {
              responseText = match[1]
                .replace(/\\"/g, '"')
                .replace(/\\n/g, "\n")
                .replace(/\\\\/g, "\\");
            }
          }
        }
      } else if (data.data && data.data.response) {
        // Alternative format: data.response
        responseText = data.data.response;
      } else if (data.message) {
        // Simple message format
        responseText = data.message;
      }

      // Ensure we have a string response
      if (typeof responseText !== "string") {
        responseText = String(responseText || "");
      }

      return responseText || "Risposta non disponibile.";
    } catch (error) {
      console.error("❌ ScheduleAI client error:", error);

      // Provide more specific error messages
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";

      if (
        errorMessage.includes("fetch") ||
        errorMessage.includes("Failed to fetch")
      ) {
        return `❌ Impossibile connettersi al server. Assicurati che il backend ScheduleAI sia in esecuzione su ${backendUrl}.`;
      } else if (errorMessage.includes("CORS")) {
        return `❌ Errore di sicurezza CORS. Il backend potrebbe non essere configurato correttamente.`;
      } else if (errorMessage.includes("HTTP 404")) {
        return `❌ Endpoint non trovato. Verifica che l'URL del backend sia corretta: ${backendUrl}`;
      } else if (errorMessage.includes("HTTP 500")) {
        return `❌ Errore interno del server. Il backend ha riscontrato un problema.`;
      } else if (errorMessage.includes("network")) {
        return `❌ Errore di rete. Controlla la tua connessione internet.`;
      } else {
        return `❌ Errore di comunicazione: ${errorMessage}. Riprova più tardi.`;
      }
    }
  }

  async testConnection(): Promise<{
    success: boolean;
    message: string;
    backendUrl: string;
    data?: unknown;
  }> {
    /**
     * Test connection to the backend
     */
    try {
      let testUrl = this.baseUrl;

      if (!testUrl) {
        testUrl =
          process.env.NEXT_PUBLIC_SCHEDULEAI_URL || "http://localhost:8000";
      }

      if (!testUrl.startsWith("http")) {
        testUrl = `http://${testUrl}`;
      }
      testUrl = testUrl.replace(/\/$/, "");

      console.log(`🧪 Testing connection to: ${testUrl}/health`);

      const response = await fetch(`${testUrl}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          message: "Connection successful",
          backendUrl: testUrl,
          data: data,
        };
      } else {
        return {
          success: false,
          message: `Server responded with ${response.status}`,
          backendUrl: testUrl,
        };
      }
    } catch (error) {
      console.error("❌ Connection test failed:", error);
      return {
        success: false,
        message: `Connection failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        backendUrl: this.baseUrl || "unknown",
      };
    }
  }

  async createAppointment(
    appointmentData: AppointmentData
  ): Promise<{ success: boolean; appointmentId?: string; error?: string }> {
    try {
      const response = await fetch("/api/appointments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(appointmentData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error:
            errorData.error || "Errore durante la creazione dell'appuntamento",
        };
      }

      const data = await response.json();
      return {
        success: true,
        appointmentId: data.appointmentId,
      };
    } catch (error) {
      console.error("Create appointment error:", error);
      return {
        success: false,
        error: "Errore di connessione al server",
      };
    }
  }

  async checkAvailability(
    date: string,
    serviceType: string,
    consultantId?: string
  ): Promise<string[]> {
    try {
      const params = new URLSearchParams({
        date,
        service: serviceType,
      });

      if (consultantId) {
        params.append("consultant", consultantId);
      }

      const response = await fetch(`/api/availability?${params}`);

      if (!response.ok) {
        return [];
      }

      const data = await response.json();
      return data.availableSlots || [];
    } catch (error) {
      console.error("Check availability error:", error);
      return [];
    }
  }

  async getServices(): Promise<
    Array<{ id: string; name: string; duration: number }>
  > {
    try {
      const response = await fetch("/api/services");

      if (!response.ok) {
        return [];
      }

      const data = await response.json();
      return data.services || [];
    } catch (error) {
      console.error("Get services error:", error);
      return [];
    }
  }

  async getConsultants(): Promise<
    Array<{ id: string; name: string; services: string[] }>
  > {
    try {
      const response = await fetch("/api/consultants");

      if (!response.ok) {
        return [];
      }

      const data = await response.json();
      return data.consultants || [];
    } catch (error) {
      console.error("Get consultants error:", error);
      return [];
    }
  }

  // Italian-specific helpers
  formatDateTime(date: Date): string {
    return new Intl.DateTimeFormat("it-IT", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Europe/Rome",
    }).format(date);
  }

  formatDate(date: Date): string {
    return new Intl.DateTimeFormat("it-IT", {
      weekday: "long",
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      timeZone: "Europe/Rome",
    }).format(date);
  }

  formatTime(date: Date): string {
    return new Intl.DateTimeFormat("it-IT", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Europe/Rome",
    }).format(date);
  }
}

// Create singleton instance
export const scheduleAIClient = new ScheduleAIClient();
