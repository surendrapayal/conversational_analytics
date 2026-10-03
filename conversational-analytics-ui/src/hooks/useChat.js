import { useState, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { streamQuery } from '../api/client';

export function useChat({ userId, role }) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [steps, setSteps] = useState([]);
  const sessionIdRef = useRef(uuidv4());

  const sendMessage = useCallback(async (query) => {
    const userMsg = { id: uuidv4(), role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setStreaming(true);
    setSteps([]);

    const assistantId = uuidv4();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '', vegaSpecs: null, loading: true }]);

    try {
      for await (const { event, data } of streamQuery({
        userId,
        query,
        sessionId: sessionIdRef.current,
        role,
      })) {
        if (event === 'step') {
          setSteps(prev => [...prev, data.message]);
        } else if (event === 'response') {
          // handle both vega_specs (array) and vega_spec (single object, backward compat)
          const vegaSpecs = data.vega_specs
            || (data.vega_spec ? [{ chart_type: 'Chart', spec: data.vega_spec }] : null);
          setMessages(prev => prev.map(m =>
            m.id === assistantId
              ? { ...m, content: data.text, vegaSpecs, loading: false }
              : m
          ));
        } else if (event === 'error') {
          setMessages(prev => prev.map(m =>
            m.id === assistantId
              ? { ...m, content: `Error: ${data.message}`, loading: false, error: true }
              : m
          ));
        }
      }
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === assistantId
          ? { ...m, content: `Error: ${err.message}`, loading: false, error: true }
          : m
      ));
    } finally {
      setStreaming(false);
      setSteps([]);
    }
  }, [userId, role]);

  const clearChat = useCallback(() => {
    setMessages([]);
    sessionIdRef.current = uuidv4();
  }, []);

  return { messages, streaming, steps, sendMessage, clearChat, sessionId: sessionIdRef.current };
}
