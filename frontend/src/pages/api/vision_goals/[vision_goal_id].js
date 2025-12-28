// frontend/src/pages/api/vision_goals/[vision_goal_id].js
import { signedFetch } from "@/lib/signedFetch";

export default async function handler(req, res) {
  const { vision_goal_id } = req.query;

  if (req.method === 'PUT') {
    return handlePut(req, res, vision_goal_id);
  }

  if (req.method === 'DELETE') {
    return handleDelete(req, res, vision_goal_id);
  }

  res.setHeader('Allow', ['PUT', 'DELETE']);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}

async function handlePut(req, res, vision_goal_id) {
  try {
    const backendResponse = await signedFetch(`/vision_goals/${ vision_goal_id }`, req, {
      method: 'PUT',
      body: JSON.stringify(req.body),
    });
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to update vision_goal' });
    }
    return res.status(200).json(data);
  } catch (err) {
    console.error(`Error updating vision_goal ${ vision_goal_id }}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}

async function handleDelete(req, res, vision_goal_id) {
  try {
    const backendResponse = await signedFetch(`/vision_goals/${ vision_goal_id }`, req, {
      method: 'DELETE',
    });

    if (!backendResponse.ok) {
      const data = await backendResponse.json().catch(() => ({}));
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to delete vision_goal' });
    }
    
    if (backendResponse.status === 204) {
        return res.status(204).end();
    }

    const data = await backendResponse.json();
    return res.status(200).json(data);

  } catch (err) {
    console.error(`Error deleting vision_goal ${ vision_goal_id }}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}