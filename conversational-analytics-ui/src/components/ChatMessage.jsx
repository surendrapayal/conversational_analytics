import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VegaChart from './VegaChart';
import ActivityPanel from './ActivityPanel';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'} ${message.error ? 'message-error' : ''}`}>
      <div className="message-avatar">{isUser ? '👤' : '🤖'}</div>
      <div className="message-body">
        {!isUser && <ActivityPanel activity={message.activity} live={!!message.loading} />}
        {message.loading ? (
          <div className="message-loading">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        ) : (
          <>
            <div className="message-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
            {message.vegaSpecs && <VegaChart vegaSpecs={message.vegaSpecs} responseText={message.content} />}
          </>
        )}
      </div>
    </div>
  );
}
