// frontend/src/pages/api/vision_subgoals/index.js
import { signedFetch } from "@/lib/signedFetch";

export default async function handler(req, res) {
  if (req.method === 'GET') {
    return handleGet(req, res);
  }

  if (req.method === 'POST') {
    return handlePost(req, res);
  }

  res.setHeader('Allow', ['GET', 'POST']);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}

async function handleGet(req, res) {
  try {
    const backendResponse = await signedFetch("/vision_subgoals/", req);
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to fetch vision_subgoals' });
    }
    return res.status(200).json(data);
  } catch (err) {
    console.error("Error fetching vision_subgoals:", err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}

async function handlePost(req, res) {
  try {
    const backendResponse = await signedFetch("/vision_subgoals/", req, {
      method: 'POST',
      body: JSON.stringify(req.body),
    });
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return res.status(backendResponse.status).json({ error: data.detail || 'Failed to create vision_subgoal' });
    }
    return res.status(201).json(data);
  } catch (err) {
    console.error("Error creating vision_subgoal:", err);
    return res.status(500).json({ error: "Internal Server Error" });
  }
}