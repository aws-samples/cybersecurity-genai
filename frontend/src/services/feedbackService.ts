// Mock feedback service to simulate API calls
export const feedbackService = {
  submitFeedback: async (messageId: string, feedback: 'positive' | 'negative'): Promise<boolean> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // In a real application, this would make an API call
    console.log(`Feedback submitted for message ${messageId}: ${feedback}`);
    
    // Simulate successful submission
    return true;
  }
};
