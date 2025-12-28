// frontend/src/pages/api/todo_lists/[todo_list_id].js
import { signedFetch } from "@/lib/signedFetch";

export default async function handler(req, res) {
  const { todo_list_id } = req.query;

  if (req.method === 'PUT') {
    return handlePut(req, res, todo_list_id);
  }

  if (req.method === 'DELETE') {
    return handleDelete(req, res, todo_list_id);
  }

  res.setHeader('Allow', ['PUT', 'DELETE']);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}

async function handlePut(req, res, todo_list_id) {
  try {
    const backendResponse = await signedFetch(`/todo_lists/${ todo_list_id }`, req, {
      method: 'PUT',
      body: JSON.stringify(req.body),
    });
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to update todo_list' });
    }
    return res.status(200).json(data);
  } catch (err) {
    console.error(`Error updating todo_list ${ todo_list_id }}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}

async function handleDelete(req, res, todo_list_id) {
  try {
    const backendResponse = await signedFetch(`/todo_lists/${ todo_list_id }`, req, {
      method: 'DELETE',
    });

    if (!backendResponse.ok) {
      const data = await backendResponse.json().catch(() => ({}));
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to delete todo_list' });
    }
    
    if (backendResponse.status === 204) {
        return res.status(204).end();
    }

    const data = await backendResponse.json();
    return res.status(200).json(data);

  } catch (err) {
    console.error(`Error deleting todo_list ${ todo_list_id }}:`, err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}