export interface Notebook {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  icon: string;
  is_default: boolean;
  note_count: number;
  created_at: string;
}

export interface NotebookCreate {
  name: string;
  description?: string;
  icon?: string;
}

export interface NotebookUpdate {
  name?: string;
  description?: string;
  icon?: string;
}

export interface Note {
  id: number;
  user_id: number;
  notebook_id?: number;
  learning_path_id?: number;
  title?: string;
  content: string;
  tags: string[];
  editor_mode: 'markdown' | 'rich_text';
  created_at: string;
  updated_at?: string;
}

export interface NoteCreate {
  notebook_id?: number;
  learning_path_id?: number;
  title?: string;
  content: string;
  tags?: string[];
  editor_mode?: 'markdown' | 'rich_text';
}

export interface NoteUpdate {
  notebook_id?: number;
  title?: string;
  content?: string;
  tags?: string[];
  editor_mode?: 'markdown' | 'rich_text';
}

