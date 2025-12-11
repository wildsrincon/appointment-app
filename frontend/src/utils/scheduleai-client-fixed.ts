import { AppointmentData } from "../utils/types";

export class ScheduleAIClientFixed {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl?: string, apiKey?: string) {
    this.baseUrl =
      baseUrl ||
      process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
      "http://localhost:8000";
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
    try {
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

      console.log(
        `📤 Sending message to ScheduleAI backend: ${backendUrl}/chat`
      );
      console.log(`📝 Message: ${message.substring(0, 50)}...`);
      console.log(`🔑 Session ID: ${sessionId}`);
      console.log(`🌐 Backend URL: ${backendUrl}`);

      // Prepare request body with correct field names
      const requestBody = {
        message: message,
        session_id: sessionId, // Backend expects session_id, not sessionId
        business_id: options?.businessId, // Backend expects business_id
        consultant_id: options?.consultantId, // Backend expects consultant_id
        stream: false, // Disable streaming for simpler debugging
      };

      console.log(`📦 Request body:`, requestBody);

      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add any required headers
          ...(this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
        },
        body: JSON.stringify(requestBody),
      });

      console.log(`📬 Response status: ${response.status}`);
      console.log(`📬 Response headers:`, response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ HTTP error: ${response.status} - ${errorText}`);

        // Try to parse error as JSON
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { error: errorText };
        }

        throw new Error(
          `HTTP ${response.status}: ${
            errorData.error || errorData.message || errorText
          }`
        );
      }

      // Get response as JSON
      const data = await response.json();
      console.log(`✅ Response data:`, data);

      // Handle different response formats from the backend
      let responseText = "";

      // Primary format: direct response field
      if (data.response) {
        responseText = data.response;

        // If response is an object with different properties
        if (typeof data.response === "object") {
          responseText =
            data.response.output ||
            data.response.data ||
            data.response.message ||
            JSON.stringify(data.response);
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
      }
      // Alternative formats
      else if (data.data && data.data.response) {
        responseText = data.data.response;
      } else if (data.message) {
        responseText = data.message;
      } else if (data.output) {
        responseText = data.output;
      }

      // Ensure we have a string response
      if (typeof responseText !== "string") {
        responseText = String(responseText || "");
      }

      console.log(`🎯 Final response: ${responseText.substring(0, 100)}...`);

      return responseText || "Risposta non disponibile.";
    } catch (error) {
      console.error("❌ ScheduleAI client error:", error);

      // Provide more detailed error information
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";

      // Check for common error patterns
      if (errorMessage.includes("fetch")) {
        return `Mi dispiace, non riesco a contattare il server. Assicurati che il backend ScheduleAI sia in esecuzione su http://localhost:8000`;
      } else if (errorMessage.includes("CORS")) {
        return `Mi dispiace, c'è un problema di connessione tra il frontend e il backend. Ricarica la pagina e riprova.`;
      } else if (errorMessage.includes("500")) {
        return `Mi dispiace, si è verificato un errore nel server. Riprova tra qualche momento.`;
      } else {
        return `Mi dispiace, si è verificato un errore: ${errorMessage}. Riprova più tardi.`;
      }
    }
  }

  async testConnection(): Promise<{
    success: boolean;
    message: string;
    backendUrl: string;
    data?: any;
  }> {
    // Test connection to the backend
    try {
      let backendUrl =
        this.baseUrl ||
        process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
        "http://localhost:8000";

      if (!backendUrl.startsWith("http")) {
        backendUrl = `http://${backendUrl}`;
      }
      backendUrl = backendUrl.replace(/\/$/, "");

      console.log(`🧪 Testing connection to: ${backendUrl}`);

      const response = await fetch(`${backendUrl}/test`, {
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
          backendUrl: backendUrl,
          data: data,
        };
      } else {
        return {
          success: false,
          message: `Server responded with ${response.status}`,
          backendUrl: backendUrl,
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
export const scheduleAIClientFixed = new ScheduleAIClientFixed();
