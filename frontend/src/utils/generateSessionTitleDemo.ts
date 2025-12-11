import { Message } from "@/utils/types";

// Constants for title generation
const TITLE_MAX_LENGTH = 50;
const TITLE_TRUNCATE_LENGTH = 47;
const DEFAULT_SESSION_TITLE = "Nuova Conversazione";

/**
 * Generates a session title from the first user message
 * @param messages - Array of messages in the chat session
 * @returns A formatted title for the session
 */
const generateSessionTitle = (messages: Message[]): string => {
  try {
    // Validate input
    if (!Array.isArray(messages) || messages.length === 0) {
      return DEFAULT_SESSION_TITLE;
    }

    // Find the first user message
    const userMessage = messages.find((m) => m.role === "user");

    // Return default title if no user message found
    if (!userMessage || !userMessage.content) {
      return DEFAULT_SESSION_TITLE;
    }

    // Clean and normalize the content
    const cleanContent = userMessage.content
      .trim()
      .replace(/\s+/g, " ") // Replace multiple whitespace with single space
      .replace(/[\r\n\t]/g, " "); // Replace newlines and tabs with spaces

    // Return content as is if it's within the length limit
    if (cleanContent.length <= TITLE_MAX_LENGTH) {
      return cleanContent;
    }

    // Truncate content and add ellipsis
    return cleanContent.substring(0, TITLE_TRUNCATE_LENGTH) + "...";
  } catch (error) {
    console.error("Error generating session title:", error);
    return DEFAULT_SESSION_TITLE;
  }
};

// Demo function to showcase the improvements
export const demonstrateGenerateSessionTitle = () => {
  // Helper function to create a test message
  const createMessage = (
    content: string,
    role: "user" | "assistant" | "system" = "user"
  ): Message => ({
    id: Math.random().toString(),
    content,
    role,
    timestamp: new Date(),
  });

  console.log("=== generateSessionTitle Function Demo ===\n");

  // Test case 1: Empty messages array
  console.log("1. Empty messages array:");
  console.log("Input: []");
  console.log("Output:", generateSessionTitle([]));
  console.log("Expected:", DEFAULT_SESSION_TITLE);
  console.log("");

  // Test case 2: No user message
  console.log("2. No user message:");
  console.log("Input: [assistant message, system message]");
  console.log(
    "Output:",
    generateSessionTitle([
      createMessage("Hello from assistant", "assistant"),
      createMessage("System message", "system"),
    ])
  );
  console.log("Expected:", DEFAULT_SESSION_TITLE);
  console.log("");

  // Test case 3: Short message (under limit)
  console.log("3. Short message (under limit):");
  const shortContent = "Short message";
  console.log("Input:", `"${shortContent}"`);
  console.log("Output:", generateSessionTitle([createMessage(shortContent)]));
  console.log("Expected:", shortContent);
  console.log("");

  // Test case 4: Long message (over limit)
  console.log("4. Long message (over limit):");
  const longContent =
    "This is a very long message that exceeds the fifty character limit for titles";
  console.log("Input:", `"${longContent}"`);
  console.log("Output:", generateSessionTitle([createMessage(longContent)]));
  console.log('Expected: "This is a very long message that exceeds the..."');
  console.log("");

  // Test case 5: Message with messy whitespace
  console.log("5. Message with messy whitespace:");
  const messyContent = "  Multiple   spaces\nand\ttabs  ";
  console.log("Input:", `"${messyContent}"`);
  console.log("Output:", generateSessionTitle([createMessage(messyContent)]));
  console.log('Expected: "Multiple spaces and tabs"');
  console.log("");

  // Test case 6: Empty content
  console.log("6. Empty content:");
  console.log("Input:", '""');
  console.log("Output:", generateSessionTitle([createMessage("")]));
  console.log("Expected:", DEFAULT_SESSION_TITLE);
  console.log("");

  console.log("=== Demo Complete ===");
};

// Export the function for use in other components
export { generateSessionTitle };
