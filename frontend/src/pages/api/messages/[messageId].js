// frontend/src/pages/api/messages/[messageId].js
import { signedFetch } from "@/lib/signedFetch";

export default async function handler(req, res) {
  const { messageId } = req.query;

  if (req.method === 'DELETE') {
    return handleDelete(req, res, messageId);
  }

  if (req.method === 'PUT') {
    return handlePut(req, res, messageId);
  }

  res.setHeader('Allow', ['DELETE', 'PUT']);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}

async function handlePut(req, res, messageId) {
  try {
    const backendResponse = await signedFetch(`/messages/${messageId}`, req, {
      method: 'PUT',
      body: JSON.stringify(req.body),
    });

    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to update message' });
    }
    return res.status(200).json(data);
  } catch (err) {
    console.error(`Error updating message ${messageId}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}


async function handleDelete(req, res, messageId) {
  try {
    const backendResponse = await signedFetch(`/messages/${messageId}`, req, {
      method: 'DELETE',
    });

    if (!backendResponse.ok) {
      const data = await backendResponse.json().catch(() => ({})); // Handle cases where backend sends no body on error
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to delete message' });
    }
    
    // Check for 204 No Content, which won't have a body
    if (backendResponse.status === 204) {
        return res.status(204).end();
    }

    const data = await backendResponse.json();
    return res.status(200).json(data);

  } catch (err) {
    console.error(`Error deleting message ${messageId}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}
