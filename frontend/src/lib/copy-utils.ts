import { useTelegram } from './telegram';

export const useCopyToClipboard = () => {
  const { hapticFeedback } = useTelegram();

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      
      hapticFeedback('success');
      return true;
    } catch (error) {
      console.error('Failed to copy text: ', error);
      hapticFeedback('error');
      return false;
    }
  };

  const extractCode = (text: string): string | null => {
    const codeMatch = text.match(/\b\d{4,6}\b/);
    return codeMatch ? codeMatch[0] : null;
  };

  return { copyToClipboard, extractCode };
};
