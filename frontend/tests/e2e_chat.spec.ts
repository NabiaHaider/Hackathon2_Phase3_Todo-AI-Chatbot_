import { test, expect } from '@playwright/test';

test.describe('E2E Chatbot Conversation Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto('/'); 
  });

  test('should display chat window, send message, and receive AI response', async ({ page }) => {
    // 1. Click the floating chat icon to open the chat window
    await page.locator('button[aria-label="Open chat"]').click();

    // 2. Expect the chat window modal to be visible
    const chatWindow = page.locator('[role="dialog"][aria-modal="true"]');
    await expect(chatWindow).toBeVisible();

    // 3. Type a message into the chat input
    const chatInput = chatWindow.locator('textarea[placeholder="Type your message..."]');
    await chatInput.fill('Hello AI Chatbot');

    // 4. Press Enter to send the message
    await chatInput.press('Enter');

    // 5. Expect the user's message to appear
    await expect(chatWindow.locator('.message-user:has-text("Hello AI Chatbot")')).toBeVisible();

    // 6. Expect an AI response (adjust selector as per actual component structure)
    // This assumes the AI response will have a specific class or data-testid for identification
    const aiResponse = chatWindow.locator('.message-ai');
    await expect(aiResponse).toBeVisible();
    await expect(aiResponse).not.toBeEmpty(); // Ensure it's not empty, indicating a response
    // Add more specific assertions if the AI's initial response is predictable, e.g.:
    // await expect(aiResponse).toContainText('Hello there! How can I help you?'); 
  });

  test('should ask for clarification when an ambiguous task command is given', async ({ page }) => {
    // 1. Click the floating chat icon to open the chat window
    await page.locator('button[aria-label="Open chat"]').click();

    // 2. Expect the chat window modal to be visible
    const chatWindow = page.locator('[role="dialog"][aria-modal="true"]');
    await expect(chatWindow).toBeVisible();

    // 3. Type an ambiguous command
    const chatInput = chatWindow.locator('textarea[placeholder="Type your message..."]');
    await chatInput.fill('Add task');

    // 4. Press Enter to send the message
    await chatInput.press('Enter');

    // 5. Expect the user's message to appear
    await expect(chatWindow.locator('.message-user:has-text("Add task")')).toBeVisible();

    // 6. Expect the AI to ask for clarification
    const aiClarification = chatWindow.locator('.message-ai');
    await expect(aiClarification).toBeVisible();
    await expect(aiClarification).toContainText('What is the title of the task?'); 
  });

  // Additional test scenarios could be added here:
  // - Test adding a task and verifying a confirmation message
  // - Test listing tasks
  // - Test error handling in chat
  // - Test multi-turn conversations and history persistence
});
