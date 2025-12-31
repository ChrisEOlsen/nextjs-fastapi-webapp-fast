import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Navbar from '../components/Navbar';
import { 
  FiFolder, FiFileText, FiTrash2, FiPlus, FiEdit2, 
  FiChevronRight, FiChevronDown, FiSave, FiFolderPlus, FiFilePlus,
  FiX, FiArrowLeft
} from 'react-icons/fi';
import { clsx } from 'clsx';

export default function Notes() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [selectedItem, setSelectedItem] = useState(null);
  const [view, setView] = useState('list'); // 'list' or 'editor' (mobile only)
  
  // Editor State
  const [editorTitle, setEditorTitle] = useState('');
  const [editorContent, setEditorContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // New Item State (Modal or Inline) - Using simple inline for now or prompt
  // actually let's just use buttons to add to current folder

  const API_ENDPOINT = `/api/note_items`;

  const fetchItems = async () => {
    try {
      const res = await fetch(API_ENDPOINT);
      if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
      const data = await res.json();
      setItems(data);
    } catch (err) {
      setError(`Could not load notes.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  // Update editor when selection changes
  useEffect(() => {
    if (selectedItem) {
      setEditorTitle(selectedItem.title);
      setEditorContent(selectedItem.content || '');
      setView('editor');
    } else {
      setEditorTitle('');
      setEditorContent('');
    }
  }, [selectedItem]);

  const handleCreate = async (isFolder, parentId = null) => {
    const defaultTitle = isFolder ? 'New Folder' : 'New Note';
    const tempTitle = prompt(`Enter name for ${defaultTitle}`, defaultTitle);
    if (!tempTitle) return;

    try {
      const res = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: tempTitle,
          content: '',
          is_folder: isFolder,
          parent_id: parentId
        }),
      });
      if (!res.ok) throw new Error('Failed to create item.');
      const createdItem = await res.json();
      setItems([...items, createdItem]);
      
      // Auto expand parent if exists
      if (parentId) {
        setExpandedFolders(prev => new Set(prev).add(parentId));
      }
      
      // Select if it's a file
      if (!isFolder) {
        setSelectedItem(createdItem);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (itemId) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    try {
      const res = await fetch(`${API_ENDPOINT}/${itemId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete item.');
      setItems(items.filter((item) => item.id !== itemId));
      if (selectedItem?.id === itemId) {
        setSelectedItem(null);
        setView('list');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleSave = async () => {
    if (!selectedItem) return;
    setIsSaving(true);
    try {
      const res = await fetch(`${API_ENDPOINT}/${selectedItem.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editorTitle,
          content: editorContent,
          is_folder: selectedItem.is_folder,
          parent_id: selectedItem.parent_id
        }),
      });
      if (!res.ok) throw new Error('Failed to update item.');
      const updatedItem = await res.json();
      
      setItems(items.map(i => i.id === updatedItem.id ? updatedItem : i));
      setSelectedItem(updatedItem);
    } catch (err) {
      alert(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  const toggleFolder = (id) => {
    const next = new Set(expandedFolders);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedFolders(next);
  };

  // Recursive Tree Component
  const FileTreeItem = ({ item, depth = 0 }) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedFolders.has(item.id);
    const isSelected = selectedItem?.id === item.id;

    return (
      <div className="select-none">
        <div 
          className={clsx(
            "flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-colors text-sm",
            isSelected ? "bg-indigo-500/20 text-indigo-300" : "hover:bg-zinc-800 text-zinc-400"
          )}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => {
            if (item.is_folder) {
                toggleFolder(item.id);
            } else {
                setSelectedItem(item);
            }
          }}
        >
          <span className="shrink-0 opacity-70">
            {item.is_folder ? (
              isExpanded ? <FiChevronDown /> : <FiChevronRight />
            ) : (
              <span className="w-4" /> // Spacer
            )}
          </span>
          
          <span className="shrink-0">
            {item.is_folder ? <FiFolder className="text-amber-500/80" /> : <FiFileText className="text-zinc-500" />}
          </span>
          
          <span className="truncate flex-1">{item.title}</span>

          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {item.is_folder && (
                <>
                 <button 
                    onClick={(e) => { e.stopPropagation(); handleCreate(false, item.id); }}
                    title="New Note"
                    className="p-1 hover:bg-zinc-700 rounded text-zinc-400 hover:text-green-400"
                >
                    <FiFilePlus size={14} />
                </button>
                <button 
                    onClick={(e) => { e.stopPropagation(); handleCreate(true, item.id); }}
                    title="New Folder"
                    className="p-1 hover:bg-zinc-700 rounded text-zinc-400 hover:text-amber-400"
                >
                    <FiFolderPlus size={14} />
                </button>
                </>
            )}
            <button 
                onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                title="Delete"
                className="p-1 hover:bg-zinc-700 rounded text-zinc-400 hover:text-red-400"
            >
                <FiTrash2 size={14} />
            </button>
          </div>
        </div>
        
        {item.is_folder && isExpanded && (
            <div>
                {item.children.length > 0 ? (
                     item.children.map(child => (
                        <FileTreeItem key={child.id} item={child} depth={depth + 1} />
                    ))
                ) : (
                    <div 
                        className="text-xs text-zinc-600 italic py-1"
                        style={{ paddingLeft: `${(depth + 1) * 12 + 28}px` }}
                    >
                        Empty folder
                    </div>
                )}
            </div>
        )}
      </div>
    );
  };

  // Build the tree structure
  const buildTree = (allItems) => {
    const itemMap = {};
    const roots = [];

    // Clone and map
    allItems.forEach(item => {
      itemMap[item.id] = { ...item, children: [] };
    });

    // Link children
    allItems.forEach(item => {
      if (item.parent_id && itemMap[item.parent_id]) {
        itemMap[item.parent_id].children.push(itemMap[item.id]);
      } else {
        roots.push(itemMap[item.id]);
      }
    });

    // Sort: Folders first, then alphabetical
    const sortFn = (a, b) => {
        if (a.is_folder === b.is_folder) return a.title.localeCompare(b.title);
        return a.is_folder ? -1 : 1;
    };
    
    // Recursive sort
    const sortTree = (nodes) => {
        nodes.sort(sortFn);
        nodes.forEach(node => {
            if (node.children) sortTree(node.children);
        });
        return nodes;
    };

    return sortTree(roots);
  };

  const treeData = buildTree(items);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200">
      <Head>
        <title>Notes | MCP App</title>
      </Head>
      
      <Navbar />

      <div className="flex pt-24 h-screen max-w-7xl mx-auto px-4 md:px-8 gap-6 pb-8">
        
        {/* Sidebar: File Explorer */}
        <div 
          className={clsx(
            "flex-col border border-zinc-800 bg-zinc-900/50 rounded-2xl overflow-hidden flex-shrink-0",
            "w-full md:w-80",
            view === 'list' ? 'flex' : 'hidden md:flex'
          )}
        >
          <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900">
            <h2 className="font-semibold text-zinc-100 flex items-center gap-2">
                <FiFolder className="text-indigo-500" /> Explorer
            </h2>
            <div className="flex gap-1">
                <button 
                    onClick={() => handleCreate(false)}
                    className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-400 hover:text-green-400 transition-colors"
                    title="New Note (Root)"
                >
                    <FiFilePlus />
                </button>
                <button 
                    onClick={() => handleCreate(true)}
                    className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-400 hover:text-amber-400 transition-colors"
                    title="New Folder (Root)"
                >
                    <FiFolderPlus />
                </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 custom-scrollbar group">
            {loading ? (
                <div className="text-center py-4 text-zinc-500">Loading...</div>
            ) : treeData.length === 0 ? (
                <div className="text-center py-8 text-zinc-600 text-sm px-4">
                    No files yet. Create one above.
                </div>
            ) : (
                treeData.map(node => (
                    <FileTreeItem key={node.id} item={node} />
                ))
            )}
          </div>
        </div>

        {/* Main Editor Area */}
        <div 
          className={clsx(
            "flex-1 flex-col border border-zinc-800 bg-zinc-900/30 rounded-2xl overflow-hidden relative",
            view === 'editor' ? 'flex' : 'hidden md:flex'
          )}
        >
            {selectedItem ? (
                <>
                     {/* Toolbar */}
                    <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50 backdrop-blur">
                        <div className="flex items-center gap-3 flex-1 overflow-hidden">
                            <button 
                                onClick={() => setView('list')}
                                className="md:hidden p-2 -ml-2 text-zinc-400 hover:text-white"
                            >
                                <FiArrowLeft />
                            </button>
                            <input 
                                type="text" 
                                value={editorTitle}
                                onChange={(e) => setEditorTitle(e.target.value)}
                                className="bg-transparent text-lg font-bold text-zinc-100 focus:outline-none placeholder-zinc-600 w-full"
                                placeholder="Note Title"
                            />
                        </div>
                        <button 
                            onClick={handleSave}
                            disabled={isSaving}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ml-2",
                                isSaving 
                                    ? "bg-zinc-800 text-zinc-500 cursor-wait" 
                                    : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
                            )}
                        >
                            <FiSave className={clsx(isSaving && "animate-spin")} />
                            <span className="hidden sm:inline">{isSaving ? 'Saving...' : 'Save'}</span>
                        </button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 p-0 overflow-hidden flex flex-col">
                        <textarea
                            value={editorContent}
                            onChange={(e) => setEditorContent(e.target.value)}
                            className="flex-1 w-full bg-transparent p-6 resize-none focus:outline-none text-zinc-300 font-mono text-sm leading-relaxed"
                            placeholder="Start typing..."
                        />
                    </div>
                    
                    {/* Status Bar */}
                    <div className="px-4 py-1.5 bg-zinc-950 border-t border-zinc-800 text-xs text-zinc-600 flex justify-between">
                        <span>ID: {selectedItem.id}</span>
                        <span>{selectedItem.is_folder ? 'Folder' : 'Markdown'}</span>
                    </div>
                </>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-zinc-600 p-8 text-center">
                    <button 
                        onClick={() => setView('list')}
                        className="md:hidden absolute top-4 left-4 p-2 text-zinc-400"
                    >
                        <FiArrowLeft size={24} />
                    </button>
                    <div className="w-16 h-16 bg-zinc-900 rounded-full flex items-center justify-center mb-4">
                        <FiFileText size={32} className="opacity-20" />
                    </div>
                    <p>Select a note to view or edit</p>
                </div>
            )}
        </div>

      </div>
    </div>
  );
}