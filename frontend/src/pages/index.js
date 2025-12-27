import { useState, useEffect } from 'react';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  
  // State for editing
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editingText, setEditingText] = useState('');

  // Fetch messages from the backend
  const fetchMessages = async () => {
    try {
      const res = await fetch('/api/messages');
      if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
      const data = await res.json();
      setMessages(data);
    } catch (err) {
      setError('Could not load messages.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  // Handle form submission to create a new message
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newMessage }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to post message.');
      }
      const createdMessage = await res.json();
      setMessages([...messages, createdMessage]);
      setNewMessage('');
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  // Handle message deletion
  const handleDelete = async (messageId) => {
    try {
      const res = await fetch(`/api/messages/${messageId}`, { method: 'DELETE' });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to delete message.');
      }
      setMessages(messages.filter((msg) => msg.id !== messageId));
      setError('');
    } catch (err) {
       setError(err.message);
    }
  };
  
  // Handle starting an edit
  const startEditing = (message) => {
    setEditingMessageId(message.id);
    setEditingText(message.content);
  };
  
  // Handle canceling an edit
  const cancelEditing = () => {
    setEditingMessageId(null);
    setEditingText('');
  };

  // Handle submitting an edit
  const handleUpdate = async (messageId) => {
    if (!editingText.trim()) return;

    try {
      const res = await fetch(`/api/messages/${messageId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: editingText }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to update message.');
      }
      const updatedMessage = await res.json();
      setMessages(messages.map((msg) => (msg.id === messageId ? updatedMessage : msg)));
      cancelEditing();
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center pt-10">
      <main className="w-full max-w-2xl px-4">
        <h1 className="text-4xl font-bold mb-8 text-center">Message Board</h1>

        {error && <p className="bg-red-500 text-white p-3 rounded-md mb-4 text-center">{error}</p>}

        <form onSubmit={handleCreate} className="mb-8 flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Write a new message..."
            className="flex-grow bg-gray-800 border border-gray-700 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md">Post</button>
        </form>

        <div className="space-y-4">
          {loading ? <p className="text-center">Loading messages...</p> : 
           messages.length > 0 ? (
            messages.map((msg) => (
              <div key={msg.id} className="bg-gray-800 p-4 rounded-lg flex justify-between items-center">
                {editingMessageId === msg.id ? (
                  <input
                    type="text"
                    value={editingText}
                    onChange={(e) => setEditingText(e.target.value)}
                    className="flex-grow bg-gray-700 border border-gray-600 rounded-md py-1 px-3"
                  />
                ) : (
                  <p>{msg.content}</p>
                )}
                <div className="flex gap-2 ml-4">
                  {editingMessageId === msg.id ? (
                    <>
                      <button onClick={() => handleUpdate(msg.id)} className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded-md">Save</button>
                      <button onClick={cancelEditing} className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-1 px-3 rounded-md">Cancel</button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => startEditing(msg)} className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-1 px-3 rounded-md">Edit</button>
                      <button onClick={() => handleDelete(msg.id)} className="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded-md">Delete</button>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-500">No messages yet. Be the first to post!</p>
          )}
        </div>
      </main>
    </div>
  );
}