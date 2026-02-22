// ==================== Messages Auto-Hide ==================== 

document.addEventListener('DOMContentLoaded', function() {
  const messagesContainer = document.getElementById('messagesContainer');
  
  if (!messagesContainer) return;

  const messages = messagesContainer.querySelectorAll('.message-toast');

  messages.forEach((message) => {
    // // Auto-hide after 5 seconds
    // const timeout = setTimeout(() => {
    //   message.classList.add('hiding');
      
    //   // Remove from DOM after animation completes
    //   setTimeout(() => {
    //     message.remove();
    //   }, 300); // Match slideOutRight animation duration
    // }, 5000); // 5 seconds

    // Allow manual close to clear the timeout
    const closeBtn = message.querySelector('.message-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(timeout);
      });
    }

    // Remove container if empty
    const observer = new MutationObserver(() => {
      if (messagesContainer.querySelectorAll('.message-toast').length === 0) {
        messagesContainer.remove();
      }
    });

    observer.observe(messagesContainer, { childList: true });
  });
});
