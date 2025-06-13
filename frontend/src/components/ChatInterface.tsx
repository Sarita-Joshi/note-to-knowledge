import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Upload, Send, MessageSquare, Trash2, RotateCcw, Loader2, Menu } from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import UploadModal from './UploadModal';
import UploadHistory, { UploadRecord } from './UploadHistory';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onDocumentUpload: (text: string) => void;
  onClearConversation: () => void;
  onResetAll: () => void;
  isLoading: boolean;
  uploadHistory: UploadRecord[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onDocumentUpload,
  onClearConversation,
  onResetAll,
  isLoading,
  uploadHistory
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Compact header */}
      <div className="p-3 border-b bg-muted/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            <h2 className="text-sm font-medium">Chat</h2>
          </div>
          
          {/* Desktop controls */}
          <div className="hidden sm:flex gap-1">
            <UploadHistory uploadHistory={uploadHistory} />
            <Button
              onClick={() => setShowUploadModal(true)}
              variant="ghost"
              size="sm"
              disabled={isLoading}
            >
              <Upload className="h-4 w-4" />
            </Button>
            <Button
              onClick={onClearConversation}
              variant="ghost"
              size="sm"
              disabled={isLoading}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
            <Button
              onClick={onResetAll}
              variant="ghost"
              size="sm"
              disabled={isLoading}
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>

          {/* Mobile menu */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="sm:hidden">
                <Menu className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-64">
              <div className="flex flex-col gap-3 mt-6">
                <UploadHistory uploadHistory={uploadHistory} />
                <Button
                  onClick={() => setShowUploadModal(true)}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                  className="w-full justify-start"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
                <Button
                  onClick={onClearConversation}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                  className="w-full justify-start"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear Chat
                </Button>
                <Button
                  onClick={onResetAll}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                  className="w-full justify-start"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset All
                </Button>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-3">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <div className="text-2xl mb-3">💬</div>
            <p className="text-sm font-medium mb-1">Start a conversation</p>
            <p className="text-xs">Ask questions about your graph.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-2 ${
                    message.isUser
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 opacity-70`}>
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-2 flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </ScrollArea>

      {/* Compact Input */}
      <div className="p-3 border-t bg-muted/30">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your graph..."
            disabled={isLoading}
            className="flex-1 text-sm h-9"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            size="icon"
            className="h-9 w-9"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={onDocumentUpload}
        isLoading={isLoading}
      />
    </div>
  );
};

export default ChatInterface;
